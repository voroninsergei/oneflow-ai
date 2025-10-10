"""API keys manager (placeholder)."""
import json, os
def load_keys(path=".api_keys.json", example=".api_keys.example.json"):
    if not os.path.exists(path) and os.path.exists(example):
        return json.load(open(example,"r"))
    if os.path.exists(path):
        return json.load(open(path,"r"))
    return {"openai":{"api_key":""},"anthropic":{"api_key":""}}
