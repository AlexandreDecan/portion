# To use a consistent encoding
from codecs import open
from os import path

from setuptools import find_packages, setup

import intervals

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=intervals.__name__,

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=intervals.__version__,

    description=intervals.__description__,
    long_description=long_description,
    long_description_content_type='text/markdown',

    # The project's main homepage.
    url=intervals.__url__,

    # Author details
    author=intervals.__author__,
    author_email=intervals.__author_email__,

    # Choose your license
    license=intervals.__licence__,

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',

        'Topic :: Scientific/Engineering :: Mathematics',

        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',

        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',

    ],

    # What does your project relate to?
    keywords='interval arithmetic math',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    #packages=find_packages(exclude=['tests']),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    py_modules=['intervals'],

    python_requires='>=3.4',

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[],
    tests_require=[
          'pytest',
    ],
    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        #'dev': ['check-manifest'],
    },

    include_package_data=True,
    zip_safe=True,
)
