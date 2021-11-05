#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Construire une base de donnée selon un fichier de configuration simple.

Created on Fri Nov  5 14:55:41 2021

@author: ejetzer
"""

import pathlib

import configparser as cp
import sqlalchemy as db

types_db = {'datetime.date': db.Date,
            'datetime.datetime': db.DateTime,
            'datetime.time': db.Time,
            'datetime.timedelta': db.Interval,
            'str': db.UnicodeText,
            'int': db.BigInteger,
            'float': db.Float,
            'bool': db.Boolean}

def définir_db(fichier_config: pathlib.Path):
    metadata = db.MetaData()

    config = cp.ConfigParser()
    config.read(fichier_config)

    for nom_table in config.sections():
        section = config[nom_table]

        colonnes = []
        for nom_colonne in section:
            type_colonne = section[nom_colonne]
            db_type = types_db.get(type_colonne, db.PickleType)
            if nom_colonne == 'index':
                colonnes.append(db.Column(nom_colonne, db_type, primary_key=True))
            else:
                colonnes.append(db.Column(nom_colonne, db_type))

        db.Table(nom_table, metadata, *colonnes)

    return metadata

if __name__ == '__main__':
    moteur = db.create_engine('sqlite:///référence.db')
    metadata = définir_db('référence.config')
    metadata.create_all(moteur)
