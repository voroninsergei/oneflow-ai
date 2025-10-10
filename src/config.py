"""Config loader (placeholder)."""
import json, os
def load_config(path="config.json", default="config.example.json"):
    p = path if os.path.exists(path) else default
    if os.path.exists(p):
        return json.load(open(p,"r"))
    return {}
