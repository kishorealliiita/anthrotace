import unittest
from anthrotrace.core.cost_calculator import calculate_cost, make_cost_calculator

class TestCostCalculator(unittest.TestCase):
    def test_calculate_cost(self):
        context = {
            'model': 'claude-sonnet-4-20250514',
            'input_tokens': 1000,
            'output_tokens': 2000
        }
        cost = calculate_cost(context)
        expected = (1000/1_000_000)*3.00 + (2000/1_000_000)*15.00
        self.assertAlmostEqual(cost, expected)

    def test_calculate_cost_unknown_model(self):
        context = {
            'model': 'unknown-model',
            'input_tokens': 1000,
            'output_tokens': 2000
        }
        with self.assertRaises(ValueError):
            calculate_cost(context)

    def test_calculate_cost_zero_tokens(self):
        context = {
            'model': 'claude-sonnet-4-20250514',
            'input_tokens': 0,
            'output_tokens': 0
        }
        cost = calculate_cost(context)
        self.assertEqual(cost, 0.0)

    def test_make_cost_calculator(self):
        my_pricing = {
            'my-model': {'input': 2.0, 'output': 4.0}
        }
        my_cost_fn = make_cost_calculator(my_pricing)
        context = {
            'model': 'my-model',
            'input_tokens': 1000,
            'output_tokens': 2000
        }
        expected = (1000/1_000_000)*2.0 + (2000/1_000_000)*4.0
        self.assertAlmostEqual(my_cost_fn(context), expected)

if __name__ == '__main__':
    unittest.main() 