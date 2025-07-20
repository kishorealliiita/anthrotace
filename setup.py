from setuptools import setup, find_packages

setup(
    name="anthrotrace",
    version="0.1.0",
    description="Benchmarking and analytics suite for LLM prompts and responses.",
    author="Kishore Korathaluri",
    packages=find_packages(),
    install_requires=[
        "anthropic",
        "streamlit",
        "pandas",
        "python-dateutil",
        "prometheus_client",
        "clickhouse-connect",
        # Add any other dependencies here
    ],
    python_requires=">=3.8",
    include_package_data=True,
) 