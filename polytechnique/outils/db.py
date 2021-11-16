#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Construire une base de donnée selon un fichier de configuration simple.

Created on Fri Nov  5 14:55:41 2021

@author: ejetzer
"""

import pathlib
import datetime

import configparser as cp
import itertools as it

import sqlalchemy as db
import pandas as pd


types_py = {'datetime.date': datetime.date,
            'datetime.datetime': datetime.datetime,
            'datetime.time': datetime.time,
            'datetime.timedelta': datetime.timedelta,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool}

type_py = object

types_pd = {'datetime.date': 'datetime64[ns]',
            'datetime.datetime': 'datetime64[ns]',
            'datetime.time': 'datetime64[ns]',
            'datetime.timedelta': 'period[ns]',
            'str': 'string',
            'int': 'int64',
            'float': 'float64',
            'bool': 'boolean'}

type_pd = 'object'

types_db = {'datetime.date': db.Date,
            'datetime.datetime': db.DateTime,
            'datetime.time': db.Time,
            'datetime.timedelta': db.Interval,
            'str': db.UnicodeText,
            'int': db.BigInteger,
            'float': db.Float,
            'bool': db.Boolean}

type_db = db.PickleType

class BaseDeDonnées:

    def __init__(self, adresse, commun=('index',)):
        self.adresse = adresse
        self.commun = commun

    def def_col(self, nom, type_):
        type_ = types_db.get(type_, type_db)
        if nom == 'index':
            return db.Column(nom, type_, primary_key=True)
        else:
            return db.Column(nom, type_)

    def def_db(self, tables):
        metadata = db.MetaData()

        for nom, section in tables.items():
            colonnes = [self.def_col(nom_colonne, type_colonne) for nom_colonne, type_colonne in it.chain(self.commun.items(), section.items())]
            db.Table(nom, metadata, *colonnes)

        self.metadata = metadata

    def config(self, config):
        tables = {x: config[x] for x in config.sections() if x in config['base de données']['tables']}
        self.commun = config['common']
        self.def_db(tables)

    def réinitialiser(self, config):
        self.config(config)
        with self.begin() as conn:
            self.metadata.drop_all(conn)
            self.metadata.create_all(conn)

    def df(self, table=None, requête=None, filtre=None, index_col='index'):
        if table is not None:
            sql = table
        elif requête is not None:
            sql = requête

        with self.begin() as conn:
            df = pd.read_sql(sql, conn, index_col=index_col)

        if filtre is not None:
            df = df.loc[filtre(df)]

        return df

    def màj(self, df, table):
        with self.begin() as conn:
            df.to_sql(table, conn, if_exists='replace')

    def begin(self):
        engine = db.create_engine(self.adresse)
        return engine.begin()

__all__ = [BaseDeDonnées]

if __name__ == '__main__':
    config = cp.ConfigParser()
    config.read('référence.config')

    base_de_données = BaseDeDonnées(config['base de données']['adresse'], config['commun'])
    base_de_données.réinitialiser(config)
