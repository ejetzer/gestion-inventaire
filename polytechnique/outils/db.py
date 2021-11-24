#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Construire une base de donnée selon un fichier de configuration simple.

Created on Fri Nov  5 14:55:41 2021

@author: ejetzer
"""

import pathlib
import datetime

import itertools as it

from typing import Union, Any, Callable

import sqlalchemy as db
import pandas as pd
import tkinter as tk

from .config import FichierConfig

TYPES: tuple[dict[str, Union[str, type]]] = ({'config': None,
                                              'python': str,
                                              'pandas': 'object',
                                              'sqlalchemy': db.PickleType,
                                              'tk': tk.StringVar},
                                             {'config': 'datetime.date',
                                              'python': datetime.date,
                                              'pandas': 'datetime64[D]',
                                              'sqlalchemy': db.Date,
                                              'tk': tk.StringVar},
                                             {'config': 'datetime.datetime',
                                              'python': datetime.datetime,
                                              'pandas': 'datetime64[ns]',
                                              'sqlalchemy': db.DateTime,
                                              'tk': tk.StringVar},
                                             {'config': 'datetime.time',
                                              'python': datetime.time,
                                              'pandas': 'datetime64[ns]',
                                              'sqlalchemy': db.Time,
                                              'tk': tk.StringVar},
                                             {'config': 'datetime.timedelta',
                                              'python': datetime.timedelta,
                                              'pandas': 'period[ns]',
                                              'sqlalchemy': db.Interval,
                                              'tk': tk.StringVar},
                                             {'config': 'str',
                                              'python': str,
                                              'pandas': 'string',
                                              'sqlalchemy': db.UnicodeText,
                                              'tk': tk.StringVar},
                                             {'config': 'int',
                                              'python': int,
                                              'pandas': 'int64',
                                              'sqlalchemy': db.BigInteger,
                                              'tk': tk.StringVar},
                                             {'config': 'float',
                                              'python': float,
                                              'pandas': 'float64',
                                              'sqlalchemy': db.Float,
                                              'tk': tk.StringVar},
                                             {'config': 'bool',
                                              'python': bool,
                                              'pandas': 'boolean',
                                              'sqlalchemy': db.Boolean,
                                              'tk': tk.StringVar},
                                             {'config': 'pathlib.Path',
                                              'python': pathlib.Path,
                                              'pandas': 'object',
                                              'sqlalchemy': db.PickleType,
                                              'tk': tk.StringVar})

#DATE_TYPES: tuple[str] = ('datetime64[D]', 'datetime64[ns]')

TYPES_FICHIERS: dict[str, Callable] = {'xlsx': pd.read_excel,
                                       'xls': pd.read_excel,
                                       'csv': pd.read_csv,
                                       'pickle': pd.read_pickle,
                                       'txt': pd.read_table}

def get_type(de: str, t: Union[type, str], à: str) -> Union[type, str]:
    for s in filter(lambda x: x[de] == t, TYPES):
        return s[à]
    return next(filter(lambda x: x['config'] == None, TYPES))[à]

def def_col(nom: str, t: str) -> db.Column:
    primaire = nom == 'index'
    t = get_type('config', t, 'sqlalchemy')
    return db.Column(nom, t, primary_key=primaire)

class BaseDeDonnées:

    def __init__(self, config: FichierConfig):
        self.config = config

    @property
    def adresse(self):
        return self.config.get('bd', 'adresse', fallback='test.db')

    def dtype(self, table: str, champ: str):
        return get_type('config', self.config.get(table, champ, fallback=self.config.get('common', champ, fallback=None)), 'pandas')

    def dtypes(self, table: str) -> pd.Series:
        cols = self.columns(table)
        dtypes = map(lambda x: self.dtype(table, x), self.columns(table))
        dtypes = pd.Series(dtypes, index=cols)
        return dtypes

    # def date_types(self, table: str) -> pd.Series:
    #     return self.dtypes[self.dtypes(table).isin(DATE_TYPES)]

    def columns(self, table: str, from_config=False) -> pd.Index:
        if from_config:
            return pd.Index(it.chain(self.config['common'].items(), self.config[table].items()))
        return pd.Index(c.name for c in self.table(table).columns)

    def tables(self, from_config=False) -> dict[str, Union[str, db.Table]]:
        if from_config:
            return dict(map(lambda n: (n, self.config[n]), self.config.get('bd', 'tables').strip().split('\n')))
        return self.metadata.tables

    def table(self, table: str) -> db.Table:
        return self.metadata.tables[table]

    def index(self, table: str) -> pd.Index:
        requête = db.select([db.column('index')]).select_from(db.table(table))
        with self.begin() as conn:
            résultat = conn.execute(requête)
            return pd.Index(résultat)

    @property
    def metadata(self) -> db.MetaData:
        metadata = db.MetaData()

        for nom in self.tables(True):
            colonnes = map(def_col, *zip(*self.columns(nom, True)))
            db.Table(nom, metadata, *colonnes)

        return metadata

    def réinitialiser(self): #, tables: tuple[str] = None):
        with self.begin() as conn:
            self.metadata.drop_all(conn) #, tables)
            self.metadata.create_all(conn) #, tables)

    def loc(self, table: str, columns: tuple[str] = tuple(), where: tuple = tuple(), errors: str = 'ignore'):
        return self.select(table, columns, where, errors).loc

    def iloc(self, table: str, columns: tuple[str] = tuple(), where: tuple = tuple(), errors: str = 'ignore'):
        return self.select(table, columns, where, errors).iloc

    def execute(self, *requests):
        with self.begin() as conn:
            for request in requests:
                conn.execute(request)

    def select(self, table: str, columns: tuple[str] = tuple(), where: tuple = tuple(), errors: str = 'ignore') -> pd.DataFrame:
        if not columns:
            columns = self.columns(table)

        columns = map(db.column, columns)
        requête = db.select(columns)
        requête = requête.select_from(db.table(table))

        for clause in where:
            requête = requête.where(clause)

        with self.begin() as conn:
            print(f'{requête!s}')
            df = pd.read_sql(requête, conn, index_col='index')

        # Erreur avec le mapping dtypes, incertain pourquoi
        #dtypes = dict(self.dtypes(table))
        #df = df.astype(dtypes, errors=errors)

        return df

    def update(self, table: str, values: pd.DataFrame):
        requête = db.update(db.table(table))
        index = values.index.name
        requêtes = [requête.where(db.column(index) == i).values(**rangée) for i, rangée in values.iterrows()]
        self.execute(*requêtes)

    def insert(self, table: str, values: pd.DataFrame):
        requête = db.insert(db.table(table))
        requêtes = [requête.values(index=i, **rangée) for i, rangée in values.iterrows()]
        for r in requêtes:
            print(f'{r!r}')
        self.execute(*requêtes)

    def append(self, table: str, values: pd.DataFrame):
        indice_min = max(self.index(table), default=-1) + 1
        nouvel_index = pd.Index(range(len(values.index)), name='index') + indice_min
        values = values.copy()
        values.index = nouvel_index
        print(f'{values!s}')
        self.insert(table, values)

    def delete(self, table: str, values: pd.DataFrame):
        requête = db.delete(db.table(table))
        index = values.index.name
        requêtes = [requête.where(column(index) == i) for i in values.index]
        self.execute(*requêtes)

    ## TODO Ajouter un support pour ALTER pour ajouter ou retirer des colonnes

    def insert_columns(self, table: str, dtypes: pd.Series):
        '''Méthode d'ajout de colonnes.
Techniquement de la triche, efface et ré-entre les données.
Ne fonctionnera pas avec les grosses bases de données.'''
        vieille = self.select(table)

        for col, dtype in self.dtypes(table).items():
            self.config[table][col] = get_type('pandas', dtype, 'config')

        self.réinitialiser()
        self.insert(table, vieille)

    def delete_columns(self, table: str, columns: pd.Series):
        vieille = self.select(table)

        for col in columns:
            del self.config[table][col]

        self.config.write()

        self.réinitialiser()
        self.insert(table, vieille)

    def deviner_type_fichier(self, chemin: pathlib.Path):
        return TYPES_FICHIERS[chemin.suffix]

    def read_file(self, table: str, chemin: pathlib.Path, type_fichier: Union[str, Callable] = None):
        if type_fichier is None:
            type_fichier = self.deviner_type_fichier(chemin)
        elif isinstance(type_fichier, str):
            type_fichier = TYPES_FICHIERS[type_fichier]

        df = type_fichier(chemin, index_col='index')
        self.màj(table, df)

    def màj(self, table: str, values: pd.DataFrame):
        index = self.index(table)
        existe = values.index.isin(index)

        test = ~values.columns.isin(self.columns(table, from_config=True))
        if test.any():
            nouvelles_colonnes = values.columns[test]
            self.insert_columns(table, values.dtypes[test])

        self.update(table, values.loc[existe, :])
        self.insert(table, values.loc[~existe, :])

    def create_engine(self):
        return db.create_engine(self.adresse)

    def begin(self):
        return self.create_engine().begin()

__all__ = [BaseDeDonnées]

if __name__ == '__main__':
    config = FichierConfig('référence.config')

    base_de_données = BaseDeDonnées(config)
    #base_de_données.réinitialiser()
