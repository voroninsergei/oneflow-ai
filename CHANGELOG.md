# Changelog

All notable changes to OneFlow.AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned for v3.0.0
- PostgreSQL-only support (SQLite removal)
- API v1 deprecation
- Legacy authentication sunset

---

## [2.0.0] - 2025-10-10

### 🚀 Major Release - Production Ready

**BREAKING CHANGES:**
- Upgraded to Pydantic v2 (v1 no longer supported)
- API endpoints moved to `/api/v1/` and `/api/v2/` (root endpoints deprecated)
- Regional configuration required for new users (defaults to US)
- Response schema changes in v2 (added `request_id`, `timestamp`, `latency_ms`)

### Added

#### API & Contracts
- API versioning system with `/api/v1/` and `/api/v2/` endpoints
- Pydantic v2 schemas with strict validation
- Contract tests for backward compatibility
- API version discovery endpoint at `/api/versions`
- Automated validation of breaking changes

#### Multi-Region Support
- Regional data governance for US, EU, and RU regions
- Data residency enforcement - data stays in region of origin
- Regional encryption - AES-256-GCM (US/EU), GOST (RU)
- Cross-region transfer policies with compliance checks
- Regional rate limits and quotas
- Regional provider isolation (OpenAI-US/EU, YandexGPT-RU)

#### Compliance & Security
- GDPR compliance (EU) - Articles 44-50
- CCPA compliance (US) - California privacy rights
- FZ-152 compliance (RU) - Data localization
- Data retention policies by region
- Encryption at rest and in transit
- Incident response procedures

#### CI/CD & Deployment
- GitHub Container Registry (GHCR) publishing
- PyPI package distribution
- Docker multi-arch builds (amd64, arm64)
- Automated releases via GitHub Actions
- Security scanning with Trivy
- Artifact attestation

#### Documentation
- Data Governance Guide (`docs/DATA_GOVERNANCE.md`)
- API versioning guide
- Regional compliance documentation
- Installation guides for Docker and PyPI

### Changed
- Refactored web server to support multiple API versions
- Enhanced authentication with regional considerations
- Improved error handling with detailed compliance messages

### Fixed
- Rate limiting edge cases
- Database connection pooling issues
- CORS configuration for multi-origin requests

### Security
- End-to-end encryption for all data
- JWT token rotation policies
- API key hashing with bcrypt
- SQL injection prevention
- XSS protection headers

---

## [1.0.0] - 2025-01-15

### 🎉 Initial Release

### Added

#### Core Features
- Multi-modal AI support (Text, Image, Audio, Video)
- Smart routing with automatic fallbacks
- Transparent pricing and cost estimation
- Unified wallet system
- Budget controls (daily/weekly/monthly limits)
- Analytics dashboard

#### Provider Integrations
- OpenAI integration (GPT, DALL-E)
- Anthropic integration (Claude)
- Stability AI integration
- ElevenLabs integration

#### Infrastructure
- FastAPI web server
- SQLAlchemy ORM with SQLite/PostgreSQL support
- JWT authentication
- API key management
- Rate limiting

#### Developer Experience
- CLI interface
- Python SDK
- Interactive dashboard
- Swagger documentation
- Comprehensive test suite (58+ tests)

---

## [0.1.0] - 2024-12-01

### 🧪 Initial Public Beta

First public beta release. System is in preview - not recommended for production use.

### Added
- Beta status badge and preview documentation
- Environment variable-based secret management
- Legacy `.api_keys.json` format (development only) with migration script
- Basic QA workflow using GitHub Actions (`ci.yml`)
  - Code formatting checks (ruff, black)
  - Type checking (mypy)
  - Test suite with coverage (pytest)
  - Coverage badges in README
- PEP 621 packaging via `pyproject.toml`
- Unified version number system
- Initial changelog

### Changed
- Pricing documentation updated to reference token-based billing (`pricing_v2.py`)
- Pricing tables show credits per 1K tokens as approximate values
- Performance and availability metrics rephrased as targets (not SLOs)
- Benchmarks removed from static documentation

### Removed
- Placeholder `.gitignore_file.txt` replaced with comprehensive `.gitignore`
- Claims of "production ready" and "99.9% uptime" from README

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
# Option 1: Use v1 endpoint (backward compatible)
response = requests.post("http://localhost:8000/api/v1/request", json={
    "provider": "gpt",
    "prompt": "Hello"
})

# Option 2: Use v2 with enhanced features
response = requests.post("http://localhost:8000/api/v2/request", json={
    "provider": "gpt",
    "prompt": "Hello",
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 1000
})
```

#### Pydantic v2 Migration

**Before (Pydantic v1):**
```python
class MyModel(BaseModel):
    class Config:
        orm_mode = True
```

**After (Pydantic v2):**
```python
from pydantic import ConfigDict

class MyModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
```

**Update command:**
```bash
pip install pydantic>=2.0.0
```

#### Regional Configuration

**New in v2:**
```python
from src.region_manager import RegionManager, Region

# Select region
rm = RegionManager()
user_region = rm.select_region(user_preference="eu")

# Validate compliance
compliance = rm.validate_compliance(Region.EU, "store_user_data")
```

---

## Deprecation Timeline

| Feature | Deprecated In | Removed In | Alternative |
|---------|--------------|------------|-------------|
| API v1 endpoints | v2.0.0 (2025-10-10) | v3.0.0 (2026-Q1) | API v2 endpoints |
| SQLite support | v2.0.0 (2025-10-10) | v3.0.0 (2026-Q1) | PostgreSQL |
| Legacy auth | v2.0.0 (2025-10-10) | v3.0.0 (2026-Q1) | JWT + regional auth |

---

## Version Support Policy

| Version | Release Date | End of Support | Status |
|---------|--------------|----------------|--------|
| 2.0.x   | 2025-10-10  | 2026-10-10    | ✅ **Active** |
| 1.0.x   | 2025-01-15  | 2025-07-15    | ⚠️ **Security fixes only** |
| 0.1.x   | 2024-12-01  | 2025-01-15    | ❌ **Unsupported** |

---

## Links

- 🏠 **Repository**: https://github.com/voroninsergei/oneflow-ai
- 📦 **PyPI**: https://pypi.org/project/oneflow-ai/
- 🐳 **Docker**: ghcr.io/voroninsergei/oneflow-ai
- 📚 **Documentation**: https://github.com/voroninsergei/oneflow-ai/tree/main/docs
- 🐛 **Issues**: https://github.com/voroninsergei/oneflow-ai/issues

---

**Contributors**: Sergey Voronin  
**License**: Proprietary  
**Copyright**: © 2024-2025 Sergey Voronin. All rights reserved.
