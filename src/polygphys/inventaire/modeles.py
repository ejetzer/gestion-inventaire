#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Modèles de bases de données d'inventaire.

Créé le Fri Nov 26 15:36:57 2021

@author: ejetzer
"""

from datetime import date

from sqlalchemy import MetaData, Table, ForeignKey

from ..outils.database.dtypes import column
from ..outils.database import modeles
from ..outils.database.modeles import col_index


def appareils(metadata: MetaData) -> Table:
    """
    Lister des appareils.

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
    designation = metadata.tables['etageres'].columns['index']
    cols = [col_index(),
            column('responsable', int, ForeignKey(
                matricule, onupdate='CASCADE')),
            column('place', int, ForeignKey(designation)),
            column('numéro de série', str),
            column('numéro de modèle', str),
            column('fournisseur', str),
            column('fabricant', str),
            column('fonctionnel', bool),
            column('informations supplémentaires', str),
            column('nom', str),
            column('description', str)
            ]

    return Table('appareils', metadata, *cols)


def consommables(metadata: MetaData) -> Table:
    matricule = metadata.tables['personnes'].columns['index']
    designation = metadata.tables['etageres'].columns['index']
    cols = [col_index(),
            column('responsable', int, ForeignKey(matricule)),
            column('place', int, ForeignKey(designation)),
            column('numéro de fabricant', str),
            column('numéro de fournisseur', str),
            column('fournisseur', str),
            column('fabricant', str),
            column('commander', bool),
            column('informations supplémentaires', str),
            column('nom', str),
            column('description', str)
            ]

    return Table('consommables', metadata, *cols)


def boites(metadata: MetaData) -> Table:
    """
    Lister des boîtes de transport.

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
    designation = metadata.tables['etageres'].columns['index']
    cols = [col_index(),
            column('responsable', int, ForeignKey(matricule)),
            column('place', int, ForeignKey(designation)),
            column('description', str),
            column('dimensions', str)
            ]

    return Table('boites', metadata, *cols)


def emprunts(metadata: MetaData) -> Table:
    """
    Lister des emprunts.

    Parameters
    ----------
    metadata : MetaData
        DESCRIPTION.

    Returns
    -------
    Table
        DESCRIPTION.

    """
    appareil = metadata.tables['appareils'].columns['index']
    personnes = metadata.tables['personnes'].columns['index']
    cols = [col_index(),
            column('appareil', int, ForeignKey(appareil)),
            column('responsable', int, ForeignKey(personnes)),
            column('emprunteur', int, ForeignKey(personnes)),
            column('date emprunt', date),
            column('date retour', date),
            column('retourné', bool),
            column('détails', str)
            ]

    return Table('emprunts', metadata, *cols)


def utilisation_boites(metadata: MetaData) -> Table:
    """
    Lister des boîtes utilisées.

    Parameters
    ----------
    metadata : MetaData
        DESCRIPTION.

    Returns
    -------
    Table
        DESCRIPTION.

    """
    boite = metadata.tables['appareils'].columns['index']
    personnes = metadata.tables['personnes'].columns['index']
    cols = [col_index(),
            column('boite', int, ForeignKey(boite)),
            column('responsable', int, ForeignKey(personnes)),
            column('emprunteur', int, ForeignKey(personnes)),
            column('date emprunt', date),
            column('date retour', date),
            column('retourné', bool),
            column('détails', str)
            ]

    return Table('utilisation_boites', metadata, *cols)


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
    modeles.créer_dbs(metadata)

    appareils(metadata)
    consommables(metadata)
    boites(metadata)
    emprunts(metadata)
    utilisation_boites(metadata)

    return metadata


if __name__ == '__main__':
    md = créer_dbs(MetaData())
    print(md)
    for t, T in md.tables.items():
        print(t)
        for c in T.columns:
            print('\t', c)
