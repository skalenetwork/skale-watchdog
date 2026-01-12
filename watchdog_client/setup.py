#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import (
    find_packages,
    setup,
)

setup(
    name='skale-watchdog-client',
    version='1.2',
    description='SKALE Watchdog Client - SKALE and FAIR Nodes Health Checks',
    author='SKALE Labs',
    author_email='support@skalelabs.com',
    url='https://github.com/skalenetwork/skale-watchdog',
    license='AGPL-3.0-or-later',
    license_files=['LICENSE'],
    include_package_data=True,
    install_requires=[
        'requests>=2.31.0',
    ],
    extras_require={
        'dev': [
            'twine>=5.0.0,<7',
            'build>=1.2.1',
        ],
    },
    python_requires='>=3.13,<4',
    keywords='skale',
    packages=find_packages(exclude=['tests']),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.13',
    ],
)
