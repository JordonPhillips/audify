#!/usr/bin/env python
from setuptools import setup, find_packages

with open("README.md") as f:
    README = f.read()

setup(
    name="audify",
    version="0.1.0",
    description=("A simple command line tool to transform text to speech with AWS."),
    long_description=README,
    long_description_content_type="text/markdown",
    author="Jordon Phillips",
    author_email="pypi@jkphillips.me",
    license="MIT",
    packages=find_packages(exclude=["tests"]),
    url="https://github.com/JordonPhillips/audify",
    install_requires=[
        "boto3>=1.9.75<2.0.0",
        "pydub>=0.23.0,<1.0.0",
        "tqdm>=4.37.0,<5.0.0",
    ],
    python_requires="~=3.8",
    keywords="aws polly tts",
    entry_points={"console_scripts": ["audify = audify:main"]},
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.8",
    ],
)
