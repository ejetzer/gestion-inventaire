#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Exemple d'inventaire.

Créé le Thu Dec 16 13:37:19 2021

@author: ejetzer
"""

import logging

from . import main

from polygphys.outils.journal import Formats

if __name__ == '__main__':
    logging.basicConfig(format=Formats().default, level=logging.WARNING)
    main()
