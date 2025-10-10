"""
Setup configuration for OneFlow.AI
Package for distribution on PyPI
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, "r", encoding="utf-8") as f:
        requirements = [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith("#")
        ]

# Version
VERSION = "2.0.0"

setup(
    # ========================================================================
    # Basic Information
    # ========================================================================
    name="oneflow-ai",
    version=VERSION,
    author="Sergey Voronin",
    author_email="voroninsergeiai@gmail.com",
    
    # ========================================================================
    # Description
    # ========================================================================
    description="AI Model Aggregator with Pricing, Routing, Analytics & Authentication",
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    # ========================================================================
    # URLs
    # ========================================================================
    url="https://github.com/voroninsergei/oneflow-ai",
    project_urls={
        "Bug Tracker": "https://github.com/voroninsergei/oneflow-ai/issues",
        "Documentation": "https://github.com/voroninsergei/oneflow-ai/tree/main/docs",
        "Source Code": "https://github.com/voroninsergei/oneflow-ai",
        "Changelog": "https://github.com/voroninsergei/oneflow-ai/blob/main/CHANGELOG.md",
    },
    
    # ========================================================================
    # Package Configuration
    # ========================================================================
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # Include additional files
    include_package_data=True,
    package_data={
        "": ["*.json", "*.yaml", "*.yml", "*.md"],
    },
    
    # ========================================================================
    # Python Version
    # ========================================================================
    python_requires=">=3.9",
    
    # ========================================================================
    # Dependencies
    # ========================================================================
    install_requires=[
        # Core dependencies
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.0.0",
        
        # Database
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",  # PostgreSQL
        
        # Authentication
        "PyJWT>=2.8.0",
        "passlib[bcrypt]>=1.7.4",
        "python-multipart>=0.0.6",
        
        # HTTP & Utils
        "httpx>=0.25.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    
    # ========================================================================
    # Optional Dependencies
    # ========================================================================
    extras_require={
        # Development tools
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
            "pre-commit>=3.5.0",
        ],
        
        # API providers
        "api": [
            "openai>=1.0.0",
            "anthropic>=0.7.0",
            "stability-sdk>=0.8.0",
            "elevenlabs>=0.2.0",
        ],
        
        # Web server enhancements
        "web": [
            "aiofiles>=23.2.0",
            "jinja2>=3.1.0",
            "python-multipart>=0.0.6",
        ],
        
        # Database extras
        "db": [
            "alembic>=1.12.0",  # Database migrations
            "asyncpg>=0.29.0",   # Async PostgreSQL
        ],
        
        # Monitoring & Observability
        "monitoring": [
            "prometheus-client>=0.19.0",
            "opentelemetry-api>=1.21.0",
            "opentelemetry-sdk>=1.21.0",
        ],
        
        # Regional compliance
        "compliance": [
            "cryptography>=41.0.0",
        ],
        
        # Full installation (all extras)
        "all": [
            # Combines all extras above
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "openai>=1.0.0",
            "anthropic>=0.7.0",
            "alembic>=1.12.0",
            "prometheus-client>=0.19.0",
            "cryptography>=41.0.0",
        ],
    },
    
    # ========================================================================
    # Entry Points
    # ========================================================================
    entry_points={
        "console_scripts": [
            "oneflow-ai=src.cli:main",
            "oneflow-server=web_server:main",
        ],
    },
    
    # ========================================================================
    # Classification
    # ========================================================================
    classifiers=[
        # Development Status
        "Development Status :: 4 - Beta",
        
        # Intended Audience
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Information Technology",
        
        # Topics
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        
        # License
        "License :: Other/Proprietary License",
        
        # Programming Language
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        
        # Operating System
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        
        # Framework
        "Framework :: FastAPI",
        
        # Typing
        "Typing :: Typed",
    ],
    
    # ========================================================================
    # Keywords
    # ========================================================================
    keywords=[
        "ai",
        "artificial-intelligence",
        "machine-learning",
        "gpt",
        "openai",
        "anthropic",
        "api-aggregator",
        "pricing",
        "routing",
        "analytics",
        "fastapi",
        "multi-region",
        "compliance",
        "gdpr",
    ],
    
    # ========================================================================
    # Additional Metadata
    # ========================================================================
    zip_safe=False,
    platforms=["any"],
    
    # License
    license="Proprietary",
    license_files=["LICENSE"],
)
