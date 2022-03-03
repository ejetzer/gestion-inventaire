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
    matricule = metadata.tables['personnes'].columns['matricule']
    designation = metadata.tables['etageres'].columns['designation']
    cols = [col_index(),
            column('responsable', str, ForeignKey(matricule)),
            column('place', str, ForeignKey(designation)),
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


def boites(metadata: MetaData) -> Table:
    matricule = metadata.tables['personnes'].columns['matricule']
    designation = metadata.tables['etageres'].columns['designation']
    cols = [col_index(),
            column('responsable', str, ForeignKey(matricule)),
            column('place', str, ForeignKey(designation)),
            column('description', str),
            column('dimensions', str)
            ]

    return Table('boites', metadata, *cols)


def emprunts(metadata: MetaData) -> Table:
    appareil = metadata.tables['appareils'].columns['index']
    personnes = metadata.tables['personnes'].columns['matricule']
    cols = [col_index(),
            column('appareil', str, ForeignKey(appareil)),
            column('responsable', str, ForeignKey(personnes)),
            column('emprunteur', str, ForeignKey(personnes)),
            column('date emprunt', date),
            column('date retour', date),
            column('retourné', bool),
            column('détails', str)
            ]

    return Table('emprunts', metadata, *cols)


def utilisation_boites(metadata: MetaData) -> Table:
    boite = metadata.tables['appareils'].columns['index']
    personnes = metadata.tables['personnes'].columns['matricule']
    cols = [col_index(),
            column('boite', str, ForeignKey(boite)),
            column('responsable', str, ForeignKey(personnes)),
            column('emprunteur', str, ForeignKey(personnes)),
            column('date emprunt', date),
            column('date retour', date),
            column('retourné', bool),
            column('détails', str)
            ]

    return Table('utilisation_boites', metadata, *cols)


def créer_dbs(metadata: MetaData):
    modeles.créer_dbs(metadata)

    appareils(metadata)
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
