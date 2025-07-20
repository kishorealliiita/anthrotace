import unittest
from anthrotrace.core.yaml_prompt_loader import load_prompts_with_categories
import tempfile
import yaml
import os

class TestYamlPromptLoader(unittest.TestCase):
    def setUp(self):
        self.test_yaml = {
            'Category1': ['Prompt 1', 'Prompt 2'],
            'Category2': ['Prompt 3']
        }
        self.tempfile = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.yaml')
        yaml.dump(self.test_yaml, self.tempfile)
        self.tempfile.close()

    def tearDown(self):
        os.unlink(self.tempfile.name)

    def test_load_prompts_with_categories(self):
        prompts = load_prompts_with_categories(self.tempfile.name)
        self.assertEqual(len(prompts), 3)
        categories = set(p['category'] for p in prompts)
        self.assertEqual(categories, {'Category1', 'Category2'})
        prompt_texts = set(p['prompt_text'] for p in prompts)
        self.assertEqual(prompt_texts, {'Prompt 1', 'Prompt 2', 'Prompt 3'})

if __name__ == '__main__':
    unittest.main() 