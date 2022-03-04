#!python
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

import polygphys.outils.database
import polygphys.outils.config
import polygphys.outils.interface.tkinter.onglets

from .outils.journal import Formats


def main(dossier=None):
    """Exemple des fonctionnalités du module."""
    logging.basicConfig(format=Formats().détails, level=logging.DEBUG)

    logging.info('Démonstration du module polytechnique:')

    if dossier is None:
        if len(sys.argv) > 1:
            dossier = pathlib.Path(sys.argv[1]).resolve()
        else:
            fichier = pathlib.Path(__file__).expanduser().resolve()
            dossier = fichier.parent

    base, md = polygphys.outils.database.main(dossier)
    config = polygphys.outils.config.main(dossier)

    fichier_db = str(dossier / 'demo.db')
    swap_db = config.get('bd', 'adresse')
    config.set('bd', 'adresse', f'sqlite:///{fichier_db!s}')

    racine, onglets = polygphys.outils.interface.tkinter.onglets.main(
        config, md)

    config.set('bd', 'adresse', swap_db)

    logging.info('Fin.')
