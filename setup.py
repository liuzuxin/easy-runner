#!/usr/bin/env python3 -*- coding: utf-8 -*-

import os

from setuptools import find_packages, setup


def get_version() -> str:
    # https://packaging.python.org/guides/single-sourcing-package-version/
    init = open(os.path.join("easy_runner", "__init__.py"), "r").read().split()
    return init[init.index("__version__") + 2][1:-1]


def get_install_requires() -> str:
    return [
        "prettytable~=3.7.0",
        "psutil~=5.9.5",
    ]


setup(
    name="easy_runner",
    version=get_version(),
    description=  # noqa
    "A lightweight tool for managing and executing multiple parallel experiments.",  # noqa
    long_description=open("README.md", encoding="utf8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/liuzuxin/easy-runner",
    author="Zuxin Liu",
    author_email="zuxin1997@gmail.com",
    license="MIT",
    python_requires=">=3.6",
    classifiers=[
        # How mature is this project? Common values are 3 - Alpha 4 - Beta 5 -
        #   Production/Stable
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: MIT License",
        # Specify the Python versions you support here. In particular, ensure that you
        # indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="reinforcement learning platform pytorch",
    packages=find_packages(
        exclude=["tests", "tests.*", "examples", "examples.*", "docs", "docs.*"]
    ),
    install_requires=get_install_requires(),
)
