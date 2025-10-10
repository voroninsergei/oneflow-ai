"""
Setup script for OneFlow.AI
Установочный скрипт для OneFlow.AI

This script allows OneFlow.AI to be installed as a package.
Этот скрипт позволяет установить OneFlow.AI как пакет.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_file(filename):
    """Read file contents."""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

# Read requirements
def read_requirements():
    """Read requirements from requirements.txt."""
    requirements = []
    req_file = 'requirements.txt'
    if os.path.exists(req_file):
        with open(req_file, 'r') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
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
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.9',
            'mypy>=0.900',
        ],
    },
    entry_points={
        'console_scripts': [
            'oneflow=cli:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords='ai ml aggregator pricing routing analytics budget',
    project_urls={
        'Documentation': 'https://github.com/yourusername/OneFlow.AI/docs',
        'Source': 'https://github.com/yourusername/OneFlow.AI',
        'Tracker': 'https://github.com/yourusername/OneFlow.AI/issues',
    },
)
