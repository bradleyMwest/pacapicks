def shares_for_pct(portfolio_value, price, pct):
    target_value = portfolio_value * (pct / 100)
    return max(1, int(target_value // price))


def guardrails(order, max_pos_pct, existing_pos_pct):
    # e.g., block if would exceed max position size or too illiquid
    return existing_pos_pct + order["target_pct"] <= max_pos_pct
