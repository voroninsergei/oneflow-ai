"""
OneFlow.AI - Multi-provider AI orchestration platform.
Платформа оркестрации мультипровайдерных AI сервисов.
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("oneflow-ai")
except PackageNotFoundError:
    __version__ = "0.0.0.dev0"

__all__ = [
    "__version__",
]
