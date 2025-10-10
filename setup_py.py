"""
Setup script for OneFlow.AI
Установочный скрипт для OneFlow.AI
"""

from setuptools import setup, find_packages
import os

def read_file(filename):
    """Read file contents."""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

def read_requirements():
    """Read requirements from requirements.txt."""
    requirements = []
    req_file = 'requirements.txt'
    if os.path.exists(req_file):
        with open(req_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line)
    return requirements

setup(
    name='oneflow-ai',
    version='2.0.0',
    author='Sergey Voronin',
    author_email='voroninsergeiai@gmail.com',
    description='AI Model Aggregator with pricing, routing, and analytics',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/voroninsergeiai/OneFlow.AI',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=4.1.0',
            'black>=23.0.0',
            'flake8>=6.1.0',
            'mypy>=1.6.0',
        ],
        'api': [
            'openai>=1.0.0',
            'anthropic>=0.5.0',
            'requests>=2.31.0',
        ],
        'web': [
            'fastapi>=0.104.0',
            'uvicorn[standard]>=0.24.0',
        ],
        'db': [
            'sqlalchemy>=2.0.0',
            'psycopg2-binary>=2.9.9',
        ],
        'auth': [
            'PyJWT>=2.8.0',
            'passlib[bcrypt]>=1.7.4',
            'python-multipart>=0.0.6',
        ],
    },
    entry_points={
        'console_scripts': [
            'oneflow=cli:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords='ai ml aggregator pricing routing analytics budget authentication',
    project_urls={
        'Documentation': 'https://github.com/voroninsergeiai/OneFlow.AI/docs',
        'Source': 'https://github.com/voroninsergeiai/OneFlow.AI',
        'Tracker': 'https://github.com/voroninsergeiai/OneFlow.AI/issues',
    },
)
