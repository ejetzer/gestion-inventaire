#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Programme pour afficher et modifier visuellement des DataFrames Pandas.

Created on Tue Nov  2 15:40:02 2021

@author: ejetzer
"""

import pathlib

import itertools as it
import tkinter as tk

from tkinter.simpledialog import askstring, askinteger, askfloat
from dataclasses import dataclass, field, InitVar
from typing import Callable, Any, Union

import pandas as pd

from .db import BaseDeDonnées, get_type

@dataclass
class InterfaceHandler:
    entrée: Callable[[str, Callable, type], Any]
    texte: Callable[[str], Any]
    bouton: Callable[[str, Callable], Any]
    demander: Callable[[str, type], Callable]

def tkHandler(master: tk.Tk) -> InterfaceHandler:
    def entrée(value: pd.DataFrame, commande: Callable, dtype: str = 'object') -> tk.Entry:
        variable = get_type('pandas', dtype, 'tk')(master, value.iloc[0, 0])
        conversion = get_type('pandas', dtype, 'python')

        variable.trace_add('write', lambda x, i, m, v=variable: commande(pd.DataFrame(conversion(v.get()),
                                                                                      index=value.index,
                                                                                      columns=value.columns,
                                                                                      dtype=dtype)))

        if dtype == 'boolean':
            widget = Tkinter.Checkbutton(master, variable=variable)
        else:
            widget = tk.Entry(master, textvariable=variable)

        return widget

    texte = lambda s: tk.Label(master, text=s)
    bouton = lambda s, c: tk.Button(master, text=s, command=c)

    def demander(question: str = '', dtype: type = str):
        if dtype == str:
            return askstring('?', question)
        elif dtype == int:
            return askinteger('?', question)
        elif dtype == float:
            return askfloat('?', question)

    return InterfaceHandler(entrée, texte, bouton, demander)


class HTMLÉlémentInterface:

    def __init__(self, master, tag: str, attrs: dict[str, str], contenu: list=None):
        self.master = master
        self.tag = tag
        self.attrs = attrs
        self.contenu = contenu

    def grid(row: int, column: int):
        return str(self)

    def __repr__(self):
        return f'<Élément {tag}>'

    def __str__(self):
        attributs = ' '.join(f'{a}="{b}"' for a, b in self.attrs.items())
        if contenu is None:
            return f'<{self.tag} {attributs} />'
        elif isinstance(contenu, list):
            return f'<{self.tag} {attributs}>\n' + '\n'.join(str(e) for e in self.contenu) + f'</{self.tag}>'

class HTMLTable(HTMLÉlémentInterface):

    def __init__(self, master=None):
        super().__init__(master, 'table')
        self.grille = [[]]

    def grid(row: int, column: int):
        return str(self)



class HTMLCellule(HTMLÉlémentInterface):

    def __init__(self, master: HTMLTable = None):
        super().__init__(master, 'td')

    def grid(row: int, column: int):
        while row >= len(self.master.grille):
            self.master.grille.append([])
        while column >= len(self.master.grille[row]):
            self.master.grille[row].append(None)
        self.master.grille[row][column] = self

        return super().grid(row, column)

class HTMLEntrée(HTMLCellule):

    def __init__(self, master: HTMLTable, texte: str, commande: Callable):
        pass


class HTMLTexte(HTMLCellule):

    def __init__(self, master: HTMLTable, texte: str):
        pass


class HTMLBouton(HTMLCellule):

    def __init__(self, master: HTMLTable, texte: str, commande: Callable):
        pass

class Tableau:
    """Wrapper for BaseDeDonnées & InterfaceHandler"""

    def __init__(self, handler: InterfaceHandler, db: BaseDeDonnées, table: str):
        """Wrap DataFrame & Frame."""
        self.db = db
        self.table = table
        self.handler = handler

    @property
    def df(self):
        return self.db.select(self.table)

    @property
    def dtypes(self):
        return self.db.dtypes(self.table)

    def màj(self, values: pd.DataFrame):
        self.db.màj(self.table, values)

    @property
    def shape(self):
        return self.df.shape

    @property
    def columns(self):
        return self.df.columns

    @property
    def index(self):
        return self.df.index

    def iterrows(self):
        return self.df.iterrows()

    @property
    def loc(self):
        return self.df.loc

    @property
    def iloc(self):
        return self.df.iloc

    def réinitialiser(self):
        self.db.réinitialiser()

    def oublie_pas_la_màj(self, f: Callable, *args):
        def F():
            f(*args)
            self.update_grid()

        return F

    def commandes_colonne(self, col):
        return (self.handler.bouton('+', self.oublie_pas_la_màj(self.ajouter_colonne)),
                self.handler.bouton('-', self.oublie_pas_la_màj(self.retirer_colonne)))

    def commandes_rangée(self, rangée):
        return (self.handler.bouton('+', self.oublie_pas_la_màj(self.append)),
                self.handler.bouton('-', self.oublie_pas_la_màj(self.retirer_rangée, rangé)))

    def build(self):
        df = self.df

        if df.shape[0] == 0:
            self.append()
        if df.shape[1] == 0:
            self.ajouter_colonne('index')

        self.rangée_titres = [self.handler.texte(c) for c in df.columns]
        self.colonne_index = [self.handler.texte(i) for i in df.index]
        self.tableau_contenu = [[self.handler.entrée(df.loc[[i], [c]], lambda v: self.màj(v)) for c in df.columns] for i in df.index]
        self.commandes_colonnes = [self.commandes_colonne(c) for c in df.columns]
        self.commandes_rangées = [self.commandes_rangée(i) for i in df.index]

    @property
    def rowspan(self):
        return self.shape[0] + 1

    @property
    def columnspan(self):
        return self.shape[1] + 1

    def grid(self, row: int, column: int):
        """Display the DataFrame."""
        self.__grid_params = {'row': row, 'column': column}

        self.build()

        for i, (col, (plus, moins)) in enumerate(zip(self.rangée_titres, self.commandes_colonnes)):
            for k, w in enumerate((plus, moins, col)):
                w.grid(row=row+k, column=column+i+3)

        for i, (idx, rang, (plus, moins)) in enumerate(zip(self.colonne_index, self.tableau_contenu, self.commandes_rangées)):
            for k, w in enumerate((plus, moins, idx)):
                w.grid(row=row+i+3, column=column+k)

            for j, col in enumerate(rang):
                col.grid(row=row+i+3, column=column+k+j+1)

    @property
    def widgets(self):
        return it.chain(self.rangée_titres, self.colonne_index, *self.tableau_contenu, *self.commandes_rangées, *self.commandes_colonnes)

    def destroy_widgets(self):
        for widget in self.widgets:
            widget.destroy()

    def destroy(self):
        self.destroy_widgets()
        super().destroy()

    def update_grid(self):
        'Update the grid after a change to the DataFrame'
        self.destroy_widgets()
        self.build()
        self.grid(**self.__grid_params)

    ## TODO Les fonctions d'ajout et de retrait de rangée et colonne devraient affecter directement la base de données

    def append(self, values: pd.DataFrame = None):
        if values is None:
            values = pd.DataFrame({c: [get_type('pandas', t, 'python')()] for c, t in self.dtypes.items()})
            values = values.set_index('index')

        self.db.append(self.table, values)

    def ajouter_colonne(self, nom_de_colonne=None):
        if nom_de_colonne is None:
            nom_de_colonne = self.handler.demander('Quel nom de colonne?')

        if nom_de_colonne not in self.columns:
            self.db.insert_columns(self.table, {nom_de_colonne: 'object'})

    def delete(self, index=None):
        if index is None:
            index = self.handler.demander('Quelle rangée?', int)

        df = self.loc[[index], :]
        self.db.delete(self.table, df)

    def retirer_colonne(self, nom=None):
        if nom is None:
            nom = self.handler.demander('Quelle colonne?')

        if nom in self.columns:
            self.db.delete_columns(table, pd.Series([nom]))
