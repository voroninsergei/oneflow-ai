"""
Setup script for configuring API keys.
Скрипт настройки API ключей.

Run this script to configure your API keys for OneFlow.AI.
Запустите этот скрипт для настройки API ключей OneFlow.AI.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from api_keys import APIKeyManager


def setup_api_keys():
    """
    Interactive setup for API keys.
    Интерактивная настройка API ключей.
    """
    print("=" * 70)
    print("OneFlow.AI API Keys Setup | Настройка API ключей OneFlow.AI")
    print("=" * 70)
    print()
    print("This script will help you configure API keys for AI providers.")
    print("Этот скрипт поможет настроить API ключи для AI провайдеров.")
    print()
    print("⚠ IMPORTANT | ВАЖНО:")
    print("  - API keys are stored in .api_keys.json")
    print("  - Make sure .api_keys.json is in your .gitignore")
    print("  - Never commit API keys to version control")
    print()
    print("  - API ключи сохраняются в .api_keys.json")
    print("  - Убедитесь, что .api_keys.json добавлен в .gitignore")
    print("  - Никогда не коммитьте API ключи в систему контроля версий")
    print()
    
    key_manager = APIKeyManager()
    
    providers = {
        'openai': {
            'name': 'OpenAI (GPT models)',
            'description': 'For text generation with GPT-3.5, GPT-4',
            'url': 'https://platform.openai.com/api-keys',
            'required': True
        },
        'anthropic': {
            'name': 'Anthropic (Claude models)',
            'description': 'For text generation with Claude',
            'url': 'https://console.anthropic.com/settings/keys',
            'required': False
        },
        'stability': {
            'name': 'Stability AI',
            'description': 'For image generation with Stable Diffusion',
            'url': 'https://platform.stability.ai/account/keys',
            'required': False
        },
        'elevenlabs': {
            'name': 'ElevenLabs',
            'description': 'For voice/audio generation',
            'url': 'https://elevenlabs.io/app/settings/api-keys',
            'required': False
        },
        'runway': {
            'name': 'Runway ML',
            'description': 'For video generation',
            'url': 'https://runwayml.com/account',
            'required': False
        }
    }
    
    configured_count = 0
    
    for provider_id, info in providers.items():
        print("-" * 70)
        print(f"\n{info['name']}")
        print(f"Purpose: {info['description']}")
        print(f"Get API key: {info['url']}")
        
        if key_manager.has_key(provider_id):
            current_key = key_manager.get_masked_key(provider_id)
            print(f"Current key: {current_key}")
            
            update = input("\nUpdate this key? (y/n) [n]: ").strip().lower()
            if update != 'y':
                configured_count += 1
                continue
        elif info['required']:
            print("\n⚠ This provider is REQUIRED for basic functionality")
        
        api_key = input(f"\nEnter API key for {info['name']} (or press Enter to skip): ").strip()
        
        if api_key:
            key_manager.set_key(provider_id, api_key)
            print(f"✓ API key for {info['name']} configured")
            configured_count += 1
        elif info['required']:
            print(f"⚠ Warning: {info['name']} is required but not configured")
    
    print("\n" + "=" * 70)
    
    if configured_count > 0:
        save = input(f"\nSave {configured_count} API key(s)? (y/n) [y]: ").strip().lower()
        if save != 'n':
            key_manager.save_keys()
            print()
            print("✓ API keys saved successfully!")
            print()
            print("Next steps:")
            print("1. Verify .api_keys.json is in your .gitignore")
            print("2. Run: python -m src.main")
            print()
            print("Следующие шаги:")
            print("1. Проверьте, что .api_keys.json в вашем .gitignore")
            print("2. Запустите: python -m src.main")
        else:
            print("\n✗ API keys not saved")
    else:
        print("\n⚠ No API keys configured")
        print("Run this script again when you have API keys")
    
    print("\n" + "=" * 70)


def main():
    """Main entry point."""
    try:
        setup_api_keys()
    except KeyboardInterrupt:
        print("\n\n✗ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error during setup: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
