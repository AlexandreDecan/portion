from os import path
from setuptools import setup
from codecs import open

import intervals

with open(path.join(path.abspath(path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=intervals.__package__,
    version=intervals.__version__,
    license=intervals.__licence__,

    author=intervals.__author__,
    url=intervals.__url__,

    description=intervals.__description__,
    long_description=long_description,
    long_description_content_type='text/markdown',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',

        'Topic :: Scientific/Engineering :: Mathematics',

        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='interval arithmetic range math',

    py_modules=['intervals'],
    tests_require=['pytest'],
    zip_safe=True,
)
