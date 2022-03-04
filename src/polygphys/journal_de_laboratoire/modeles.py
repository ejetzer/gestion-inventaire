#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Modèles de bases de données pour un journal de laboratoire.

Créé le Fri Nov 26 15:36:57 2021

@author: ejetzer
"""

from sqlalchemy import MetaData

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
