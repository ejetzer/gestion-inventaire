#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Programme ou module pour ...

Créé le Fri Nov 26 15:36:57 2021

@author: ejetzer
"""

from sqlalchemy import MetaData, Table

from ..outils.database.dtypes import column

metadata = MetaData()


def colonnes_communes():
    """
    Retourne les colonnes communes à tous les tableaux.

    Returns
    -------
    tuple[Column]
        Colonnes.

    """
    return column('index', int, primary_key=True), column('responsable', str)


cols = colonnes_communes() +\
    (column('description', str),
     column('local', str),
     column('quantité', int),
     column('largeur (cm)', float),
     column('longueur (cm)', float),
     column('hauteur (cm)', float))
boîtes = Table('boites', metadata, *cols)

cols_locaux = colonnes_communes() + (column('nom', str),
                                     column('description', str),
                                     column('nombre', int),
                                     column('local', str),
                                     column('armoire', str),
                                     column('étagère', str),
                                     column('Numéro de série', str),
                                     column('Numéro de modèle', str),
                                     column('Fournisseur', str),
                                     column('Fabricant', str),
                                     column('Fonctionnel', bool),
                                     column('Informations supplémentaires',
                                            str))
locaux = Table('inventaire', metadata, *cols_locaux)
