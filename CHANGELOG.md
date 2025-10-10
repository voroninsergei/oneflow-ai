# Changelog
## [0.1.0] - 2025-10-10

### 🎉 Initial Public Beta

This release marks the first public beta of OneFlow.AI.  The project has been refactored to reflect its early‑stage nature and to set realistic expectations for users.

#### Added
- A beta status badge and updated documentation to highlight that the system is in preview.  Removed claims of “production ready”, “99.9 % uptime” and 100 % readiness from the README.
- A clearly documented secret management approach that prioritises environment variables and external secret managers.  The legacy `.api_keys.json` format is now explicitly marked as **development‑only** and a migration script is provided.
- A basic quality assurance workflow using GitHub Actions (`ci.yml`) that runs ruff, black, mypy and pytest with coverage.  Coverage results are exposed via badges in the README.
- Packaging via PEP 621 using `pyproject.toml` with a unified version number (`0.1.0`) and updated `setup.py`/`pyproject.poetry.toml` to match.  This lays the groundwork for automated releases to PyPI.
- An initial entry in the changelog to track future changes.  Follow [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and [Semantic Versioning](https://semver.org/) going forward.

#### Changed
- The pricing documentation now explicitly references the token‑based billing engine (`pricing_v2.py`) instead of implying per‑word pricing.  Pricing tables denote credits per 1 K tokens as approximate values.
- Performance and availability metrics in the README have been rephrased as **targets** rather than accomplished SLOs.  Benchmarks are removed from the static documentation because they depend on the deployment environment.

#### Removed
- The placeholder `.gitignore_file.txt` has been removed in favour of a comprehensive `.gitignore` that includes database files, logs and other artifacts.

All notable changes to OneFlow.AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2025-10-10

### 🚀 Major Release - Production Ready

### Added

#### API Versioning & Contracts
- ✅ **API versioning system** with `/api/v1/` and `/api/v2/` endpoints
- ✅ **Pydantic v2 schemas** with strict validation
- ✅ **Contract tests** for backward compatibility
- ✅ **API version discovery** endpoint at `/api/versions`
- ✅ Automated validation of breaking changes

#### Multi-Region Support
- ✅ **Regional data governance** for US, EU, and RU regions
- ✅ **Data residency enforcement** - data stays in region of origin
- ✅ **Regional encryption** - AES-256-GCM (US/EU), GOST (RU)
- ✅ **Cross-region transfer policies** with compliance checks
- ✅ **Regional rate limits** and quotas
- ✅ **Regional provider isolation** (OpenAI-US/EU, YandexGPT-RU)

#### Compliance & Security
- ✅ **GDPR compliance** (EU) - Articles 44-50
- ✅ **CCPA compliance** (US) - California privacy rights
- ✅ **FZ-152 compliance** (RU) - Data localization
- ✅ **Data retention policies** by region
- ✅ **Encryption at rest and in transit**
- ✅ **Incident response procedures**

#### CI/CD & Deployment
- ✅ **GitHub Container Registry (GHCR)** publishing
- ✅ **PyPI package** distribution
- ✅ **Docker multi-arch builds** (amd64, arm64)
- ✅ **Automated releases** via GitHub Actions
- ✅ **Security scanning** with Trivy
- ✅ **Artifact attestation**

#### Documentation
- ✅ **Data Governance Guide** (`docs/DATA_GOVERNANCE.md`)
- ✅ **API versioning guide**
- ✅ **Regional compliance documentation**
- ✅ **Installation guides** for Docker and PyPI

### Changed

- 🔄 **Upgraded to Pydantic v2** - Breaking change from v1
- 🔄 **Refactored web server** to support multiple API versions
- 🔄 **Enhanced authentication** with regional considerations
- 🔄 **Improved error handling** with detailed compliance messages

### Fixed

- 🐛 Fixed rate limiting edge cases
- 🐛 Resolved database connection pooling issues
- 🐛 Fixed CORS configuration for multi-origin requests

### Security

- 🔒 End-to-end encryption for all data
- 🔒 JWT token rotation policies
- 🔒 API key hashing with bcrypt
- 🔒 SQL injection prevention
- 🔒 XSS protection headers

---

## [1.0.0] - 2025-01-15

### Initial Release

#### Core Features
- ✅ Multi-modal AI support (Text, Image, Audio, Video)
- ✅ Smart routing with automatic fallbacks
- ✅ Transparent pricing and cost estimation
- ✅ Unified wallet system
- ✅ Budget controls (daily/weekly/monthly limits)
- ✅ Analytics dashboard

#### Providers
- ✅ OpenAI integration (GPT, DALL-E)
- ✅ Anthropic integration (Claude)
- ✅ Stability AI integration
- ✅ ElevenLabs integration

#### Infrastructure
- ✅ FastAPI web server
- ✅ SQLAlchemy ORM with SQLite/PostgreSQL
- ✅ JWT authentication
- ✅ API key management
- ✅ Rate limiting

#### Developer Experience
- ✅ CLI interface
- ✅ Python SDK
- ✅ Interactive dashboard
- ✅ Swagger documentation
- ✅ Comprehensive test suite (58+ tests)

---

## Migration Guides

### Migrating from v1 to v2

#### API Versioning

**Before (v1):**
```python
response = requests.post("http://localhost:8000/request", json={
    "provider": "gpt",
    "prompt": "Hello"
})
```

**After (v2):**
```python
# Option 1: Use v1 endpoint (no changes needed)
response = requests.post("http://localhost:8000/api/v1/request", json={
    "provider": "gpt",
    "prompt": "Hello"
})

# Option 2: Use v2 with new features
response = requests.post("http://localhost:8000/api/v2/request", json={
    "provider": "gpt",
    "prompt": "Hello",
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 1000
})
```

#### Pydantic v2

**Before (Pydantic v1):**
```python
class Config:
    orm_mode = True
```

**After (Pydantic v2):**
```python
model_config = ConfigDict(from_attributes=True)
```

#### Regional Configuration

**New in v2:**
```python
from src.region_manager import RegionManager, Region

# Select region
rm = RegionManager()
user_region = rm.select_region(user_preference="eu")

# Check compliance
compliance = rm.validate_compliance(Region.EU, "store_user_data")
```

---

## Breaking Changes

### v2.0.0

1. **Pydantic v2 Required** - Pydantic v1 is no longer supported
   - Update: `pip install pydantic>=2.0.0`
   
2. **API Versioning** - Root endpoints moved to `/api/v1/` and `/api/v2/`
   - Old: `/request` → New: `/api/v1/request`
   - Old endpoints redirect to v1 with deprecation warning

3. **Regional Configuration Required** - Must specify region for new users
   - Default: US region if not specified
   
4. **Response Schema Changes** - v2 responses include additional fields
   - `request_id`, `timestamp`, `latency_ms` are now mandatory in v2

---

## Deprecation Notices

### Planned for v3.0.0 (2026-Q1)

- ⚠️ **API v1 will be deprecated** in v3.0.0
- ⚠️ SQLite support will be removed (PostgreSQL only)
- ⚠️ Legacy authentication methods will be sunset

---

## Version Support Policy

| Version | Release Date | End of Support | Status |
|---------|--------------|----------------|--------|
| 2.0.x   | 2025-10-10  | 2026-10-10    | ✅ Current |
| 1.0.x   | 2025-01-15  | 2025-07-15    | ⚠️ Security fixes only |

---

## Links

- **Repository**: https://github.com/voroninsergei/oneflow-ai
- **PyPI**: https://pypi.org/project/oneflow-ai/
- **Docker**: ghcr.io/voroninsergei/oneflow-ai
- **Documentation**: https://github.com/voroninsergei/oneflow-ai/tree/main/docs
- **Issues**: https://github.com/voroninsergei/oneflow-ai/issues

---

**Contributors**: Sergey Voronin
**License**: Proprietary
**Copyright**: © 2025 Sergey Voronin. All rights reserved.
