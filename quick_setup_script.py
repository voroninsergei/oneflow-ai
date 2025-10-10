#!/usr/bin/env python3
"""
Quick Setup Script for OneFlow.AI
Скрипт быстрой настройки для OneFlow.AI

This script helps you quickly set up the OneFlow.AI project structure.
Этот скрипт помогает быстро настроить структуру проекта OneFlow.AI.
"""

import os
import sys
from pathlib import Path

def create_directory_structure():
    """
    Create necessary directories for the project.
    Создать необходимые директории для проекта.
    """
    directories = [
        'src',
        'src/providers',
        'tests',
        'docs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def create_gitignore():
    """
    Create .gitignore file with necessary entries.
    Создать .gitignore с необходимыми записями.
    """
    gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# API Keys - NEVER COMMIT!
.api_keys.json
*.key
*.pem

# Virtual Environment
venv/
env/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/
*.cover

# Logs
*.log
logs/

# Temporary files
*.tmp
*.bak
temp/

# OS files
.DS_Store
Thumbs.db
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    
    print("✓ Created .gitignore")

def create_init_files():
    """
    Create __init__.py files for Python packages.
    Создать файлы __init__.py для Python пакетов.
    """
    init_files = [
        'src/__init__.py',
        'src/providers/__init__.py',
        'tests/__init__.py'
    ]
    
    for init_file in init_files:
        Path(init_file).touch()
        print(f"✓ Created: {init_file}")

def update_requirements():
    """
    Update requirements.txt with all dependencies.
    Обновить requirements.txt всеми зависимостями.
    """
    requirements = """# Core dependencies
pytest>=6.0
pytest-cov>=2.0

# Optional: For real API integration
# openai>=1.0.0
# anthropic>=0.5.0
# requests>=2.31.0

# Optional: Development tools
# black>=21.0
# flake8>=3.9
# mypy>=0.900
"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    
    print("✓ Created/Updated requirements.txt")

def create_example_config():
    """
    Create example configuration file.
    Создать пример файла конфигурации.
    """
    config_content = """{
  "rates": {
    "gpt": 1.0,
    "image": 10.0,
    "audio": 5.0,
    "video": 20.0
  },
  "wallet_balance": 100.0,
  "budget_limits": {
    "daily": 50.0,
    "weekly": 300.0,
    "monthly": 1000.0,
    "total": null
  },
  "provider_budgets": {
    "gpt": 100.0,
    "image": 200.0,
    "audio": 150.0,
    "video": 300.0
  },
  "region": "US"
}
"""
    
    with open('config.example.json', 'w') as f:
        f.write(config_content)
    
    print("✓ Created config.example.json")

def create_example_api_keys():
    """
    Create example API keys file.
    Создать пример файла API ключей.
    """
    api_keys_content = """{
  "openai": "sk-your-openai-api-key-here",
  "anthropic": "sk-ant-your-anthropic-api-key-here",
  "stability": "sk-your-stability-api-key-here",
  "elevenlabs": "your-elevenlabs-api-key-here",
  "runway": "your-runway-api-key-here"
}
"""
    
    with open('.api_keys.example.json', 'w') as f:
        f.write(api_keys_content)
    
    print("✓ Created .api_keys.example.json")

def check_existing_files():
    """
    Check which essential files already exist.
    Проверить, какие важные файлы уже существуют.
    """
    essential_files = {
        'src/main.py': False,
        'src/router.py': False,
        'src/pricing.py': False,
        'src/wallet.py': False,
        'src/analytics.py': False,
        'src/budget.py': False,
        'src/config.py': False,
        'src/api_keys.py': False,
        'src/cli.py': False,
        'src/real_api_integration.py': False,
        'src/providers/base_provider.py': False,
        'src/providers/gpt_provider.py': False,
        'src/providers/image_provider.py': False,
        'src/providers/audio_provider.py': False,
        'src/providers/video_provider.py': False,
    }
    
    print("\n" + "=" * 60)
    print("Checking existing files | Проверка существующих файлов")
    print("=" * 60)
    
    for file_path, _ in essential_files.items():
        exists = Path(file_path).exists()
        essential_files[file_path] = exists
        status = "✓ EXISTS" if exists else "✗ MISSING"
        print(f"{status}: {file_path}")
    
    missing_count = sum(1 for exists in essential_files.values() if not exists)
    
    print("\n" + "=" * 60)
    print(f"Summary | Сводка:")
    print(f"  Total files: {len(essential_files)}")
    print(f"  Existing: {len(essential_files) - missing_count}")
    print(f"  Missing: {missing_count}")
    print("=" * 60)
    
    return essential_files, missing_count

def provide_next_steps(missing_count):
    """
    Provide instructions for next steps.
    Предоставить инструкции для следующих шагов.
    """
    print("\n" + "=" * 60)
    print("Next Steps | Следующие шаги")
    print("=" * 60)
    
    if missing_count == 0:
        print("\n✓ All essential files exist!")
        print("  You can now run the project:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Run tests: pytest -v")
        print("  3. Run demo: python -m src.main --demo")
        print("  4. Run interactive: python -m src.main")
    else:
        print(f"\n⚠ {missing_count} files are missing.")
        print("\nTo complete the setup:")
        print("\n1. Copy code from artifacts/documents to create missing files:")
        print("   - src/analytics.py (from Analytics Module artifact)")
        print("   - src/budget.py (from budget_module.py document)")
        print("   - src/config.py (from config_module.py document)")
        print("   - src/api_keys.py (from api_keys_module.py document)")
        print("   - src/cli.py (from cli_module.py document)")
        print("   - src/real_api_integration.py (from Real API Integration artifact)")
        print("   - src/main.py (update with Complete Main Module artifact)")
        
        print("\n2. Install dependencies:")
        print("   pip install -r requirements.txt")
        
        print("\n3. Run tests:")
        print("   pytest -v")
        
        print("\n4. Run demo:")
        print("   python -m src.main --demo")
    
    print("\n" + "=" * 60)

def main():
    """
    Main setup function.
    Основная функция настройки.
    """
    print("=" * 60)
    print("OneFlow.AI Quick Setup | Быстрая настройка OneFlow.AI")
    print("=" * 60)
    print("\nThis script will set up the basic project structure.")
    print("Этот скрипт настроит базовую структуру проекта.\n")
    
    # Step 1: Create directories
    print("\nStep 1: Creating directories...")
    create_directory_structure()
    
    # Step 2: Create .gitignore
    print("\nStep 2: Creating .gitignore...")
    create_gitignore()
    
    # Step 3: Create __init__.py files
    print("\nStep 3: Creating __init__.py files...")
    create_init_files()
    
    # Step 4: Update requirements.txt
    print("\nStep 4: Creating requirements.txt...")
    update_requirements()
    
    # Step 5: Create example files
    print("\nStep 5: Creating example configuration files...")
    create_example_config()
    create_example_api_keys()
    
    # Step 6: Check existing files
    essential_files, missing_count = check_existing_files()
    
    # Step 7: Provide next steps
    provide_next_steps(missing_count)
    
    print("\n✓ Setup script completed!")
    print("  For detailed instructions, see the Final Completion Guide artifact.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error during setup: {e}")
        sys.exit(1)
