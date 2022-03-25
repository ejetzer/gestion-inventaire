#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modèles de base de données.

Created on Tue Jan 25 11:51:37 2022

@author: emilejetzer
"""

from sqlalchemy import MetaData, Table, Column, ForeignKey

from .dtypes import column


def col_index() -> Column:
    """
    Retourne une colonne d'index.

    Returns
    -------
    Column
        DESCRIPTION.

    """
    return column('index', int, primary_key=True, autoincrement=True)


def personnes(metadata: MetaData) -> Table:
    """
    Retourne le tableau du personnel.

    Parameters
    ----------
    metadata : MetaData
        DESCRIPTION.

    Returns
    -------
    Table
        DESCRIPTION.

    """
    cols = [col_index(),
            column('matricule', str),
            column('nom', str),
            column('prénom', str),
            column('courriel', str),
            column('role', str)
            ]

    return Table('personnes', metadata, *cols)


def locaux(metadata: MetaData) -> Table:
    """
    Retourne le tableau des locaux.

    Parameters
    ----------
    metadata : MetaData
        DESCRIPTION.

    Returns
    -------
    Table
        DESCRIPTION.

    """
    matricule = metadata.tables['personnes'].columns['index']
    cols = [col_index(),
            column('porte principale', str),
            column('responsable', int, ForeignKey(matricule)),
            column('description', str),
            column('utilisation', str)
            ]

    return Table('locaux', metadata, *cols)


def portes(metadata: MetaData) -> Table:
    """
    Retourne le tableau des portes.

    Parameters
    ----------
    metadata : MetaData
        DESCRIPTION.

    Returns
    -------
    Table
        DESCRIPTION.

    """
    local = metadata.tables['locaux'].columns['index']
    cols = [col_index(),
            column('numéro', str),
            column('local', int, ForeignKey(local))
            ]

    return Table('portes', metadata, *cols)


def etageres(metadata: MetaData) -> Table:
    """
    Retourne le tableau des étagères.

    Parameters
    ----------
    metadata : MetaData
        DESCRIPTION.

    Returns
    -------
    Table
        DESCRIPTION.

    """
    local = metadata.tables['locaux'].columns['index']
    matricule = metadata.tables['personnes'].columns['index']
    cols = [col_index(),
            column('local', int, ForeignKey(local)),
            column('responsable', int, ForeignKey(matricule)),
            column('numéro', str),
            column('tablette', str),
            column('sous-division', str),
            column('designation', str),
            column('description', str)
            ]

    return Table('etageres', metadata, *cols)


def créer_dbs(metadata: MetaData):
    """
    Créer les bases de données.

    Parameters
    ----------
    metadata : MetaData
        DESCRIPTION.

    Returns
    -------
    metadata : TYPE
        DESCRIPTION.

    """
    personnes(metadata)
    locaux(metadata)
    portes(metadata)
    etageres(metadata)

    return metadata


if __name__ == '__main__':
    md = créer_dbs(MetaData())
    print(md)
    for t, T in md.tables.items():
        print(t)
        for c in T.columns:
            print('\t', c)
