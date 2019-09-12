#!/usr/bin/env python3
from setuptools import setup, find_packages
import sys

VERSION = '0.1'
DESCRIPTION = 'Python import/export data in tecplot format'

with open('README.md') as f:
    LONG_DESCRIPTION = ''.join(f.readlines())

if sys.version_info[:2] < (3, 5):
    raise RuntimeError("Python version >= 3.5 required.")

setup(
    version=VERSION,
    name='py2tec',
    author='luohancfd',
    author_email='han.luo@gmail.com',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/luohancfd/py2tec",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)'
    ],
    license="GPLv3+",
    keywords=["Tecplot"],
    platforms=["Windows", "Linux", "Solaris", "Mac OS-X", "Unix"],
    python_requires='>=3.5',
    install_requires=['numpy'],
    packages=find_packages(exclude=["contrib", "docs", "tests*"])
)
