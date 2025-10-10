"""
Regional Data Management Module
Handles multi-region data residency, routing, and compliance
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Region Definitions
# ============================================================================

class Region(str, Enum):
    """Supported regions"""
    US = "us"
    EU = "eu"
    RU = "ru"


class ComplianceFramework(str, Enum):
    """Compliance frameworks by region"""
    CCPA = "ccpa"          # California/US
    GDPR = "gdpr"          # EU
    FZ152 = "fz152"        # Russia
    SOC2 = "soc2"          # US
    FSTEC = "fstec"        # Russia


# ============================================================================
# Regional Configuration
# ============================================================================

@dataclass
class RegionConfig:
    """Configuration for a specific region"""
    region: Region
    name: str
    db_host: str
    storage_endpoint: str
    encryption_algorithm: str
    providers: List[str]
    compliance_frameworks: List[ComplianceFramework]
    
    # Rate limits
    daily_limit: int
    hourly_limit: int
    minute_limit: int
    concurrent_limit: int
    
    # Storage quotas
    user_storage_gb: int
    log_storage_gb: int
    
    # Data retention (in days)
    user_data_retention_days: int
    log_retention_days: int
    analytics_retention_days: int
    
    # Cost multiplier
    cost_multiplier: float
    
    # Feature flags
    gdpr_compliant: bool = False
    data_localization_required: bool = False
    cross_border_transfer_allowed: bool = False


# ============================================================================
# Regional Configurations
# ============================================================================

REGION_CONFIGS: Dict[Region, RegionConfig] = {
    Region.US: RegionConfig(
        region=Region.US,
        name="United States",
        db_host="us-postgres.amazonaws.com",
        storage_endpoint="s3://oneflow-us",
        encryption_algorithm="AES-256-GCM",
        providers=["openai", "anthropic", "stability", "elevenlabs"],
        compliance_frameworks=[ComplianceFramework.CCPA, ComplianceFramework.SOC2],
        daily_limit=10000,
        hourly_limit=1000,
        minute_limit=60,
        concurrent_limit=50,
        user_storage_gb=100,
        log_storage_gb=50,
        user_data_retention_days=730,      # 2 years
        log_retention_days=730,            # 2 years
        analytics_retention_days=1825,     # 5 years
        cost_multiplier=1.0,
        cross_border_transfer_allowed=False
    ),
    
    Region.EU: RegionConfig(
        region=Region.EU,
        name="European Union",
        db_host="eu-postgres.amazonaws.com",
        storage_endpoint="s3://oneflow-eu",
        encryption_algorithm="AES-256-GCM",
        providers=["openai-eu", "anthropic-eu"],
        compliance_frameworks=[ComplianceFramework.GDPR],
        daily_limit=8000,
        hourly_limit=800,
        minute_limit=60,
        concurrent_limit=40,
        user_storage_gb=100,
        log_storage_gb=50,
        user_data_retention_days=30,       # 30 days after deletion request (GDPR)
        log_retention_days=180,            # 6 months (GDPR)
        analytics_retention_days=730,      # 2 years (anonymized)
        cost_multiplier=1.2,               # +20% for GDPR overhead
        gdpr_compliant=True,
        cross_border_transfer_allowed=False
    ),
    
    Region.RU: RegionConfig(
        region=Region.RU,
        name="Russian Federation",
        db_host="ru-postgres.yandexcloud.net",
        storage_endpoint="s3://oneflow-ru",
        encryption_algorithm="GOST-R-34.12-2015",
        providers=["yandexgpt", "gigachat", "kandinsky"],
        compliance_frameworks=[ComplianceFramework.FZ152, ComplianceFramework.FSTEC],
        daily_limit=5000,
        hourly_limit=500,
        minute_limit=30,
        concurrent_limit=20,
        user_storage_gb=50,
        log_storage_gb=25,
        user_data_retention_days=1095,     # 3 years (FZ-152)
        log_retention_days=1095,           # 3 years
        analytics_retention_days=1825,     # 5 years
        cost_multiplier=1.5,               # +50% for localization
        data_localization_required=True,
        cross_border_transfer_allowed=False
    )
}


# ============================================================================
# Region Manager
# ============================================================================

class RegionManager:
    """Manages regional data operations and compliance"""
    
    def __init__(self):
        self.configs = REGION_CONFIGS
        self._routing_cache = {}
    
    def get_config(self, region: Region) -> RegionConfig:
        """Get configuration for a specific region"""
        config = self.configs.get(region)
        if not config:
            raise ValueError(f"Unknown region: {region}")
        return config
    
    def select_region_by_ip(self, ip_address: str) -> Region:
        """
        Select region based on IP geolocation
        
        In production, use a real geolocation service:
        - MaxMind GeoIP2
        - IP2Location
        - ipinfo.io
        """
        # TODO: Implement real IP geolocation
        # For now, return US as default
        logger.info(f"Geolocating IP: {ip_address}")
        return Region.US
    
    def select_region(
        self,
        user_preference: Optional[str] = None,
        ip_address: Optional[str] = None,
        default: Region = Region.US
    ) -> Region:
        """
        Select appropriate region for user
        
        Priority:
        1. User's explicit preference
        2. IP geolocation
        3. Default region
        """
        # 1. Check user preference
        if user_preference:
            try:
                return Region(user_preference.lower())
            except ValueError:
                logger.warning(f"Invalid user region preference: {user_preference}")
        
        # 2. Geolocate by IP
        if ip_address:
            return self.select_region_by_ip(ip_address)
        
        # 3. Default
        return default
    
    def can_transfer_data(
        self,
        from_region: Region,
        to_region: Region,
        has_user_consent: bool = False
    ) -> bool:
        """
        Check if data transfer between regions is allowed
        
        Rules:
        - Same region: Always allowed
        - Cross-region: Generally forbidden
        - Exceptions: With explicit consent and compliance
        """
        # Same region always allowed
        if from_region == to_region:
            return True
        
        # Check source region config
        from_config = self.get_config(from_region)
        
        # GDPR: No transfers to non-adequate countries
        if from_config.gdpr_compliant:
            if to_region == Region.RU:
                # EU -> RU blocked (inadequate data protection)
                return False
            if to_region == Region.US and not has_user_consent:
                # EU -> US requires consent + SCCs
                return False
        
        # FZ-152: Data localization required
        if from_config.data_localization_required:
            # Russian data cannot leave Russia
            return False
        
        # Check if cross-border transfers enabled
        if not from_config.cross_border_transfer_allowed:
            return False
        
        return has_user_consent
    
    def enforce_data_transfer(
        self,
        from_region: Region,
        to_region: Region,
        has_user_consent: bool = False
    ):
        """
        Enforce data transfer policy (raises exception if not allowed)
        """
        if not self.can_transfer_data(from_region, to_region, has_user_consent):
            raise DataTransferViolation(
                f"Data transfer from {from_region.value} to {to_region.value} "
                f"is prohibited by data governance policy"
            )
    
    def get_providers_for_region(self, region: Region) -> List[str]:
        """Get list of AI providers available in region"""
        config = self.get_config(region)
        return config.providers
    
    def calculate_cost(self, base_cost: float, region: Region) -> float:
        """Calculate cost with regional multiplier"""
        config = self.get_config(region)
        return base_cost * config.cost_multiplier
    
    def check_rate_limit(
        self,
        region: Region,
        user_id: str,
        period: str = "minute"
    ) -> bool:
        """
        Check if user has exceeded rate limit
        
        Args:
            region: User's region
            user_id: User identifier
            period: Time period (minute, hour, day)
        
        Returns:
            True if within limits, False if exceeded
        """
        config = self.get_config(region)
        
        # TODO: Implement real rate limiting with Redis
        # This is a placeholder
        limits = {
            "minute": config.minute_limit,
            "hour": config.hourly_limit,
            "day": config.daily_limit
        }
        
        limit = limits.get(period, config.minute_limit)
        logger.info(f"Rate limit check: {user_id} in {region.value}, limit: {limit}")
        
        return True  # Placeholder
    
    def get_data_retention_period(
        self,
        region: Region,
        data_type: str = "user_data"
    ) -> timedelta:
        """Get data retention period for region and data type"""
        config = self.get_config(region)
        
        retention_map = {
            "user_data": config.user_data_retention_days,
            "logs": config.log_retention_days,
            "analytics": config.analytics_retention_days
        }
        
        days = retention_map.get(data_type, config.user_data_retention_days)
        return timedelta(days=days)
    
    def should_delete_data(
        self,
        region: Region,
        data_type: str,
        created_at: datetime
    ) -> bool:
        """Check if data should be deleted based on retention policy"""
        retention_period = self.get_data_retention_period(region, data_type)
        age = datetime.utcnow() - created_at
        return age > retention_period
    
    def validate_compliance(self, region: Region, operation: str) -> Dict[str, Any]:
        """
        Validate if operation complies with regional requirements
        
        Returns compliance check result with details
        """
        config = self.get_config(region)
        
        result = {
            "region": region.value,
            "operation": operation,
            "compliant": True,
            "frameworks": [f.value for f in config.compliance_frameworks],
            "requirements": []
        }
        
        # GDPR checks
        if ComplianceFramework.GDPR in config.compliance_frameworks:
            result["requirements"].extend([
                "User consent required",
                "Right to erasure must be honored",
                "Data minimization principle applies",
                "Purpose limitation applies"
            ])
        
        # FZ-152 checks
        if ComplianceFramework.FZ152 in config.compliance_frameworks:
            result["requirements"].extend([
                "Data must stay in Russia",
                "Roskomnadzor registration required",
                "GOST encryption mandatory"
            ])
        
        return result


# ============================================================================
# Custom Exceptions
# ============================================================================

class DataTransferViolation(Exception):
    """Raised when data transfer violates regional policy"""
    pass


class RegionNotSupported(Exception):
    """Raised when region is not supported"""
    pass


class ComplianceViolation(Exception):
    """Raised when operation violates compliance requirements"""
    pass


# ============================================================================
# Encryption Handler
# ============================================================================

class RegionalEncryption:
    """Handles encryption based on regional requirements"""
    
    @staticmethod
    def get_encryption_algorithm(region: Region) -> str:
        """Get encryption algorithm for region"""
        config = REGION_CONFIGS[region]
        return config.encryption_algorithm
    
    @staticmethod
    def encrypt_data(data: bytes, region: Region) -> bytes:
        """
        Encrypt data according to regional standards
        
        US/EU: AES-256-GCM
        RU: GOST R 34.12-2015
        """
        algorithm = RegionalEncryption.get_encryption_algorithm(region)
        
        if algorithm == "GOST-R-34.12-2015":
            # TODO: Implement GOST encryption
            logger.info("Using GOST encryption for Russian data")
            return data  # Placeholder
        else:
            # Use AES-256-GCM for US/EU
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.backends import default_backend
            import os
            
            key = os.urandom(32)  # 256-bit key
            iv = os.urandom(12)   # 96-bit IV for GCM
            
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv),
                backend=default_backend()
            )
            
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(data) + encryptor.finalize()
            
            # In production, store key in KMS
            return ciphertext
    
    @staticmethod
    def decrypt_data(ciphertext: bytes, region: Region, key: bytes, iv: bytes) -> bytes:
        """Decrypt data according to regional standards"""
        algorithm = RegionalEncryption.get_encryption_algorithm(region)
        
        if algorithm == "GOST-R-34.12-2015":
            # TODO: Implement GOST decryption
            return ciphertext  # Placeholder
        else:
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.backends import default_backend
            
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv),
                backend=default_backend()
            )
            
            decryptor = cipher.decryptor()
            return decryptor.update(ciphertext) + decryptor.finalize()


# ============================================================================
# Usage Examples
# ============================================================================

if __name__ == "__main__":
    # Initialize region manager
    rm = RegionManager()
    
    # Example 1: Select region for user
    user_region = rm.select_region(
        user_preference="eu",
        ip_address="203.0.113.0"
    )
    print(f"Selected region: {user_region}")
    
    # Example 2: Check data transfer
    try:
        rm.enforce_data_transfer(
            from_region=Region.EU,
            to_region=Region.RU,
            has_user_consent=False
        )
    except DataTransferViolation as e:
        print(f"Transfer blocked: {e}")
    
    # Example 3: Get providers for region
    providers = rm.get_providers_for_region(Region.RU)
    print(f"RU providers: {providers}")
    
    # Example 4: Calculate regional cost
    base_cost = 10.0
    eu_cost = rm.calculate_cost(base_cost, Region.EU)
    print(f"EU cost (with 20% multiplier): ${eu_cost}")
    
    # Example 5: Check compliance
    compliance = rm.validate_compliance(Region.EU, "store_user_data")
    print(f"Compliance check: {compliance}")
    
    # Example 6: Check data retention
    old_date = datetime(2020, 1, 1)
    should_delete = rm.should_delete_data(Region.EU, "logs", old_date)
    print(f"Should delete old EU logs: {should_delete}")
