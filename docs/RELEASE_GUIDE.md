# Release Guide

**OneFlow.AI Release Process**  
Complete guide for maintainers

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Release Types](#release-types)
3. [Release Process](#release-process)
4. [Automated Workflows](#automated-workflows)
5. [Manual Steps](#manual-steps)
6. [Rollback Procedure](#rollback-procedure)
7. [Post-Release](#post-release)

---

## Prerequisites

### Required Access

- ✅ Write access to GitHub repository
- ✅ PyPI trusted publisher configured
- ✅ GHCR write permissions
- ✅ GitHub release permissions

### Required Tools

```bash
# Install release tools
pip install build twine bump2version

# Verify tools
python -m build --version
twine --version
bump2version --version
```

### Configuration Files

Ensure these files are up to date:
- `setup.py` - Version and metadata
- `CHANGELOG.md` - Release notes
- `.github/workflows/*.yml` - CI/CD pipelines
- `Dockerfile` - Build configuration

---

## Release Types

### Semantic Versioning

We follow [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH

Example: 2.1.3
```

**Version Components:**

| Type | When to Increment | Example |
|------|-------------------|---------|
| **MAJOR** | Breaking API changes | 1.0.0 → 2.0.0 |
| **MINOR** | New features (backward compatible) | 2.0.0 → 2.1.0 |
| **PATCH** | Bug fixes (backward compatible) | 2.1.0 → 2.1.1 |

**Pre-release Tags:**
- `2.1.0-alpha.1` - Alpha release
- `2.1.0-beta.2` - Beta release
- `2.1.0-rc.1` - Release candidate

---

## Release Process

### 1. Prepare Release Branch

```bash
# Update main branch
git checkout main
git pull origin main

# Create release branch
git checkout -b release/v2.1.0
```

### 2. Update Version Numbers

Update version in multiple locations:

**`setup.py`:**
```python
VERSION = "2.1.0"
```

**`src/__init__.py`:**
```python
__version__ = "2.1.0"
```

**`Dockerfile`:**
```dockerfile
LABEL org.opencontainers.image.version="2.1.0"
```

Or use bump2version (recommended):

```bash
# For patch release (2.0.0 -> 2.0.1)
bump2version patch

# For minor release (2.0.0 -> 2.1.0)
bump2version minor

# For major release (2.0.0 -> 3.0.0)
bump2version major
```

### 3. Update CHANGELOG.md

Add release notes to `CHANGELOG.md`:

```markdown
## [2.1.0] - 2025-10-15

### Added
- New feature X
- Enhancement Y

### Changed
- Modified behavior Z

### Fixed
- Bug fix A
- Security patch B

### Deprecated
- Feature C will be removed in v3.0.0
```

### 4. Run Tests

```bash
# Run full test suite
pytest tests/ -v --cov=src

# Run contract tests
pytest tests/test_api_compatibility.py -v

# Check code quality
black src/ tests/
flake8 src/ tests/
mypy src/
```

### 5. Build and Test Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build package
python -m build

# Verify package
twine check dist/*

# Test installation locally
pip install dist/oneflow_ai-2.1.0-py3-none-any.whl
python -c "from src.main import OneFlowAI; print('Success!')"
```

### 6. Commit Changes

```bash
git add setup.py src/__init__.py CHANGELOG.md Dockerfile
git commit -m "chore: bump version to 2.1.0"
git push origin release/v2.1.0
```

### 7. Create Pull Request

1. Go to GitHub
2. Create Pull Request: `release/v2.1.0` → `main`
3. Title: "Release v2.1.0"
4. Description: Copy from CHANGELOG.md
5. Request reviews

### 8. Merge and Tag

After PR approval:

```bash
# Merge to main
git checkout main
git merge release/v2.1.0
git push origin main

# Create and push tag
git tag -a v2.1.0 -m "Release v2.1.0"
git push origin v2.1.0
```

### 9. Create GitHub Release

1. Go to GitHub → Releases → "Draft a new release"
2. Tag: `v2.1.0`
3. Title: "OneFlow.AI v2.1.0"
4. Description: Copy from CHANGELOG.md
5. Upload artifacts (optional)
6. Check "Set as latest release"
7. Click "Publish release"

**This triggers automated workflows:**
- ✅ Docker image build → GHCR
- ✅ PyPI package publish
- ✅ Security scanning
- ✅ Release notes generation

---

## Automated Workflows

### Docker Publishing

**Workflow:** `.github/workflows/docker-publish.yml`

**Triggers:**
- Tag push matching `v*.*.*`
- Manual workflow dispatch

**Actions:**
1. Build multi-arch Docker images (amd64, arm64)
2. Push to GHCR: `ghcr.io/voroninsergei/oneflow-ai`
3. Tag with version and `latest`
4. Run security scan with Trivy
5. Generate SBOM and attestation

**Manual trigger:**
```bash
# Via GitHub UI: Actions → Docker Publish → Run workflow

# Or via GitHub CLI
gh workflow run docker-publish.yml -f version=v2.1.0
```

### PyPI Publishing

**Workflow:** `.github/workflows/pypi-publish.yml`

**Triggers:**
- GitHub release published

**Actions:**
1. Build wheel and sdist packages
2. Publish to PyPI using trusted publisher
3. Upload artifacts to GitHub release
4. Test installation across Python versions (3.9-3.12)

**Testing on TestPyPI first:**
```bash
gh workflow run pypi-publish.yml -f test_pypi=true
```

---

## Manual Steps

### Manual PyPI Upload (if automated fails)

```bash
# Build packages
python -m build

# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ oneflow-ai

# Upload to PyPI
twine upload dist/*
```

### Manual Docker Build

```bash
# Build image
docker build -t ghcr.io/voroninsergei/oneflow-ai:v2.1.0 .

# Test image
docker run -p 8000:8000 ghcr.io/voroninsergei/oneflow-ai:v2.1.0

# Login to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Push image
docker push ghcr.io/voroninsergei/oneflow-ai:v2.1.0
docker tag ghcr.io/voroninsergei/oneflow-ai:v2.1.0 ghcr.io/voroninsergei/oneflow-ai:latest
docker push ghcr.io/voroninsergei/oneflow-ai:latest
```

---

## Rollback Procedure

### If Release Has Critical Bugs

**Option 1: Quick Patch Release**

```bash
# Create hotfix branch
git checkout -b hotfix/v2.1.1
# Fix bug, commit, release v2.1.1
```

**Option 2: Yank from PyPI**

```bash
# Yank broken version (doesn't delete, just hides)
pip install twine
twine upload --skip-existing dist/oneflow_ai-2.1.0*
# Contact PyPI support to yank: https://pypi.org/help/
```

**Option 3: Revert Docker Image**

```bash
# Re-tag previous version as latest
docker pull ghcr.io/voroninsergei/oneflow-ai:v2.0.0
docker tag ghcr.io/voroninsergei/oneflow-ai:v2.0.0 ghcr.io/voroninsergei/oneflow-ai:latest
docker push ghcr.io/voroninsergei/oneflow-ai:latest
```

**Option 4: Delete GitHub Release**

```bash
# Delete release and tag
gh release delete v2.1.0 --yes
git push origin :refs/tags/v2.1.0
```

---

## Post-Release

### Announce Release

**Update Documentation:**
- [ ] Update README.md with new version
- [ ] Update installation instructions
- [ ] Update migration guides

**Notify Users:**
- [ ] GitHub Discussions announcement
- [ ] Email to mailing list (if applicable)
- [ ] Social media post
- [ ] Update website

**Monitor:**
- [ ] Check PyPI downloads
- [ ] Monitor GitHub issues for bug reports
- [ ] Review Docker pull statistics
- [ ] Check security scan results

### Release Checklist

```markdown
## Pre-Release
- [ ] All tests passing
- [ ] CHANGELOG.md updated
- [ ] Version bumped in all files
- [ ] Documentation updated
- [ ] Migration guide written (if breaking changes)

## Release
- [ ] PR merged to main
- [ ] Git tag created and pushed
- [ ] GitHub release published
- [ ] Docker image published to GHCR
- [ ] PyPI package published
- [ ] Installation tested

## Post-Release
- [ ] Release announced
- [ ] Documentation site updated
- [ ] Next version milestone created
- [ ] Monitoring for issues
```

---

## Release Schedule

### Regular Releases

- **Patch releases**: As needed (bug fixes, security)
- **Minor releases**: Monthly (new features)
- **Major releases**: Quarterly (breaking changes)

### Supported Versions

| Version | Status | End of Support |
|---------|--------|----------------|
| 2.x     | ✅ Active | 2026-10-10 |
| 1.x     | ⚠️ Security only | 2025-07-15 |

---

## Emergency Hotfix Process

For critical security vulnerabilities:

1. **Create hotfix branch** from `main`
```bash
git checkout -b hotfix/security-fix
```

2. **Apply fix and test**
```bash
# Fix vulnerability
# Run security tests
pytest tests/security/ -v
```

3. **Fast-track release**
```bash
# Skip normal review process
git checkout main
git merge hotfix/security-fix
bump2version patch
git tag -a v2.1.1 -m "Security hotfix"
git push origin main --tags
```

4. **Notify users immediately**
- Create GitHub Security Advisory
- Email all users
- Update all documentation

---

## Contacts

**Release Manager**: Sergey Voronin  
**Email**: voroninsergeiai@gmail.com  
**GitHub**: @voroninsergei

**For urgent issues during release:**
- Create issue with `priority:critical` label
- Email release manager directly
- Use GitHub Discussions for questions

---

## Resources

- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [PyPI Publishing](https://packaging.python.org/tutorials/packaging-projects/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Trusted Publishing](https://docs.pypi.org/trusted-publishers/)

---

**Last Updated**: 2025-10-10  
**Version**: 1.0
