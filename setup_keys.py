"""
Script to create/edit .api_keys.json from .api_keys.example.json
"""
import json, os, shutil

EXAMPLE = ".api_keys.example.json"
TARGET = ".api_keys.json"

def main():
    if not os.path.exists(EXAMPLE):
        print(f"Missing {EXAMPLE}, creating a blank example...")
        with open(EXAMPLE, "w", encoding="utf-8") as f:
            json.dump({"openai": {"api_key": ""}, "anthropic": {"api_key": ""}}, f, indent=2)
    if not os.path.exists(TARGET):
        shutil.copyfile(EXAMPLE, TARGET)
        print(f"Created {TARGET} from {EXAMPLE}. Fill in your keys.")
    else:
        print(f"{TARGET} already exists.")

if __name__ == "__main__":
    main()
