# coding: utf-8
from __future__ import unicode_literals

import codecs
import os

from setuptools import find_packages, setup

rf = codecs.open(os.path.join(os.path.dirname(__file__), "README.txt"), "r")
with rf as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="nsre",
    version="0.1.0",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    license="WTFPL",
    description="Non-String Regular Expressions, making RegExps more abstract",
    long_description=README,
    url="https://github.com/Xowap/nsre",
    author="Rémy Sanchez",
    author_email="remy.sanchez@hyperthese.net",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
