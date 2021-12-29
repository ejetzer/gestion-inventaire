#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Module utilitaire pour des tâches de laboratoire.

    - `outils` fournis les outils
    - les autres sous-modules sont des applications configurables.

Created on Mon Nov 15 15:17:28 2021

@author: ejetzer
"""

import logging
import sys
import pathlib

from .outils.journal import Formats

logger = logging.getLogger(__name__)


def main():
    """Exemple des fonctionnalités du module."""
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)

    fmt = logging.Formatter(Formats().default)
    ch.setFormatter(fmt)

    logger.info('Démonstration du module polytechnique:')

    fichier = pathlib.Path(__file__).expanduser().resolve()

    import polygphys.outils.database
    polygphys.outils.database.logger.addHandler(ch)
    polygphys.outils.database.logger.setLevel(logging.DEBUG)
    fichier_db = str(fichier.parent / 'demo.db')
    base, md = polygphys.outils.database.main(fichier_db)

    import polygphys.outils.config
    polygphys.outils.config.logger.addHandler(ch)
    polygphys.outils.config.logger.setLevel(logging.DEBUG)
    fichier_cfg = fichier / 'base.cfg'
    config = polygphys.outils.config.main(fichier_cfg)

    swap_db = config.geturl('bd', 'adresse')
    config.set('bd', 'adresse', f'sqlite:///{fichier_db!s}')

    import polygphys.outils.interface.onglets
    polygphys.outils.interface.onglets.logger.addHandler(ch)
    polygphys.outils.interface.onglets.logger.setLevel(logging.DEBUG)
    racine, onglets = polygphys.outils.interface.onglets.main(config, md)

    config.set('bd', 'adresse', swap_db)

    logger.info('Fin.')
