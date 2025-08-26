import os
import json
import yaml
from datetime import date
from openai import OpenAI
from pacapicks import config
from ai.schemas import Picks

PROMPT_PATH = os.path.join(os.path.dirname(__file__), 'prompts.yaml')

client = OpenAI(api_key=config.OPENAI_API_KEY)


def load_prompt(key):
    with open(PROMPT_PATH, 'r') as f:
        prompts = yaml.safe_load(f)
    return prompts[key]['description']

def test_research_prompt():
    prompt = load_prompt('stock_opportunities')

    prompt = prompt.format(
        current_date=date.today().strftime("%Y-%m-%d"),
    )

    # Append the expected output schema to the prompt
    schema = Picks.model_json_schema()
    prompt += "\n\nEXPECTED OUTPUT SCHEMA (JSON):\n" + json.dumps(schema, indent=2)

    response = client.responses.create(
        model="gpt-4o",
        input=[{"role": "user", "content": prompt}],
        tools=[{"type": "web_search"}],
        response_format="json",
        max_output_tokens=1200,
    )

    # Parse the response into Picks
    output_json = response.output  # or response.choices[0].message.content if using completions
    picks: Picks = Picks.model_validate_json(output_json)

    print("Validated Picks object:", picks)
    print("First ticker:", picks[0].ticker)

    # Save output to JSON file
    with open('research_output.json', 'w') as f:
        json.dump([pick.model_dump() for pick in picks], f, indent=2)

    # You can still access usage & cost
    usage = response.usage
    print("Token usage:", usage)
    if usage:
        input_cost = usage.prompt_tokens * 0.000005  # $5 / 1M tokens
        output_cost = usage.completion_tokens * 0.000015  # $15 / 1M tokens
        print(f"Estimated cost: ${input_cost + output_cost:.4f}")
    
    return picks

def test_hello_world():
	response = client.chat.completions.create(
		model="gpt-4o-mini",
		messages=[{"role": "user", "content": "hello world"}]
	)
	print(response.choices[0].message.content)

if __name__ == "__main__":
	test_hello_world()
