"""
Quick project setup: installs deps, provides guidance on API keys.
"""
import subprocess
import sys
import os

def sh(cmd):
    print("+", cmd)
    r = subprocess.call(cmd, shell=True)
    if r != 0:
        sys.exit(r)

def main():
    # Create example config without API keys
    if not os.path.exists("config.example.json"):
        with open("config.example.json", "w", encoding="utf-8") as f:
            f.write('{"region":"us-east","pricing":{}}')
    
    # Install dependencies
    sh(f"{sys.executable} -m pip install -r requirements.txt")
    sh(f"{sys.executable} -m pip install -e .")
    
    print("\n" + "="*70)
    print("Quick setup complete!")
    print("="*70)
    print("\nAPI Key Configuration (choose one method):")
    print("\n1. RECOMMENDED: Use environment variables")
    print("   export OPENAI_API_KEY='your-key-here'")
    print("   export ANTHROPIC_API_KEY='your-key-here'")
    print("\n2. Alternative: Use secure config file")
    print("   python setup_keys.py")
    print("\nSee README.md for detailed instructions.")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
