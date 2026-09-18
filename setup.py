"""CIEL Package Setup Configuration."""

# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀
# reze ma queen 🥀

import os
from setuptools import setup, find_packages


def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8") as f:
            return [
                line.strip()
                for line in f
                if line.strip() and not line.startswith("#")
            ]
    return []


setup(
    name="ciel-agent",
    version="1.0.0",
    description="CIEL: Autonomous Windows 11 Desktop Agent with Sub-50ms Fast-Path Execution",
    author="aaditya079",
    packages=find_packages(exclude=["tests*", "research*", "scratch*"]),
    py_modules=["main"],
    install_requires=read_requirements(),
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "ciel=main:main",
            "ceil=main:main",
        ],
    },
    license="MIT",
    classifiers=[
        "Operating System :: Microsoft :: Windows :: Windows 11",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
