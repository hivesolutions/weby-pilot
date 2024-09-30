#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import setuptools

setuptools.setup(
    name="weby-pilot",
    version="0.1.4",
    author="Hive Solutions Lda.",
    author_email="development@hive.pt",
    description="Weby Pilot",
    license="Apache License, Version 2.0",
    keywords="weby automation pilot",
    url="http://weby-pilot.hive.pt",
    zip_safe=False,
    packages=["weby_pilot"],
    package_dir={"": os.path.normpath("src")},
    install_requires=["selenium"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    long_description=open(os.path.join(os.path.dirname(__file__), "README.md"), "rb")
    .read()
    .decode("utf-8"),
    long_description_content_type="text/markdown",
)
