#!/usr/bin/env python

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# Read version info from figura/version.py
version_vars = {}
with open("figura/version.py") as fp:
    exec(fp.read(), version_vars)
version_string = version_vars['__version_string__']

setup(
    name='figura',
    version=version_string,

    description='A python package for parsing and working with Figura config files',
    long_description=long_description,
    url='https://github.com/shx2/figura',
    author='shx2',
    author_email='shx222@gmail.com',
    license='MIT',

    packages=find_packages(exclude=['tests*', 'figura.tests*']),
    platforms = ["POSIX", "Windows"],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'figura_print=figura.tools.figura_print:main',
        ],
    },

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Code Generators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
    ],
    keywords='config, configuration, object oriented, code generation',

)
