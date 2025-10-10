"""
Quick project setup: installs deps, seeds config and api keys.
"""
import subprocess, sys, os

def sh(cmd):
    print("+", cmd)
    r = subprocess.call(cmd, shell=True)
    if r != 0:
        sys.exit(r)

def main():
    if not os.path.exists(".api_keys.example.json"):
        open(".api_keys.example.json","w").write('{"openai":{"api_key":""},"anthropic":{"api_key":""}}')
    if not os.path.exists("config.example.json"):
        open("config.example.json","w").write('{"region":"us-east","pricing":{}}')
    sh(f"{sys.executable} -m pip install -r requirements.txt")
    sh(f"{sys.executable} -m pip install -e .")
    print("Quick setup complete. Edit .api_keys.json using: python setup_keys.py")

if __name__ == "__main__":
    main()
