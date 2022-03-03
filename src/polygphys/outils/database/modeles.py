#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 11:51:37 2022

@author: emilejetzer
"""

from sqlalchemy import MetaData, Table, Column, ForeignKey

from .dtypes import column, default


def col_index() -> Column:
    return column('index', int, primary_key=True, autoincrement=True)


def personnes(metadata: MetaData) -> Table:
    cols = [col_index(),
            column('matricule', str),
            column('nom', str),
            column('prénom', str),
            column('courriel', str),
            column('role', str)
            ]

    return Table('personnes', metadata, *cols)


def locaux(metadata: MetaData) -> Table:
    matricule = metadata.tables['personnes'].columns['matricule']
    cols = [col_index(),
            column('porte principale', str),
            column('responsable', str, ForeignKey(matricule)),
            column('description', str),
            column('utilisation', str)
            ]

    return Table('locaux', metadata, *cols)


def portes(metadata: MetaData) -> Table:
    local = metadata.tables['locaux'].columns['porte principale']
    cols = [col_index(),
            column('numéro', str),
            column('local', str, ForeignKey(local))
            ]

    return Table('portes', metadata, *cols)


def etageres(metadata: MetaData) -> Table:
    local = metadata.tables['locaux'].columns['porte principale']
    matricule = metadata.tables['personnes'].columns['matricule']
    cols = [col_index(),
            column('local', str, ForeignKey(local)),
            column('responsable', str, ForeignKey(matricule)),
            column('numéro', str),
            column('tablette', str),
            column('sous-division', str),
            column('designation', str),
            column('description', str)
            ]

    return Table('etageres', metadata, *cols)


def créer_dbs(metadata: MetaData):
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
