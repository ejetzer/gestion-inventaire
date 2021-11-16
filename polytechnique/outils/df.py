#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Programme pour afficher et modifier visuellement des DataFrames Pandas.

Created on Tue Nov  2 15:40:02 2021

@author: ejetzer
"""

import itertools as it
import tkinter as tk

from tkinter.simpledialog import askstring, askinteger, askfloat
from dataclasses import dataclass, field, InitVar
from typing import Callable, Any

import sqlalchemy as db
import pandas as pd

@dataclass(frozen=True)
class InterfaceHandler:
    entrée: Callable[[str, Callable], Any]
    texte: Callable[[str], Any]
    bouton: Callable[[str, Callable], Any]

@dataclass
class tkHandler(InterfaceHandler):
    master: InitVar[tk.Tk]

    def __post_init__(self):
        def entrée(texte: str, commande: Callable) -> tk.Entry:
            variable = tk.StringVar(self.master, texte)
            variable.trace_add('write', lambda x, i, m, v=variable: commande())
            return tk.Entry(self.master, textvariable=variable)

        texte = lambda s: tk.Label(self.master, s)
        bouton = lambda s, c: tk.Button(self.master, text=s, command=c)

        super().__init__(entrée=entrée, texte=texte, bouton=bouton)


class HTMLÉlémentInterface:

    def __init__(self, master=None, tag: str, attrs: dict[str, str], contenu: list=tuple()):
        self.master = master
        self.tag = tag
        self.attrs = attrs
        self.contenu = contenu

    def grid(row: int, column: int):
        pass

    def __repr__(self):
        return f'<Élément {tag}>'

    def __str__(self):
        pass

class HTMLTable(HTMLÉlémentInterface):

    def grid(row: int, column: int):
        pass

class HTMLEntrée(HTMLÉlémentInterface):

    def __init__(self, master, texte: str, commande: Callable):
        pass

    def grid(row, column):
        pass


class HTMLTexte(HTMLÉlémentInterface):
    pass


class HTMLBouton(HTMLÉlémentInterface):
    pass


class Tableau:
    """Wrapper for pandas.DataFrame & tkinter.Frame."""

    def __init__(self, handler: InterfaceHandler, tableau: pd.DataFrame):
        """Wrap DataFrame & Frame."""
        self.tableau = tableau
        self.handler = handler

        self.__init_tableau()

    def __init_rangée_titres(self):
        return [self.handler.text(col) for col in self.tableau.columns]

    def __init_colonne_index(self):
        return [self.handler.text(k) for k, rang in self.tableau.iterrows()]

    def __init_tableau_contenu(self):
        return [[self.handler.entrée(col,
                                     lambda: self.update_tableau())\
                 for col in rang]\
                for k, rang in self.tableau.iterrows()]

    def __init_commandes_colonnes(self):
        return [self.commandes_colonne(col) for col in self.tableau.columns]

    def __init_commandes_rangées(self):
        return [self.commandes_rangée(rangée) for rangée, _ in self.tableau.iterrows()]

    def commandes_colonne(self, col):
        return (self.handler.bouton('+', lambda: self.ajouter_colonne()),
                self.handler.bouton('-', lambda: self.retirer_colonne(col)))

    def commandes_rangée(self, rangée):
        return (self.handler.bouton('+', lambda: self.ajouter_rangée()),
                self.handler.bouton('-', lambda: self.retirer_rangée(rangée)))

    def __init_tableau(self):
        self.rangée_titres = self.__init_rangée_titres()
        self.colonne_index = self.__init_colonne_index()
        self.tableau_contenu = self.__init_tableau_contenu()
        self.commandes_colonnes = self.__init_commandes_colonnes()
        self.commandes_rangées = self.__init_commandes_rangées()

    def grid(self,
             row: int,
             column: int,
             rowspan: int = None,
             columnspan: int = None,
             firstrow: int = 0,
             firstcolumn: int = 0):
        """Display the DataFrame."""
        self.__grid_params = {'row': row, 'column': column,
                              'rowspan': rowspan, 'columnspan': columnspan,
                              'firstrow': firstrow, 'firstcolumn': firstcolumn}

        défaut_span = self.tableau.shape

        if rowspan is None: rowspan = défaut_span[0] + 1
        if columnspan is None: columnspan = défaut_span[1] + 1

        cols = slice(firstcolumn, firstcolumn+columnspan)
        rangs = slice(firstrow, firstrow+rowspan)

        for i, (col, (plus, moins)) in enumerate(zip(self.rangée_titres[cols], self.commandes_colonnes)):
            for k, w in enumerate((plus, moins, col)):
                w.grid(row=row+k, column=column+i+3)

        for i, (idx, rang, (plus, moins)) in enumerate(zip(self.colonne_index[rangs], self.tableau_contenu[rangs], self.commandes_rangées)):
            for k, w in enumerate((plus, moins, idx)):
                w.grid(row=row+i+3, column=column+k)

            for j, col in enumerate(rang[cols]):
                col.grid(row=row+i+3, column=column+k+j+1)


    def update_tableau(self, *args, **kargs):
        for idx, rang in zip(self.colonne_index, self.tableau_contenu):
            for col, val in zip(self.rangée_titres, rang):
                self.tableau.loc[idx['text'], col['text']] = val.get()

    def update_grid(self):
        'Update the grid after a change to the DataFrame'
        for widget in it.chain(self.rangée_titres, self.colonne_index, *self.tableau_contenu, *self.commandes_rangées, *self.commandes_colonnes):
            widget.destroy()

        self.__init_tableau()
        self.grid(**self.__grid_params)

    def ajouter_rangée(self, rangée=None):
        if rangée is None or True: # Pour l'instant, toutes les rangées sont ajoutées à la fin
            self.tableau = self.tableau.append(pd.Series(), ignore_index=True)
        self.update_grid()

    def demander(self, question='', type_=str):
        if type_ == str:
            return askstring('?', question)
        elif type_ == int:
            return askinteger('?', question)
        elif type_ == float:
            return askfloat('?', question)

    def ajouter_colonne(self, nom_de_colonne=None):
        if nom_de_colonne is None:
            nom_de_colonne = self.demander('Quel nom de colonne?')

        if nom_de_colonne not in self.tableau.columns:
            self.tableau[nom_de_colonne] = None

        self.update_grid()

    def retirer_rangée(self, index=None):
        if index is None:
            index = self.demander('Quelle rangée?', int)

        self.tableau = self.tableau.drop(index)
        self.update_grid()

    def retirer_colonne(self, nom=None):
        if nom is None:
            nom = self.demander('Quelle colonne?')

        if nom in self.tableau.columns:
            self.tableau = self.tableau.drop(nom, axis=1)
        self.update_grid()
