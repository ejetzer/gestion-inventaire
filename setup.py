#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Programme ou module pour ...

Créé le Thu Dec 16 12:40:56 2021

@author: ejetzer
"""

import sys

from setuptools import setup

if sys.platform.startswith('win'):
    setup_requires = ['py2exe']
elif sys.platform == 'darwin':
    setup_requires = ['py2app']

setup(setup_requires=setup_requires)
