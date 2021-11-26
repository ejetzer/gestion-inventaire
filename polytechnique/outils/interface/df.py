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

from typing import Callable, Any, Union

import pandas as pd
import sqlalchemy as sqla

from ..database import BaseDeDonnées
from ..database.dtypes import get_type
from ..interface import InterfaceHandler

class BaseTableau:
    """Encapsulation de la classe BaseDeDonnées."""

    def __init__(self, db: BaseDeDonnées, table: str):
        """Encapsule de la classe BaseDeDonnées, avec accès seulement è la table table."""
        self.__table: str = table
        self.__db: BaseDeDonnées = db

    @property
    def table(self) -> sqla.Table:
        """Structure et métadonnées de la table de données."""
        return self.__db.table(self.__table)

    @property
    def df(self) -> pd.DataFrame:
        """Retourne un DataFrame contenant la table de données."""
        return self.__db.select(self.__table)

    @property
    def dtypes(self):
        """Retourne les types des colonnes."""
        return self.__db.dtypes(self.__table)

    @property
    def shape(self):
        """Retourne les dimensions de la table de données."""
        return self.__db.shape(self.__table)

    @property
    def columns(self):
        """Retourne une liste des colonnes de la table de données."""
        cols = self.__db.columns(self.__table)
        return cols

    @property
    def index(self):
        """Retourne un liste des indices de la table de données."""
        return self.__db.index(self.__table)

    def iterrows():
        """Itère sur les rangées de la table de données."""
        return self.df.iterrows()

    @property
    def loc(self):
        """Retourne l'objet loc du DataFrame de la table de données."""
        return self.__db.loc(self.__table, self.columns)

    @property
    def iloc(self):
        """Retourne l'object iloc du DataFrame de la table de données."""
        return self.__db.iloc(self.__table, self.columns)

    def append(self, values: pd.DataFrame = None):
        """Ajoute les entrées décrites par le cadre values dans la table de données."""
        if values is None:
            cols = self.columns
            idx = max(self.index) + 1
            values = pd.DataFrame(None, columns=cols, index=[idx])
        self.__db.append(self.__table, values)

    def delete(self, index: int):
        """Retire l'entrée avec l'index approprié."""
        self.__db.delete(self.__table, self.loc[[index], :])

    def réinitialiser(self):
        """Réinitialise la base de données, selon son schéma interne."""
        self.__db.réinitialiser()

    def màj(self, values: pd.DataFrame):
        self.__db.màj(self.__table, values)


class Tableau(BaseTableau):
    """Encapsulation de InterfaceHandler, avec héritage de BaseTableau."""

    def __init__(self, handler: InterfaceHandler, db: BaseDeDonnées, table: str):
        """Wrap DataFrame & Frame."""
        super().__init__(db, table)
        self.__widgets = pd.DataFrame()
        self.__commandes = {'index': [], 'columns': []}
        self.__handler = handler

    def oublie_pas_la_màj(self, f: Callable, *args):
        """Force la mise à jour de la grille après un changement à la base de données."""
        def F():
            f(*args)
            self.update_grid()

        return F

    def build_commandes(self, rangée):
        return (self.__handler.bouton('+', self.oublie_pas_la_màj(self.append)),
                self.__handler.bouton('-', self.oublie_pas_la_màj(self.delete, rangée)))

    def build(self):
        self.__widgets = self.df.copy()

        colonnes = filter(lambda x: x != 'index', self.columns)
        colonnes = list(map(self.__handler.texte, colonnes))
        self.__widgets.columns = colonnes

        index = list(map(self.__handler.texte, self.index))
        self.__widgets.index = index

        I, C = self.__widgets.shape
        for i, c in it.product(range(I), range(C)):
            self.__widgets.iloc[i, c] = self.__handler.entrée(self.iloc[[i], [c]],
                                                              self.màj)
        self.__commandes = list(map(self.build_commandes, self.index))

    @property
    def rowspan(self):
        """Retourne le nombre de rangées + 1 (pour l'index)."""
        return self.shape[0] + 2

    @property
    def columnspan(self):
        """Retourne le nombre de colonnes + 1 (pour l'en-tête)."""
        return self.shape[1] + 2

    def grid(self, row: int, column: int):
        """Display the DataFrame."""
        self.__grid_params = {'row': row, 'column': column}

        self.build()

        for i, c in enumerate(self.__widgets.columns):
            c.grid(row=row, column=column+i+3)

        for i, ((idx, rang), (plus, moins)) in enumerate(zip(self.__widgets.iterrows(), self.__commandes)):
            for k, w in enumerate((plus, moins, idx)):
                w.grid(row=row+i+1, column=column+k)

            for j, col in enumerate(rang):
                col.grid(row=row+i+1, column=column+k+j+1)

    def pack(self, *args, **kargs):
        pass

    @property
    def children(self):
        return it.chain(self.__widgets.columns,
                        self.__widgets.index,
                        *self.__widgets.values,
                        *self.__commandes)

    def destroy_children(self):
        for widget in self.children:
            widget.destroy()

    def destroy(self):
        self.destroy_children()
        super().destroy()

    def update_grid(self):
        """Update the grid after a change to the DataFrame"""
        self.destroy_children()
        self.build()
        self.grid(**self.__grid_params)


def main():
    import polytechnique.outils.database
    base, md = polytechnique.outils.database.main()

    import polytechnique.outils.interface.tkinter
    import tkinter

    print('Test d\'interface...')
    racine = tkinter.Tk()
    handler = polytechnique.outils.interface.tkinter.tkHandler(racine)

    print('Tableau...')
    tableau = Tableau(handler, base, 'demo')
    print(f'{tableau.index=}')

    tableau.grid(0, 0)

    racine.mainloop()

    print('On réouvre, pour montrer que les changements sont bien soumis à la base de données...')
    racine = tkinter.Tk()
    handler = polytechnique.outils.interface.tkinter.tkHandler(racine)
    tableau = Tableau(handler, base, 'demo')
    tableau.grid(0, 0)
    racine.mainloop()

if __name__ == '__main__':
    main()
