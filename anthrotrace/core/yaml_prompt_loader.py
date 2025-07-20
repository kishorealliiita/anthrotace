# app/yaml_prompt_loader.py

import yaml

def load_prompts_with_categories(yaml_file):
    with open(yaml_file, "r") as f:
        data = yaml.safe_load(f)

    prompts = []
    for category, items in data.items():
        for prompt in items:
            prompts.append({
                "category": category,
                "prompt_text": prompt
            })
    return prompts
