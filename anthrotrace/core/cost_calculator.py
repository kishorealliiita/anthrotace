# Anthropic Pricing (as of July 2025)
PRICING = {
    "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
    "claude-3-sonnet-20240229": {"input": 3.00, "output": 15.00},
    "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    "claude-opus-4-20250514": {"input": 15.00, "output": 75.00},
    "claude-haiku-4-20250514": {"input": 0.25, "output": 1.25},
}

def calculate_cost(context: dict) -> float:
    """
    Calculate cost using the default Anthropic pricing table.
    Expects context dict with keys: 'model', 'input_tokens', 'output_tokens'.
    """
    model = context.get('model', '').lower()
    input_tokens = context.get('input_tokens', 0)
    output_tokens = context.get('output_tokens', 0)
    if model not in PRICING:
        raise ValueError(f"Pricing for model '{model}' not found.")
    pricing = PRICING[model]
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return input_cost + output_cost

def make_cost_calculator(pricing_dict):
    """
    Returns a cost calculator function using a custom pricing dictionary.
    Usage:
        my_pricing = { ... }
        my_cost_fn = make_cost_calculator(my_pricing)
        runner = AnthropicBenchmarkWithSQLite(api_key, cost_calculator=my_cost_fn)
    The returned function expects a context dict with keys: 'model', 'input_tokens', 'output_tokens'.
    """
    def custom_cost(context: dict) -> float:
        model = context.get('model', '').lower()
        input_tokens = context.get('input_tokens', 0)
        output_tokens = context.get('output_tokens', 0)
        if model not in pricing_dict:
            raise ValueError(f"Pricing for model '{model}' not found.")
        pricing = pricing_dict[model]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost
    return custom_cost
