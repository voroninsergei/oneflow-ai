# Data Governance & Regional Compliance

**OneFlow.AI Multi-Region Data Policy**  
Version: 1.0  
Last Updated: 2025-10-10  
Status: Active

---

## Table of Contents

1. [Overview](#overview)
2. [Regional Architecture](#regional-architecture)
3. [Data Residency](#data-residency)
4. [Encryption Standards](#encryption-standards)
5. [Traffic Routing](#traffic-routing)
6. [Regional Limits & Quotas](#regional-limits--quotas)
7. [Compliance](#compliance)
8. [Data Retention](#data-retention)
9. [Incident Response](#incident-response)

---

## Overview

OneFlow.AI operates in three primary regions with strict data governance policies:
- **United States (US)** - `us-east-1`
- **European Union (EU)** - `eu-central-1`
- **Russian Federation (RU)** - `ru-central-1`

**Key Principles:**
- ✅ Data sovereignty: Data stays in region of origin
- ✅ No cross-border data transfers without explicit consent
- ✅ End-to-end encryption for all data
- ✅ Regional provider isolation
- ✅ Compliance-first architecture

---

## Regional Architecture

### Infrastructure Overview

```
┌────────────────────────────────────────────────────────────────┐
│                         Global Layer                            │
│  - Global Load Balancer (GeoDNS)                               │
│  - API Gateway (region routing)                                │
│  - Authentication Service (JWT, distributed)                   │
└────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌────────▼────────┐   ┌───────▼────────┐
│   US Region    │   │   EU Region     │   │   RU Region    │
│   us-east-1    │   │  eu-central-1   │   │  ru-central-1  │
├────────────────┤   ├─────────────────┤   ├────────────────┤
│ • AWS          │   │ • AWS Frankfurt │   │ • Yandex Cloud │
│ • PostgreSQL   │   │ • PostgreSQL    │   │ • PostgreSQL   │
│ • S3 Storage   │   │ • S3 Frankfurt  │   │ • Object Store │
│ • OpenAI       │   │ • OpenAI EU     │   │ • YandexGPT    │
│ • Anthropic    │   │ • Anthropic EU  │   │ • GigaChat     │
└────────────────┘   └─────────────────┘   └────────────────┘
```

### Region Selection Logic

```python
def select_region(request):
    """
    Region selection algorithm
    Priority: IP geolocation > User preference > Default
    """
    # 1. Check user's explicit region preference
    if request.headers.get('X-User-Region'):
        return request.headers['X-User-Region']
    
    # 2. Geo-locate by IP
    ip_country = geolocate_ip(request.client.host)
    return map_country_to_region(ip_country)
    
    # 3. Default fallback
    return 'us'
```

---

## Data Residency

### United States (US)

**Location:** AWS US East (Virginia)

| Component | Storage Location | Backup Location |
|-----------|------------------|-----------------|
| User Data | `us-east-1` | `us-west-2` |
| Request Logs | `us-east-1` S3 | `us-west-2` S3 |
| Database | PostgreSQL RDS `us-east-1` | Multi-AZ |
| AI Models | OpenAI US, Anthropic US | N/A |

**Compliance:**
- CCPA (California Consumer Privacy Act)
- SOC 2 Type II
- HIPAA-ready architecture

**Data Transfer:**
- ❌ No automatic transfer to EU/RU
- ✅ Cross-region only with explicit user consent
- ✅ TLS 1.3 for all transfers

---

### European Union (EU)

**Location:** AWS EU Central (Frankfurt)

| Component | Storage Location | Backup Location |
|-----------|------------------|-----------------|
| User Data | `eu-central-1` | `eu-west-1` (Ireland) |
| Request Logs | `eu-central-1` S3 | `eu-west-1` S3 |
| Database | PostgreSQL RDS `eu-central-1` | Multi-AZ |
| AI Models | OpenAI EU, Anthropic EU | N/A |

**Compliance:**
- ✅ **GDPR Articles 44-50** (data transfers)
- ✅ **GDPR Article 32** (security of processing)
- ✅ Standard Contractual Clauses (SCCs)
- ✅ EU-US Data Privacy Framework

**GDPR-Specific Protections:**
```
✅ Right to Access (Art. 15)
✅ Right to Rectification (Art. 16)
✅ Right to Erasure (Art. 17)
✅ Right to Data Portability (Art. 20)
✅ Right to Object (Art. 21)
```

**Data Transfer Rules:**
```yaml
eu_data_transfer:
  to_us: FORBIDDEN (unless explicit consent + SCCs)
  to_ru: FORBIDDEN (GDPR Article 45)
  within_eu: ALLOWED
  anonymized: ALLOWED to any region
```

---

### Russian Federation (RU)

**Location:** Yandex Cloud (Moscow)

| Component | Storage Location | Backup Location |
|-----------|------------------|-----------------|
| User Data | `ru-central-1` | `ru-central-1` Zone B |
| Request Logs | Yandex Object Storage | Same region |
| Database | PostgreSQL `ru-central-1` | Multi-AZ |
| AI Models | YandexGPT, GigaChat | N/A |

**Compliance:**
- ✅ **Federal Law No. 152-FZ** (Personal Data)
- ✅ **Federal Law No. 242-FZ** (Data Localization)
- ✅ FSTEC certification requirements
- ✅ FSB-approved cryptography (GOST)

**Data Localization Requirements:**
```
CRITICAL: All Russian citizen data MUST be stored on Russian territory
- Database: Physical servers in Russia
- Backups: Must stay within Russian borders
- Processing: Primary processing in Russia
- Logs: All logs stored locally
```

**FSB-Approved Encryption:**
- GOST R 34.12-2015 (Kuznyechik) for at-rest encryption
- GOST R 34.10-2012 for digital signatures
- VIPNet or CryptoPro for SORM compliance

---

## Encryption Standards

### At Rest Encryption

| Region | Algorithm | Key Management | Certification |
|--------|-----------|----------------|---------------|
| **US** | AES-256-GCM | AWS KMS | FIPS 140-2 Level 3 |
| **EU** | AES-256-GCM | AWS KMS (Frankfurt) | Common Criteria EAL4+ |
| **RU** | GOST R 34.12-2015 | Yandex KMS + CryptoPro | FSB-certified |

### In Transit Encryption

| Region | Protocol | Cipher Suites | Perfect Forward Secrecy |
|--------|----------|---------------|-------------------------|
| **US** | TLS 1.3 | AES-256-GCM, ChaCha20-Poly1305 | ✅ Yes |
| **EU** | TLS 1.3 | AES-256-GCM, ChaCha20-Poly1305 | ✅ Yes |
| **RU** | TLS 1.3 + VPN | GOST TLS Profile | ✅ Yes |

### Key Rotation Policy

```yaml
key_rotation:
  database_keys:
    frequency: 90 days
    automatic: true
  
  api_keys:
    frequency: 180 days
    user_action: required
  
  encryption_keys:
    us_eu: 365 days (AWS managed)
    ru: 180 days (GOST requirement)
```

### Implementation Example

```python
# src/encryption.py
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

class RegionalEncryption:
    """Region-aware encryption"""
    
    @staticmethod
    def encrypt_data(data: bytes, region: str) -> bytes:
        if region == 'ru':
            # Use GOST encryption
            return encrypt_gost(data)
        else:
            # Use AES-256-GCM
            key = os.urandom(32)
            iv = os.urandom(12)
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            return encryptor.update(data) + encryptor.finalize()
```

---

## Traffic Routing

### Regional Traffic Isolation

**Principle:** Traffic stays within region unless explicitly authorized.

```
┌─────────────────────────────────────────────────────┐
│           Request Flow (Regional Isolation)         │
└─────────────────────────────────────────────────────┘

1. User Request → GeoDNS → Regional Gateway
                             │
                             ├─→ [US] → AWS US East
                             ├─→ [EU] → AWS Frankfurt
                             └─→ [RU] → Yandex Moscow

2. AI Provider Selection (regional):
   US: OpenAI-US, Anthropic-US, Stability-US
   EU: OpenAI-EU, Anthropic-EU
   RU: YandexGPT, GigaChat, Kandinsky

3. Response → Regional Cache → User
```

### Cross-Region Request Policy

```yaml
cross_region_requests:
  us_to_eu: 
    allowed: false
    exception: With explicit user consent + GDPR compliance
  
  us_to_ru:
    allowed: false
    exception: Anonymized data only
  
  eu_to_us:
    allowed: false (GDPR Article 44)
    exception: SCCs + adequacy decision
  
  eu_to_ru:
    allowed: false (GDPR Article 45)
    exception: None (inadequate data protection)
  
  ru_to_any:
    allowed: false (FZ-152)
    exception: Non-personal data only
```

### Implementation

```python
# src/region_router.py
from enum import Enum
from typing import Optional

class Region(str, Enum):
    US = "us"
    EU = "eu"
    RU = "ru"

class RegionRouter:
    ALLOWED_ROUTES = {
        (Region.US, Region.US): True,
        (Region.EU, Region.EU): True,
        (Region.RU, Region.RU): True,
        # Cross-region blocked by default
        (Region.US, Region.EU): False,
        (Region.EU, Region.US): False,
        (Region.RU, Region.US): False,
        (Region.RU, Region.EU): False,
    }
    
    @classmethod
    def can_route(cls, from_region: Region, to_region: Region) -> bool:
        return cls.ALLOWED_ROUTES.get((from_region, to_region), False)
    
    @classmethod
    def enforce_routing(cls, from_region: Region, to_region: Region):
        if not cls.can_route(from_region, to_region):
            raise RoutingViolation(
                f"Data transfer from {from_region} to {to_region} is prohibited"
            )
```

---

## Regional Limits & Quotas

### Rate Limits by Region

| Metric | US | EU | RU |
|--------|----|----|-----|
| **Requests per day** | 10,000 | 8,000 | 5,000 |
| **Requests per hour** | 1,000 | 800 | 500 |
| **Requests per minute** | 60 | 60 | 30 |
| **Concurrent requests** | 50 | 40 | 20 |
| **Max payload size** | 10 MB | 10 MB | 5 MB |

### Storage Quotas

| Region | User Storage | Request Logs | Retention |
|--------|--------------|--------------|-----------|
| **US** | 100 GB | 50 GB | 2 years |
| **EU** | 100 GB | 50 GB | 6 months (GDPR) |
| **RU** | 50 GB | 25 GB | 3 years (FZ-152) |

### Cost Multipliers by Region

```yaml
regional_cost_multipliers:
  us: 1.0x   # Base cost
  eu: 1.2x   # +20% for GDPR compliance overhead
  ru: 1.5x   # +50% for localization requirements
```

---

## Compliance

### US Compliance

**Standards:**
- CCPA (California Consumer Privacy Act)
- SOC 2 Type II
- PCI DSS Level 1 (for payment data)

**User Rights:**
```
✅ Right to know what data is collected
✅ Right to delete personal data
✅ Right to opt-out of data sales (N/A - we don't sell data)
✅ Right to non-discrimination
```

---

### EU Compliance (GDPR)

**Legal Basis for Processing:**
```yaml
processing_basis:
  - Consent (Art. 6(1)(a))
  - Contract performance (Art. 6(1)(b))
  - Legal obligation (Art. 6(1)(c))
  - Legitimate interests (Art. 6(1)(f))
```

**Data Protection Officer (DPO):**
```
Name: [To be assigned]
Email: dpo@oneflow-ai.com
Address: Frankfurt, Germany
```

**Data Processing Agreement (DPA):**
- Available at: `/legal/dpa`
- Includes Standard Contractual Clauses (SCCs)
- GDPR Article 28 compliant

---

### RU Compliance (FZ-152)

**Registration:**
- Roskomnadzor notification: [To be completed]
- FSTEC certification: [In progress]

**Requirements:**
```yaml
fz152_requirements:
  data_localization:
    russian_citizens: MANDATORY (physical servers in Russia)
    foreigners_in_russia: MANDATORY
    foreigners_abroad: OPTIONAL
  
  operator_obligations:
    - Register with Roskomnadzor
    - Implement technical protection measures
    - Conduct regular audits
    - Maintain processing records
```

---

## Data Retention

### Retention Periods by Data Type

| Data Type | US | EU | RU |
|-----------|----|----|-----|
| User accounts | 2 years after deletion | 30 days after deletion request | 3 years |
| Request logs | 2 years | 6 months | 3 years |
| Analytics data | 5 years (anonymized) | 2 years (anonymized) | 5 years |
| Payment records | 7 years | 7 years | 5 years |
| Audit logs | 7 years | 3 years | 5 years |

### Automated Deletion

```python
# Automated data deletion schedule
deletion_schedule = {
    'eu': {
        'user_data': timedelta(days=30),      # After deletion request
        'logs': timedelta(days=180),          # 6 months
        'analytics': timedelta(days=730)      # 2 years (anonymized)
    },
    'us': {
        'user_data': timedelta(days=730),     # 2 years
        'logs': timedelta(days=730),
        'analytics': timedelta(days=1825)     # 5 years
    },
    'ru': {
        'user_data': timedelta(days=1095),    # 3 years
        'logs': timedelta(days=1095),
        'analytics': timedelta(days=1825)
    }
}
```

---

## Incident Response

### Data Breach Notification Timeline

| Region | Notification Deadline | Authority | User Notification |
|--------|----------------------|-----------|-------------------|
| **US** | No federal requirement | State-specific | As required by state law |
| **EU** | **72 hours** | National DPA | Without undue delay |
| **RU** | Immediately | Roskomnadzor, FSB | Within 24 hours |

### Incident Response Team

```
Security Lead: security@oneflow-ai.com
DPO (EU): dpo@oneflow-ai.com
Legal: legal@oneflow-ai.com

24/7 Hotline: +1-XXX-XXX-XXXX
```

### Response Procedure

```yaml
incident_response:
  1_detection:
    - Automated monitoring alerts
    - User reports
    - Third-party notifications
  
  2_containment:
    - Isolate affected systems
    - Preserve evidence
    - Stop data exfiltration
  
  3_notification:
    - EU: 72 hours to DPA
    - RU: Immediate to Roskomnadzor
    - Users: Per regional requirements
  
  4_remediation:
    - Patch vulnerabilities
    - Restore from backups
    - Conduct forensics
  
  5_review:
    - Post-incident report
    - Update security measures
    - Training for staff
```

---

## Contact

**Data Protection Inquiries:**
- General: privacy@oneflow-ai.com
- EU DPO: dpo@oneflow-ai.com
- US CCPA: ccpa@oneflow-ai.com
- RU FZ-152: russia@oneflow-ai.com

**Security Issues:**
- security@oneflow-ai.com
- Bug Bounty: https://oneflow-ai.com/security/bounty

---

**Document Control:**
- Version: 1.0
- Last Review: 2025-10-10
- Next Review: 2026-01-10
- Owner: Chief Security Officer
