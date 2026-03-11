#!/usr/bin/env python
from setuptools import (
    find_packages,
    setup,
)

extras_require = {}

with open("./README.md") as readme:
    long_description = readme.read()


setup(
    name="w3connect",
    version="0.3.2",
    description="""w3connect: AI-native crypto key lockbox for chat based AI agent such as OpenClaw or Nanobot""",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="MMT",
    url="https://github.com/ModernMagicTechnology/w3connect",
    include_package_data=True,
    install_requires=[
        "web3>=6.0.0",
        "tornado>=6.0.0",
        "pyotp>=2.9.0",
        "qrcode>=8.2",
    ],
    python_requires=">=3.8, <4",
    extras_require=extras_require,
    py_modules=["w3connect"],
    license="MIT",
    zip_safe=False,
    keywords="ethereum",
    packages=find_packages(exclude=["scripts", "scripts.*", "tests", "tests.*"]),
)