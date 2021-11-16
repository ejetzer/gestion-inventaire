#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='polytechnique',
      version='1.0',
      description='Outils de gestion d\'inventaire',
      author='Émile Jetzer',
      author_email='emile.jetzer@polymtl.ca',
      url=None,
      packages=['polytechnique', 'polytechnique.outils'],
      package_dir={'polytechnique': 'polytechnique/',
                   'polytechnique.outils': 'polytechnique/outils/'},
      package_data={'polytechnique': ['polytechnique/*.config',
                                      'polytechnique/*.md']})
