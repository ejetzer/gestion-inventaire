#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Programme d'inventaire avec base de données.

Created on Mon Nov 15 15:17:28 2021

@author: ejetzer
"""

import logging
import sys
import pathlib

logger = logging.getLogger(__name__)

ch = logging.StreamHandler(sys.stderr)
ch.setLevel(logging.INFO)

fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(fmt)


def main():
    """Exemple des fonctionnalités du module."""
    logger.info('Démonstration du module polytechnique:')

    import polygphys.outils.database
    polygphys.outils.database.logger.addHandler(ch)
    polygphys.outils.database.logger.setLevel(logging.DEBUG)
    fichier_db = str(pathlib.Path(__file__).absolute().parent / 'demo.db')
    base, md = polygphys.outils.database.main(fichier_db)

    import polygphys.outils.config
    polygphys.outils.config.logger.addHandler(ch)
    polygphys.outils.config.logger.setLevel(logging.DEBUG)
    fichier_cfg = pathlib.Path(__file__).absolute().parent / 'base.cfg'

    logger.info(f'{fichier_cfg=}')
    config = polygphys.outils.config.main(fichier_cfg)

    swap_db = config.geturl('bd', 'adresse')
    logger.info(f'{swap_db=}')
    config.set('bd', 'adresse', f'sqlite:///{fichier_db!s}')

    import polygphys.outils.interface.onglets
    polygphys.outils.interface.onglets.logger.addHandler(ch)
    polygphys.outils.interface.onglets.logger.setLevel(logging.DEBUG)
    racine, onglets = polygphys.outils.interface.onglets.main(config, md)

    config.set('bd', 'adresse', swap_db)

    logger.info('Fin.')
