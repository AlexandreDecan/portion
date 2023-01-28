from os import path
from setuptools import setup, find_packages
from codecs import open

with open(
    path.join(path.abspath(path.dirname(__file__)), "README.md"), encoding="utf-8"
) as f:
    long_description = f.read()

setup(
    name="portion",
    version="2.3.1",
    license="LGPLv3",
    author="Alexandre Decan",
    url="https://github.com/AlexandreDecan/portion",
    description="Python data structure and operations for intervals",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="interval operation range math",
    packages=find_packages(include=["portion"]),
    python_requires="~= 3.7",
    install_requires=[
        "sortedcontainers ~= 2.2",
    ],
    extras_require={
        "test": ["pytest ~= 7.0", "coverage ~= 6.0", "black >= 21.8b"],
    },
    zip_safe=True,
)
