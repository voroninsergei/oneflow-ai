# Contributing to OneFlow.AI

Thank you for your interest in contributing! This document provides guidelines and instructions.

## Development Setup

1. **Fork and clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/oneflow-ai.git
cd oneflow-ai
```

2. **Install development dependencies**
```bash
pip install -e ".[dev]"
```

3. **Install pre-commit hooks**
```bash
pre-commit install
```

## Code Style and Quality

We use the following tools to maintain code quality:

### Ruff
- **Linting and formatting**: We use [Ruff](https://github.com/astral-sh/ruff) for fast Python linting
- Configuration: See `pyproject.toml` or `ruff.toml`
- Run linting: `ruff check .`
- Auto-fix issues: `ruff check --fix .`
- Format code: `ruff format .`

### Black
- **Code formatting**: [Black](https://github.com/psf/black) ensures consistent code style
- Line length: 100 characters (or as configured)
- Run formatting: `black .`
- Check formatting: `black --check .`

### Mypy
- **Type checking**: [Mypy](https://mypy-lang.org/) performs static type analysis
- Run type checking: `mypy src/`
- Configuration: See `pyproject.toml` or `mypy.ini`
- Ensure all public functions have type hints

### Running All Checks
```bash
# Run all quality checks at once
ruff check . && black --check . && mypy src/
```

## Branching Strategy

We follow a simplified Git Flow model:

- **`main`** - Production-ready code, protected branch
- **`develop`** - Integration branch for features
- **`feature/*`** - New features (e.g., `feature/add-login`)
- **`bugfix/*`** - Bug fixes (e.g., `bugfix/fix-auth-error`)
- **`hotfix/*`** - Urgent production fixes
- **`release/*`** - Release preparation branches

### Creating a Branch
```bash
# For new features
git checkout develop
git checkout -b feature/your-feature-name

# For bug fixes
git checkout develop
git checkout -b bugfix/issue-description
```

## Pull Request Process

1. **Before submitting**:
   - Update your branch with the latest changes from `develop`
   - Run all code quality checks
   - Add/update tests for your changes
   - Update documentation if needed

2. **PR Title**: Use clear, descriptive titles
   - ✅ `feat: Add user authentication system`
   - ✅ `fix: Resolve database connection timeout`
   - ✅ `docs: Update API documentation`

3. **PR Description**: Use the provided template and fill all sections

4. **Review Process**:
   - At least one approval required
   - All CI checks must pass
   - Address review comments promptly
   - Keep discussions focused and professional

5. **Merging**: 
   - Squash commits when merging to keep history clean
   - Delete branch after merging

## Pull Request Checklist

Before submitting your PR, ensure:

- [ ] Code follows project style guidelines (ruff, black, mypy)
- [ ] All tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated (docstrings, README, etc.)
- [ ] Commit messages are clear and descriptive
- [ ] No merge conflicts with target branch
- [ ] PR description is complete and references related issues
- [ ] Breaking changes are clearly documented

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_specific.py
```

## Commit Message Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

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

**Examples**:
```
feat(auth): add OAuth2 authentication

fix(api): resolve timeout issue in user endpoint

docs: update installation instructions
```

## Getting Help

- 📖 Check existing [documentation](./docs)
- 💬 Join our [discussions](https://github.com/oneflow-ai/oneflow-ai/discussions)
- 🐛 Report bugs via [issues](https://github.com/oneflow-ai/oneflow-ai/issues)
- 📧 Contact maintainers: [email protected]

## Code of Conduct

Please be respectful and constructive in all interactions. We are committed to providing a welcoming and inclusive environment for all contributors.

---

Thank you for contributing to OneFlow.AI! 🚀
