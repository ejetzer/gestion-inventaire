#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Démonstration de l'utilisation des classes de fichiers de configuration.
"""

# Bibliothèque standard
import argparse

from pathlib import Path

# Imports relatifs
from . import FichierConfig

# Configuration pour l'application de ligne de commande
parseur_darguments = argparse.ArgumentParser('Démonstration de FichierConfig.')
parseur_darguments.add_argument('-f',
                                dest='fichier',
                                type=str,
                                help='fichier à lire',
                                required=False,
                                default=str(Path(__file__).parent / 'demo.cfg'))
arguments = parseur_darguments.parse_args()

# Ouvrir un fichier de configuration
fichier = Path(arguments.fichier)
try:
    config = FichierConfig(fichier)

    print(f'Fichier de configuration {fichier!r}')
    print(config)

    # Modifier le contenu du fichier
    config.add_section('test')
    config['test']['sous-test'] = 'valeur test'
    config['test']['autre'] = str(235)

    print('Après modification:')
    print(config)

    # Obtenir une valeur
    print(f'{config["test"]["autre"]=!r}')
    print(f'{config.getint("test", "autre")=!r}')

    # Retrait d'une option
    config.remove_option('test', 'autre')

    print('Retrait d\'une option:')
    print(config)

    # Retrait d'une section
    config.remove_section('test')

    print('Retrait d\'une section:')
    print(config)
finally:
    # Détruire le fichier de démonstration
    fichier.unlink()
