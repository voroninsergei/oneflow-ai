# Contributing to OneFlow.AI
## Участие в разработке OneFlow.AI

Thank you for your interest in contributing to OneFlow.AI! This document provides guidelines for contributing to the project.

Спасибо за интерес к участию в разработке OneFlow.AI! Этот документ содержит руководство по участию в проекте.

---

## 📋 Table of Contents | Содержание

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Coding Standards](#coding-standards)
5. [Testing Guidelines](#testing-guidelines)
6. [Submitting Changes](#submitting-changes)
7. [Review Process](#review-process)

---

## Code of Conduct

### English

This project adheres to a code of conduct that all contributors are expected to follow:

- **Be respectful**: Treat everyone with respect and consideration
- **Be collaborative**: Work together towards common goals
- **Be professional**: Maintain professionalism in all interactions
- **Be inclusive**: Welcome diverse perspectives and backgrounds

### Русский

Этот проект следует кодексу поведения, которому должны следовать все участники:

- **Будьте уважительны**: Относитесь ко всем с уважением
- **Будьте готовы к сотрудничеству**: Работайте вместе для достижения общих целей
- **Будьте профессиональны**: Поддерживайте профессионализм во всех взаимодействиях
- **Будьте открыты**: Приветствуйте разнообразие взглядов и опыта

---

## Getting Started

### Before You Begin

1. **Check existing issues**: Look for existing issues or feature requests
2. **Discuss major changes**: For significant changes, open an issue first to discuss
3. **Read the documentation**: Familiarize yourself with the codebase

### Ways to Contribute

- 🐛 **Bug reports**: Report bugs you discover
- 💡 **Feature requests**: Suggest new features
- 📝 **Documentation**: Improve documentation
- 🔧 **Code contributions**: Submit bug fixes or new features
- 🌍 **Translations**: Help translate documentation
- ✅ **Testing**: Write or improve tests

---

## Development Setup

### Prerequisites

```bash
# Python 3.7 or higher
python --version

# Git
git --version
```

### Setup Steps

1. **Fork the repository**

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/OneFlow.AI.git
cd OneFlow.AI
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
# Install project dependencies
pip install -r requirements.txt

# Install development dependencies
make dev-setup
# Or manually:
pip install pytest pytest-cov black flake8 mypy
```

4. **Verify installation**

```bash
# Run tests to ensure everything works
pytest -v
```

---

## Coding Standards

### Python Style Guide

We follow **PEP 8** with some modifications:

- **Line length**: 120 characters maximum
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Single quotes for strings (unless double quotes avoid escaping)
- **Imports**: Group stdlib, third-party, and local imports

### Code Formatting

Use **Black** for code formatting:

```bash
# Format all code
make format

# Or manually
black src/ tests/ --line-length=120
```

### Linting

Use **flake8** for linting:

```bash
# Run linter
make lint

# Or manually
flake8 src/ tests/ --max-line-length=120
```

### Type Hints

Use type hints where appropriate:

```python
def process_request(model: str, prompt: str) -> dict:
    """Process an AI request."""
    pass
```

### Docstrings

Write bilingual docstrings (English and Russian):

```python
def example_function(param: str) -> bool:
    """
    Brief description in English.
    Краткое описание на русском.
    
    Args:
        param: Parameter description.
               Описание параметра.
    
    Returns:
        bool: Return value description.
              Описание возвращаемого значения.
    """
    pass
```

### Naming Conventions

- **Variables**: `snake_case`
- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private members**: `_leading_underscore`

---

## Testing Guidelines

### Writing Tests

1. **Test file naming**: `test_<module_name>.py`
2. **Test function naming**: `test_<functionality>`
3. **Use descriptive names**: Make test names clear and specific
4. **Test one thing**: Each test should verify one specific behavior

### Test Structure

```python
def test_feature_name():
    """Test description in English.
    
    Русский: Описание теста на русском.
    """
    # Arrange
    setup_data = prepare_test_data()
    
    # Act
    result = function_under_test(setup_data)
    
    # Assert
    assert result == expected_value
```

### Running Tests

```bash
# Run all tests
pytest -v

# Run specific test file
pytest tests/test_pricing.py -v

# Run with coverage
pytest --cov=src tests/

# Run tests matching pattern
pytest -k "test_budget"
```

### Test Coverage

- Aim for **80%+ coverage** for new code
- All new features must include tests
- Bug fixes should include regression tests

---

## Submitting Changes

### Branch Naming

Use descriptive branch names:

```bash
feature/add-new-provider
bugfix/fix-wallet-calculation
docs/update-readme
refactor/improve-router-logic
```

### Commit Messages

Write clear, descriptive commit messages:

```
<type>: <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Example**:

```
feat: add budget management system

- Implement Budget class with period-based limits
- Add provider-specific budget controls
- Include automatic period reset functionality

Closes #42
```

### Pull Request Process

1. **Create a branch**

```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes**

```bash
# Edit files
# Add tests
# Update documentation
```

3. **Run quality checks**

```bash
make quality  # Runs lint, typecheck, and tests
```

4. **Commit your changes**

```bash
git add .
git commit -m "feat: your descriptive message"
```

5. **Push to your fork**

```bash
git push origin feature/your-feature-name
```

6. **Create Pull Request**

- Go to GitHub and create a Pull Request
- Fill out the PR template
- Link relevant issues
- Request review

### Pull Request Checklist

Before submitting, ensure:

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No merge conflicts
- [ ] Code is properly formatted

---

## Review Process

### What to Expect

1. **Initial Review**: A maintainer will review within 2-3 business days
2. **Feedback**: You may receive requests for changes
3. **Iteration**: Make requested changes and push updates
4. **Approval**: Once approved, your PR will be merged

### Review Criteria

Reviewers will check:

- **Functionality**: Does it work as intended?
- **Tests**: Are there adequate tests?
- **Code Quality**: Is the code clean and maintainable?
- **Documentation**: Is documentation updated?
- **Style**: Does it follow coding standards?

---

## Specific Contribution Areas

### Adding New Providers

See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md#adding-new-providers) for detailed instructions.

**Quick steps**:

1. Create provider class in `src/providers/`
2. Implement `BaseProvider` interface
3. Add tests in `tests/`
4. Update documentation
5. Register in `__init__.py`

### Improving Documentation

Documentation improvements are always welcome:

- Fix typos or unclear explanations
- Add examples
- Improve translations
- Create tutorials

### Reporting Bugs

When reporting bugs, include:

- **Description**: Clear description of the issue
- **Steps to reproduce**: How to trigger the bug
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**: Python version, OS, etc.
- **Code samples**: Minimal reproducible example

**Bug Report Template**:

```markdown
**Bug Description**
A clear description of the bug.

**To Reproduce**
Steps to reproduce:
1. Initialize system with...
2. Call method...
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- Python version: 3.9
- OS: Windows 10
- OneFlow.AI version: 2.0.0

**Additional Context**
Any other relevant information.
```

---

## License

By contributing to OneFlow.AI, you agree that your contributions will be licensed under the same license as the project.

При участии в OneFlow.AI вы соглашаетесь, что ваш вклад будет лицензирован под той же лицензией, что и проект.

---

## Questions?

If you have questions about contributing:

- Check the [Developer Guide](DEVELOPER_GUIDE.md)
- Review [Examples](EXAMPLES.md)
- Open an issue for discussion

**Вопросы?**

Если у вас есть вопросы об участии:

- Проверьте [Руководство разработчика](DEVELOPER_GUIDE.md)
- Просмотрите [Примеры](EXAMPLES.md)
- Откройте issue для обсуждения

---

## Thank You! | Спасибо!

Thank you for contributing to OneFlow.AI! Your efforts help make this project better for everyone.

Спасибо за участие в OneFlow.AI! Ваши усилия помогают сделать этот проект лучше для всех.

---

**Project Maintainer**: Sergey Voronin (voroninsergeiai@gmail.com)
