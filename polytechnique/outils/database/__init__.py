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

from typing import Union, Any, Callable, Iterable

import sqlalchemy as sqla
import pandas as pd
import tkinter as tk

from .dtypes import get_type

TYPES_FICHIERS: dict[str, Callable] = {'xlsx': pd.read_excel,
                                       'xls': pd.read_excel,
                                       'csv': pd.read_csv,
                                       'pickle': pd.read_pickle,
                                       'txt': pd.read_table}


class BaseDeDonnées:

    def __init__(self, adresse: str, schema: sqla.MetaData):
        self.__adresse = adresse
        self.__schema = schema

    @property
    def adresse(self):
        return self.__adresse

    # Interface de sqlalchemy

    @property
    def tables(self) -> dict[str, sqla.Table]:
        return self.__schema.tables

    def table(self, table: str) -> sqla.Table:
        return self.tables[table]

    def execute(self, requête, *args, **kargs):
        with self.begin() as con:
            print(f'{requête!s}')
            res = con.execute(requête, *args, **kargs)
            return res

    def select(self, table: str, columns: tuple[str] = tuple(), where: tuple = tuple(), errors: str = 'ignore') -> pd.DataFrame:
        if not len(columns):
            columns = self.columns(table)

        columns = [self.table(table).columns['index']] + list(
            filter(lambda x: x.name in columns, self.table(table).columns))
        requête = sqla.select(columns).select_from(self.table(table))

        for clause in where:
            requête = requête.where(clause)

        with self.begin() as con:
            print(f'{requête!s}')
            df = pd.read_sql(requête, con, index_col='index')

        return df

    def update(self, table: str, values: pd.DataFrame):
        requête = self.table(table).update()
        index = values.index.name
        for i, rangée in values.iterrows():
            clause = self.table(table).columns[index] == i
            r = requête.where(clause).values(**rangée)
            self.execute(r)

    def insert(self, table: str, values: pd.DataFrame):
        params = [({'index': i} | {c: v for c, v in r.items()})
                  for i, r in values.iterrows()]
        requête = self.table(table).insert(params)
        self.execute(requête)

    def append(self, table: str, values: pd.DataFrame):
        indice_min = max(self.index(table), default=-1) + 1
        nouvel_index = pd.Index(range(len(values.index)),
                                name='index') + indice_min
        values = values.copy()
        values.index = nouvel_index
        self.insert(table, values)

    def delete(self, table: str, values: pd.DataFrame):
        requête = self.table(table).delete()
        index = values.index.name
        for i in values.index:
            clause = self.table(table).columns[index] == 1
            r = requête.where(clause)
            self.execute(r)

    def màj(self, table: str, values: pd.DataFrame):
        index = self.index(table)
        existe = values.index.isin(index)

        test = ~values.columns.isin(self.columns(table))
        if test.any():
            nouvelles_colonnes = values.columns[test]
            self.insert_columns(table, values.dtypes[test])

        if existe.any():
            self.update(table, values.loc[existe, :])
        if not existe.all():
            self.insert(table, values.loc[~existe, :])

    def create_engine(self):
        print(self.__adresse)
        return sqla.create_engine(str(self.__adresse))

    def begin(self):
        return self.create_engine().begin()

    def initialiser(self, checkfirst=True):
        with self.begin() as con:
            self.__schema.create_all(con, checkfirst=checkfirst)

    def réinitialiser(self, checkfirst=True):
        with self.begin() as con:
            self.__schema.drop_all(con, checkfirst=checkfirst)
            self.__schema.create_all(con)

    # Interface de pandas.DataFrame

    def dtype(self, table: str, champ: str):
        type_champ = self.table(table).columns[champ].type
        type_champ = get_type('sqlalchemy', type_champ, 'pandas')
        return type_champ

    def dtypes(self, table: str) -> pd.Series:
        cols = self.columns(table)
        dtypes = map(lambda x: self.dtype(table, x), self.columns(table))
        dtypes = pd.Series(dtypes, index=cols)
        return dtypes

    def columns(self, table: str) -> pd.Index:
        return pd.Index(c.name for c in self.table(table).columns if c.name != 'index')

    def index(self, table: str) -> pd.Index:
        requête = sqla.select(self.table(
            table).columns['index']).select_from(self.table(table))
        with self.begin() as conn:
            résultat = conn.execute(requête)
            return pd.Index(r['index'] for r in résultat)

    def loc(self, table: str, columns: tuple[str] = None, where: tuple = tuple(), errors: str = 'ignore'):
        if columns is None:
            colums = self.columns(table)
        return self.select(table, columns, where, errors).loc

    def iloc(self, table: str, columns: tuple[str] = tuple(), where: tuple = tuple(), errors: str = 'ignore'):
        if columns is None:
            colums = self.columns(table)
        return self.select(table, columns, where, errors).iloc

    def deviner_type_fichier(self, chemin: pathlib.Path):
        return TYPES_FICHIERS[chemin.suffix]

    def read_file(self, table: str, chemin: pathlib.Path, type_fichier: Union[str, Callable] = None):
        if type_fichier is None:
            type_fichier = self.deviner_type_fichier(chemin)
        elif isinstance(type_fichier, str):
            type_fichier = TYPES_FICHIERS[type_fichier]

        df = type_fichier(chemin, index_col='index')
        self.màj(table, df)


def main() -> tuple[BaseDeDonnées, sqla.MetaData]:
    print('Définition d\'une base de données...')
    md = sqla.MetaData()
    table = sqla.Table('demo', md,
                       sqla.Column('index', get_type('python', int,
                                   'sqlalchemy'), primary_key=False),
                       sqla.Column('desc', get_type('python', str, 'sqlalchemy')))

    base = BaseDeDonnées('sqlite:///demo.db', md)
    base.réinitialiser()

    print('Base de données définie:')
    for t, T in base.tables.items():
        print(f'{t}: {T.columns}')

    print('Ajout de rangées:')
    df = base.select('demo')
    print(f'Départ:\n{df}')

    idx = pd.Index([0, 1, 2], name='index')
    df = pd.DataFrame({'desc': ['test 1', 'test 2', 'encore (3)']}, index=idx)
    print(f'Données à ajouter:\n{df}')

    base.append('demo', df)
    df = base.select('demo')
    print(f'Données ajoutées:\n{df}')

    return base, md


if __name__ == '__main__':
    main()
