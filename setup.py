from setuptools import setup, find_packages
import pathlib

this_directory = pathlib.Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="oneflow-ai",
    version="0.1.0",
    description="Routing and pricing layer for AI providers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="OneFlow.AI",
    license="Proprietary",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    py_modules=[
        "main","router","pricing","wallet","analytics","budget","config","api_keys","cli","database",
        "auth_module","security_middleware","real_api_integration","enhanced_real_api","provider_manager","main_with_db"
    ],
    include_package_data=True,
    install_requires=[r.strip() for r in (this_directory / "requirements.txt").read_text(encoding="utf-8").splitlines() if r.strip() and not r.startswith("#")],
    entry_points={
        "console_scripts": [
            "oneflow=cli:main"
        ]
    },
    python_requires=">=3.10",
)
