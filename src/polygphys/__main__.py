# -*- coding: utf-8 -*-
"""Exemple d'utilisation du module polygphys."""

# Bibliothèques standard
import argparse

from pathlib import Path

# Bibliothèques via PIPy
from sqlalchemy import MetaData
from pandas import DataFrame, Index

# Imports relatifs
from . import DemoConfig
from .outils.database.modeles import créer_dbs
from .outils.database import BaseDeDonnées, BaseTableau

# Arguments en ligne de commande
parseur_darguments = argparse.ArgumentParser()
parseur_darguments.add_argument('-f',
                                dest='fichier',
                                type=str,
                                help='fichier à lire',
                                required=False,
                                default='demo.cfg')
arguments = parseur_darguments.parse_args()

# Démo: charger un fichier de configuration
fichier_config = Path(arguments.fichier)
try:
    config = DemoConfig(arguments.fichier)  # Fichier de configuration

    # Démo: se connecter à une base de données
    md = créer_dbs(MetaData())  # Structure de la base de données

    # Aller chercher des valeurs dans le fichier de configuration
    fichier_db = config.getpath('bd', 'adresse')
    protocole = config['bd']['protocole']
    if not fichier_db.exists():
        fichier_db.touch()

    try:
        # Se connecter à la base de données
        base = BaseDeDonnées(f'{protocole}:///{fichier_db}', md)
        base.réinitialiser()  # Réinitialiser la structure

        # Démo: Obtenir une table de données
        print('Tableau \'personnes\'')
        df = base.select('personnes')  # Obtenir le tableau 'personnes'
        print(df.head())
        print()

        # Démo: Ajouter des entrées à une table de données
        # Créer les données à ajouter
        idx = Index([0, 1, 2], name='index')
        df = DataFrame({'matricule': ['p0000000', 'p0000001', 'p00000002'],
                        'nom': ['Seth', 'Anu', 'Hor'],
                        'prénom': ['Rogen', 'Bis', 'Us'],
                        'courriel': ['a@b.c', 'd@e.f', 'g@h.i'],
                        'role': ['testeur', 'testeur', 'testeur']}, index=idx)
        base.append('personnes', df)  # Ajouter les données

        print('Tableau \'personnes\' après ajout')
        df = base.select('personnes')
        print(df.head())
        print()

        # Démo: classe de manipulation d'une seule table de données
        print('Tableau \'personnes\' à partir d\'un BaseTableau')
        tab = BaseTableau(base, 'personnes')
        print(tab.head())
        print()

        # Démo: Ajouter des entrées à une table de données
        idx = Index([3, 4, 5], name='index')
        df = DataFrame({'matricule': ['p0000045', 'p0000065', 'p00000023'],
                        'nom': ['Zeke', 'Bobby', 'Flint'],
                        'prénom': ['Zeke', 'Pin', 'Marco'],
                        'courriel': ['a@b.c', 'd@e.f', 'g@h.i'],
                        'role': ['testeur', 'testeur', 'testeur']}, index=idx)
        tab.append(df)

        print('Tableau \'personnes\' après ajout')
        print(tab.head())
    finally:
        fichier_db.unlink()
finally:
    fichier_config.unlink()
