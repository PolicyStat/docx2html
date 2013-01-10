#! /usr/bin/env python
# -*- coding: utf-8 -*-

import codecs

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages  # noqa

long_description = codecs.open("README.md", "r", "utf-8").read()

setup(
    name="docx2html",
    version="0.0.2",
    description="docx (OOXML) to html converter",
    author="Jason Ward",
    author_email="jason.louard.ward@gmail.com",
    url="http://github.com/PolicyStat/docx2html/",
    platforms=["any"],
    license="BSD",
    packages=find_packages(),
    scripts=[],
    zip_safe=False,
    install_requires=['lxml', 'pillow==1.7.7'],
    cmdclass={},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: XML",
    ],
    long_description=long_description,
)
