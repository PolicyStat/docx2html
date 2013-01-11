#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages  # noqa

rel_file = lambda *args: os.path.join(
        os.path.dirname(os.path.abspath(__file__)), *args)


def get_readme():
    return open(rel_file('README.md')).read()

setup(
    name="docx2html",
    version="0.0.7",
    description="docx (OOXML) to html converter",
    author="Jason Ward",
    author_email="jason.louard.ward@gmail.com",
    url="http://github.com/PolicyStat/docx2html/",
    platforms=["any"],
    license="BSD",
    packages=find_packages(),
    scripts=[],
    zip_safe=False,
    install_requires=['lxml==2.2.4', 'pillow==1.7.7'],
    tests_require=['nose'],
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
    long_description=get_readme(),
)
