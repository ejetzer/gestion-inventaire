#!python
# -*- coding: utf-8 -*-
"""
Module utilitaire pour des tâches de laboratoire.

    - `outils` fournis les outils
    - les autres sous-modules sont des applications configurables
    - et des exemples.
"""

import logging  # Communiquer des infos pertinentes pendant l'exécution
import sys  # Accéder à certains aspects du système de l'interpréteur
import pathlib  # Manipuler facilement des chemins

import polygphys.outils.database  # Gérer facilement des bases de données
import polygphys.outils.config  # Gérer facilement des configurations complexes
import polygphys.outils.interface.tkinter.onglets  # Interface rapide

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
