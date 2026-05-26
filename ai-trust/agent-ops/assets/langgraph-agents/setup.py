"""
Setup configuration for wx_gov_agent_eval package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "wx_gov_agent_eval_README.md").read_text()

# Read requirements
requirements = []
with open("requirements.txt") as f:
    for line in f:
        line = line.strip()
        # Skip comments and optional dependencies
        if line and not line.startswith("#"):
            # Extract package name without version constraints for setup.py
            requirements.append(line)

setup(
    name="wx_gov_agent_eval",
    version="0.1.0",
    author="IBM",
    author_email="",
    description="Production-ready package for evaluating LangGraph agents using IBM watsonx.governance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ibm-self-serve-assets/building-blocks",
    packages=find_packages(exclude=["tests", "tests.*", "notebooks"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "pandas>=2.2.0",
        "ibm-watsonx-ai>=1.0.0",
        "ibm-watsonx-gov>=1.0.0",
        "ibm-cloud-sdk-core>=3.18.0",
        "langchain>=0.1.0",
        "langchain-core>=0.1.0",
        "langchain-community>=0.0.20",
        "langgraph>=0.0.40",
        "langchain-ibm>=0.1.0",
        "chromadb>=0.4.22",
        "pypdf>=3.17.0",
    ],
    extras_require={
        "web": ["tavily-python>=0.3.0"],
        "dev": [
            "black>=24.0.0",
            "pytest>=8.0.0",
            "mypy>=1.8.0",
            "jupyter>=1.0.0",
            "ipykernel>=6.29.0",
            "ipython>=8.12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            # Add command-line scripts if needed
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
