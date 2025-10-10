"""
OneFlow.AI Main Module - Complete Integration
Главный модуль OneFlow.AI - Полная интеграция

Complete implementation with optional database support.
Полная реализация с опциональной поддержкой базы данных.
"""

from typing import Optional, Dict, Any, List
import sys
import os

# Core components
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from wallet import Wallet
from pricing import PricingCalculator
from router import Router

# Extended components
try:
    from analytics import Analytics
    HAS_ANALYTICS = True
except ImportError:
    HAS_ANALYTICS = False
    print("Warning: Analytics module not available")

try:
    from budget import Budget, BudgetPeriod
    HAS_BUDGET = True
except ImportError:
    HAS_BUDGET = False
    print("Warning: Budget module not available")

try:
    from config import Config
    HAS_CONFIG = True
except ImportError:
    HAS_CONFIG = False
    print("Warning: Config module not available")

try:
    from database import get_db_manager
    HAS_DATABASE = True
except ImportError:
    HAS_DATABASE = False

# Providers
from providers.gpt_provider import GPTProvider
from providers.image_provider import ImageProvider
from providers.audio_provider import AudioProvider
from providers.video_provider import VideoProvider
