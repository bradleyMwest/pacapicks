from setuptools import setup, find_packages

setup(
    name="pacapicks",
    version="0.1.0",
    packages=find_packages(where="pacapicks"),
    package_dir={"": "pacapicks"},
    install_requires=[],  # You can add dependencies here or use requirements.txt
    include_package_data=True,
    description="Alpaca trading and analysis tools",
    author="bradleyMwest",
    python_requires=">=3.12",
)
