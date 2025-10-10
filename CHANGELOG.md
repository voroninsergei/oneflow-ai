# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Improved monitoring and observability
- Enhanced fallback strategies
- Performance optimization
- Additional AI provider integrations

## [0.1.0] - 2025-10-10

### Added
- Multi-modal AI support (Text, Image, Audio, Video)
- Smart routing with automatic provider selection
- Transparent pricing and cost estimation
- Unified wallet system with credit management
- Budget controls (daily/weekly/monthly limits)
- Analytics dashboard with usage tracking
- Multi-region support (US/EU/RU)
- Database persistence (SQLAlchemy with SQLite/PostgreSQL)
- Web API with FastAPI and interactive dashboard
- JWT authentication and secure user management
- API key management per user
- Rate limiting (60 req/min, 1000 req/hour)
- Real API integration with OpenAI, Anthropic, Stability AI, ElevenLabs
- Automatic fallback mechanisms
- CLI interface for system management
- Comprehensive test suite (58+ tests)
- Full documentation in English and Russian

### Security
- Secure password hashing with bcrypt
- API key storage with proper encryption
- Environment-based secret management

### Known Limitations
- Beta release - use with caution in production
- Fallback mechanism tested under limited scenarios
- Rate limiting is basic implementation
- No distributed tracing yet

[Unreleased]: https://github.com/voroninsergei/oneflow-ai/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/voroninsergei/oneflow-ai/releases/tag/v0.1.0
