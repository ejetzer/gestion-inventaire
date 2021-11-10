#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Construire une base de donnée selon un fichier de configuration simple.

Created on Fri Nov  5 14:55:41 2021

@author: ejetzer
"""

import pathlib

import configparser as cp
import itertools as it

import sqlalchemy as db

types_db = {'datetime.date': db.Date,
            'datetime.datetime': db.DateTime,
            'datetime.time': db.Time,
            'datetime.timedelta': db.Interval,
            'str': db.UnicodeText,
            'int': db.BigInteger,
            'float': db.Float,
            'bool': db.Boolean}

def définir_col(nom_colonne, type_colonne):
    db_type = types_db.get(type_colonne, db.PickleType)
    if nom_colonne == 'index':
        return db.Column(nom_colonne, db_type, primary_key=True)
    else:
        return db.Column(nom_colonne, db_type)

def définir_db(config: cp.ConfigParser):
    metadata = db.MetaData()

    tables = filter(lambda x: x in config.sections(),
                    eval(config['base de données']['tables']))
    for nom_table in tables:
        section = config[nom_table]

        colonnes = []
        for nom_colonne, type_colonne in it.chain(config['common'].items(), section.items()):
            colonnes.append(définir_col(nom_colonne, type_colonne))

        db.Table(nom_table, metadata, *colonnes)

    return metadata

if __name__ == '__main__':
    config = cp.ConfigParser()
    config.read('référence.config')

    moteur = db.create_engine(config['base de données']['adresse'])

    metadata = définir_db(config)
    metadata.create_all(moteur)
