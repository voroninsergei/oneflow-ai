# GitHub Workflows Documentation

This directory contains all CI/CD workflows and automation for OneFlow.AI.

## 📋 Workflows Overview

### Core CI/CD Workflows

#### 1. **CI/CD Pipeline** (`ci.yml` & `ci-improved.yml`)
- **Triggers:** Push/PR to `main`/`develop`
- **Jobs:**
  - ✅ Code linting (Ruff, Black, isort)
  - ✅ Type checking (MyPy)
  - ✅ Security linting (Bandit, Pylint)
  - ✅ Unit tests with coverage (pytest)
  - ✅ Integration tests
  - ✅ Docker build & test
  - ✅ Multi-OS testing (Ubuntu, macOS, Windows)
  - ✅ Multi-Python testing (3.9, 3.10, 3.11, 3.12)
- **Features:**
  - Pip caching for faster builds
  - Parallel test execution
  - Coverage reporting to Codecov
  - Artifact uploads for debugging

#### 2. **Tests** (`tests.yml`)
- **Triggers:** Push/PR to `main`/`develop`
- **Jobs:**
  - Unit tests
  - E2E tests
  - Integration tests
  - Code quality checks
  - Coverage reporting

#### 3. **CodeQL Security Analysis** (`codeql.yml`)
- **Triggers:** Push/PR, Weekly schedule (Mondays 6:00 UTC), Manual
- **Features:**
  - Automated vulnerability detection
  - Security-extended queries
  - SARIF upload to GitHub Security tab
  - Fails on critical/high severity issues

#### 4. **Scheduled Security Scans** (`security-scheduled.yml`)
- **Triggers:** Daily at 3:00 AM UTC, Manual
- **Scans:**
  - Dependency vulnerabilities (Safety, pip-audit)
  - Container security (Trivy)
  - License compliance (pip-licenses)
- **Features:**
  - Auto-creates GitHub issues for vulnerabilities
  - 90-day artifact retention
  - Comprehensive security reports

### Publishing Workflows

#### 5. **PyPI Publishing** (`pypi-publish.yml`)
- **Triggers:** GitHub Release, Manual (with TestPyPI option)
- **Process:**
  1. Build distribution packages (wheel & sdist)
  2. Verify package metadata
  3. Publish to PyPI (on release) or TestPyPI (manual)
  4. Create GitHub release notes
  5. Test installation across Python versions
- **Features:**
  - Trusted publishing (OIDC)
  - Automatic release notes generation
  - Installation verification

#### 6. **Docker Publishing** (`docker-publish.yml`)
- **Triggers:** Push to `main`, Tags `v*.*.*`, PR to `main`, Manual
- **Process:**
  1. Build multi-arch images (amd64, arm64)
  2. Push to GitHub Container Registry (GHCR)
  3. Security scanning (Trivy)
  4. Generate build provenance
- **Tags Generated:**
  - `latest` (main branch)
  - `vX.Y.Z` (semantic version)
  - `X.Y` (major.minor)
  - `X` (major only)
  - `branch-name` (feature branches)
  - `sha-XXXXXXX` (git SHA)

## 🤖 Automation

### Dependabot (`dependabot.yml`)
- **Python dependencies:** Weekly updates (Mondays 9:00 UTC)
  - Groups minor/patch updates
  - Separate groups for prod vs dev dependencies
- **GitHub Actions:** Weekly updates (Mondays 9:00 UTC)
  - Groups all action updates
- **Docker base images:** Weekly updates (Mondays 9:00 UTC)
- **Features:**
  - Auto-assigns to @voroninsergei
  - Proper labeling (dependencies, python, github-actions, docker)
  - Grouped PRs to reduce noise

## 📊 Monitoring & Reports

### Artifacts Generated
- **Security Reports** (30-90 days retention):
  - Bandit security analysis
  - Safety vulnerability reports
  - pip-audit findings
  - Trivy container scans
  - License compliance reports

- **Test Results** (30 days retention):
  - Coverage reports (XML, HTML)
  - Test results per OS/Python version
  - Integration test logs

- **Build Artifacts** (7 days retention):
  - Python distribution packages
  - Docker build metadata

### Coverage Reports
- Uploaded to Codecov for Python 3.11/Ubuntu
- HTML reports available as artifacts
- Branch coverage enabled
- Minimum coverage tracked (configurable)

## 🔒 Security Features

### Code Scanning
- **CodeQL:** Weekly automated scans + PR checks
- **Bandit:** Python security linting on every commit
- **Trivy:** Daily container vulnerability scans
- **Safety:** Daily dependency vulnerability checks

### Secret Scanning
- GitHub's built-in secret scanning enabled
- No secrets should be committed to the repository
- Use GitHub Secrets for sensitive data

### Security Policies
1. All critical/high vulnerabilities block CI
2. Daily automated security reports
3. Auto-created issues for vulnerabilities
4. 90-day retention of security reports for audit

## 🚀 Usage

### Running Workflows Manually

```bash
# Trigger CI pipeline
gh workflow run ci.yml

# Run security scan
gh workflow run security-scheduled.yml

# Publish to TestPyPI
gh workflow run pypi-publish.yml -f test_pypi=true

# Build and publish Docker image
gh workflow run docker-publish.yml
```

### Local Development

```bash
# Install dependencies
pip install -e ".[dev,api,web,db,auth]"

# Run tests locally
pytest -v --cov=src

# Run linting
ruff check src/ tests/
black --check src/ tests/
mypy src/

# Run security checks
bandit -r src/
safety check
pip-audit
```

### Pre-commit Hooks (Recommended)

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## 📈 Performance

### Build Times (Approximate)
- Lint job: 2-3 minutes
- Test job (per Python version): 5-7 minutes
- Docker build: 8-12 minutes
- Security scans: 5-10 minutes
- Total CI pipeline: 15-20 minutes

### Caching Strategy
- **Pip packages:** Cached per OS/Python version
- **Docker layers:** BuildKit cache (local + GitHub Actions)
- **CodeQL database:** Cached between runs
- **Cache keys include:**
  - OS and Python version
  - Hash of requirements files
  - Workflow version identifier

## 🔧 Maintenance

### Adding New Dependencies
1. Update `requirements.txt` or `setup.py`
2. Dependabot will detect and create PR
3. Review and merge
4. CI will validate changes

### Updating Python Versions
1. Update matrix in `ci.yml` and `tests.yml`
2. Update Dockerfile if needed
3. Test locally before merging

### Security Updates
- **Critical:** Address immediately (< 24 hours)
- **High:** Address within 1 week
- **Medium/Low:** Address in next sprint

## 📝 Best Practices

1. **Always run tests locally** before pushing
2. **Use descriptive commit messages** for better changelog
3. **Tag releases** using semantic versioning (v1.2.3)
4. **Review security reports** weekly
5. **Keep dependencies updated** via Dependabot
6. **Document breaking changes** in release notes

## 🆘 Troubleshooting

### Common Issues

**Issue:** Tests fail with import errors
```bash
# Solution: Reinstall in editable mode
pip install -e ".[dev]"
```

**Issue:** Docker build fails on arm64
```bash
# Solution: Enable multi-platform builds
docker buildx create --use
```

**Issue:** Coverage upload fails
```bash
# Solution: Set CODECOV_TOKEN in GitHub Secrets
```

**Issue:** Dependabot PRs fail
```bash
# Solution: Check compatibility matrix in setup.py
```

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [CodeQL Documentation](https://codeql.github.com/docs/)
- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [Docker Buildx Documentation](https://docs.docker.com/buildx/working-with-buildx/)
- [PyPI Publishing Guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)

---

**Maintained by:** @voroninsergei  
**Last Updated:** October 2025
