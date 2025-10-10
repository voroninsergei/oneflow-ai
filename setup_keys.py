"""
Script to create/edit API keys config file outside repository.
RECOMMENDED: Use environment variables instead (OPENAI_API_KEY, ANTHROPIC_API_KEY)
"""
import json
import os
import sys
import stat
from pathlib import Path

# Store keys outside repository
CONFIG_DIR = Path.home() / ".config" / "your_project_name"
TARGET = CONFIG_DIR / "api_keys.json"
SCHEMA = {
    "openai": {"api_key": ""},
    "anthropic": {"api_key": ""}
}

def validate_schema(data):
    """Validate JSON structure"""
    if not isinstance(data, dict):
        return False
    for provider in ["openai", "anthropic"]:
        if provider not in data or not isinstance(data[provider], dict):
            return False
        if "api_key" not in data[provider]:
            return False
    return True

def secure_file_permissions(filepath):
    """Set file permissions to 600 (read/write for owner only)"""
    try:
        os.chmod(filepath, stat.S_IRUSR | stat.S_IWUSR)
        return True
    except Exception as e:
        print(f"Warning: Could not set secure permissions: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("API Keys Setup")
    print("="*70)
    print("\n⚠️  SECURITY RECOMMENDATIONS:")
    print("1. Use environment variables instead (OPENAI_API_KEY, ANTHROPIC_API_KEY)")
    print("2. This script stores keys OUTSIDE your repository")
    print("3. Never commit API keys to git")
    print("="*70 + "\n")
    
    response = input("Continue with file-based config? (y/N): ").strip().lower()
    if response != 'y':
        print("\nRecommended setup:")
        print("  export OPENAI_API_KEY='sk-...'")
        print("  export ANTHROPIC_API_KEY='sk-ant-...'")
        sys.exit(0)
    
    # Create config directory
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    if TARGET.exists():
        print(f"\n✓ Config exists at: {TARGET}")
        
        # Validate existing file
        try:
            with open(TARGET, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not validate_schema(data):
                print("⚠️  Invalid schema detected. Backing up and recreating...")
                backup = TARGET.with_suffix(".json.bak")
                TARGET.rename(backup)
                print(f"Backup saved to: {backup}")
            else:
                # Check permissions
                mode = TARGET.stat().st_mode
                if mode & (stat.S_IRWXG | stat.S_IRWXO):
                    print("⚠️  Insecure permissions detected. Fixing...")
                    secure_file_permissions(TARGET)
                
                print("\nCurrent configuration:")
                for provider, config in data.items():
                    key = config.get("api_key", "")
                    masked = key[:7] + "..." + key[-4:] if len(key) > 11 else "[empty]"
                    print(f"  {provider}: {masked}")
                
                edit = input("\nEdit keys? (y/N): ").strip().lower()
                if edit != 'y':
                    sys.exit(0)
        except json.JSONDecodeError:
            print("⚠️  Corrupted JSON file. Recreating...")
        except Exception as e:
            print(f"⚠️  Error reading file: {e}")
    
    # Create or update file
    print(f"\nCreating config at: {TARGET}")
    
    keys = {}
    for provider in ["openai", "anthropic"]:
        key = input(f"Enter {provider.upper()} API key (or press Enter to skip): ").strip()
        keys[provider] = {"api_key": key}
    
    with open(TARGET, "w", encoding="utf-8") as f:
        json.dump(keys, f, indent=2)
    
    # Set secure permissions
    if secure_file_permissions(TARGET):
        print(f"\n✓ File created with secure permissions (600)")
    
    print(f"\n✓ API keys saved to: {TARGET}")
    print("\n⚠️  REMINDER: Never commit this file to git!")
    print(f"   Add to .gitignore: {TARGET.name}")
    print("\nTo use these keys in your code:")
    print(f"   config_path = Path.home() / '.config' / 'your_project_name' / 'api_keys.json'")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
