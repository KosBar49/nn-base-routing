"""
Setup configuration for IoT Network Routing package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    """Read the README.md file for long description."""
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements(filename):
    """Read requirements from file."""
    with open(filename, "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="iot-network-routing",
    version="1.0.0",
    author="IoT Network Team",
    author_email="team@iot-network.dev",
    description="IoT Network Routing Visualization and Analysis Framework",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/iot-team/iot-network-routing",
    project_urls={
        "Bug Tracker": "https://github.com/iot-team/iot-network-routing/issues",
        "Documentation": "https://iot-network-routing.readthedocs.io/",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: System :: Networking",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "isort>=5.10.0",
            "mypy>=0.991",
        ],
        "web": [
            "flask>=2.0.0",
        ],
        "visualization": [
            "matplotlib>=3.5.0",
            "seaborn>=0.11.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "iot-network-cli=iot_network_routing.cli.main:main",
            "iot-network-web=iot_network_routing.web.run:main",
        ],
    },
    include_package_data=True,
    package_data={
        "iot_network_routing": [
            "web/templates/*.html",
            "web/static/css/*.css",
            "web/static/js/*.js",
        ],
    },
    zip_safe=False,
)
