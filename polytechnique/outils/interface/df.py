#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Programme pour afficher et modifier visuellement des DataFrames Pandas.

Created on Tue Nov  2 15:40:02 2021

@author: ejetzer
"""

import itertools as it

from typing import Callable, Any, Union, Iterator, NamedTuple
from functools import partial
from inspect import signature

import pandas as pd
import sqlalchemy as sqla

from ..database import BaseDeDonnées
from ..interface import InterfaceHandler


class BaseTableau:
    """Encapsulation de la classe BaseDeDonnées."""

    def __init__(self, db: BaseDeDonnées, table: str):
        """
        Encapsule de la classe BaseDeDonnées, avec accès seulement à la table table.

        Parameters
        ----------
        db : BaseDeDonnées
            Une interface à une base de données.
        table : str
            Le nom d'un tableau dans db.

        Returns
        -------
        None.

        """
        self.__table: str = table
        self.__db: BaseDeDonnées = db

    def __getattr__(self, attr: str) -> Any:
        if hasattr(BaseDeDonnées,  attr):
            obj = getattr(self.__db, attr)
            if isinstance(obj, Callable):
                sig = signature(obj)
                if len(sig.parameters) == 1 and 'table' in sig.parameters:
                    return partial(obj, self.__table)()
                elif 'table' in sig.parameters:
                    return partial(obj, self.__table)
                else:
                    return obj
            else:
                return obj
        elif hasattr(pd.DataFrame, attr):
            return getattr(self.df, attr)
        else:
            msg = f'{self!r} de type {type(self)} n\'a pas d\'attribut {attr}, ni (self.__db: BaseDeDonnées, self.df: pandas.DataFrame).'
            raise AttributeError(msg)

    @property
    def df(self) -> pd.DataFrame:
        return self.select()

    def append(self, values: pd.DataFrame = None):
        if values is None:
            cols, idx = self.columns, [max(self.index, default=0) + 1]
            values = pd.DataFrame(None, columns=cols, index=[idx])
        self.__db.append(self.__table, values)


class Tableau(BaseTableau):
    """Encapsulation de InterfaceHandler, avec héritage de BaseTableau."""

    def __init__(self, handler: InterfaceHandler, db: BaseDeDonnées, table: str):
        """Wrap DataFrame & Frame."""
        super().__init__(db, table)
        self.__widgets = pd.DataFrame()
        self.__commandes = []
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
            self.__widgets.iloc[i, c] = self.__handler.entrée(self.iloc()[[i], [c]],
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
        self.grid(**self.__grid_params)


class Formulaire(BaseTableau):

    def __init__(self, handler: InterfaceHandler, db: BaseDeDonnées, table: str):
        """Wrap DataFrame & Frame."""
        super().__init__(db, table)
        self.__widgets = pd.DataFrame()
        self.__commandes = []
        self.__handler = handler

    def oublie_pas_la_màj(self, f: Callable, *args):
        """Force la mise à jour de la grille après un changement à la base de données."""
        def F():
            f(*args)
            self.update_grid()

        return F

    @property
    def __index(self):
        if len(self.index):
            return max(self.index) + 1
        else:
            return 0

    def effacer(self):
        self.update_grid()
        # TODO: rentrer la date automatiquement

    def soumettre(self):
        self.append(pd.DataFrame({c.cget('text'): [v.get()] for c, v in self.__widgets.loc[0, :].items()},
                                 index=[self.__index]))
        self.effacer()

    def build_commandes(self):
        return (self.__handler.bouton('Effacer', self.effacer),
                self.__handler.bouton('Soumettre', self.soumettre))

    def build(self):
        self.__widgets = pd.DataFrame(None, columns=self.columns, index=[0])

        colonnes = filter(lambda x: x != 'index', self.columns)
        colonnes = list(map(self.__handler.texte, colonnes))
        self.__widgets.columns = colonnes

        for col in colonnes:
            n = self.__handler.entrée(pd.DataFrame(None, columns=[col], index=[self.__index]),
                                      lambda x: None)
            self.__widgets.loc[0, col] = n

        self.__commandes = self.build_commandes()

    @property
    def rowspan(self):
        """Retourne le nombre de rangées + 1 (pour l'index)."""
        return self.shape[1] + 2

    @property
    def columnspan(self):
        """Retourne le nombre de colonnes + 1 (pour l'en-tête)."""
        return 2

    def grid(self, row: int, column: int):
        """Display the DataFrame."""
        self.__grid_params = {'row': row, 'column': column}

        self.build()

        for j, (c, v) in enumerate(zip(self.__widgets.columns, self.__widgets.loc[0, :])):
            c.grid(row=row+j, column=column)
            v.grid(row=row+j, column=column+1)

        for i, c in enumerate(self.__commandes):
            c.grid(row=row+j+1, column=column+i)

    def pack(self, *args, **kargs):
        pass

    @property
    def children(self):
        print(self.__widgets)
        return it.chain(self.__widgets.columns,
                        *self.__widgets.values,
                        self.__commandes)

    def destroy_children(self):
        for widget in self.children:
            print(f'{widget=}')
            widget.destroy()

    def destroy(self):
        self.destroy_children()
        super().destroy()

    def update_grid(self):
        """Update the grid after a change to the DataFrame"""
        self.destroy_children()
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

    print('On teste le formulaire...')
    racine = tkinter.Tk()
    handler = polytechnique.outils.interface.tkinter.tkHandler(racine)
    formulaire = Formulaire(handler, base, 'demo')
    formulaire.grid(0, 0)
    racine.mainloop()

    print('On réouvre, pour montrer que les changements sont bien soumis à la base de données...')
    racine = tkinter.Tk()
    handler = polytechnique.outils.interface.tkinter.tkHandler(racine)
    tableau = Tableau(handler, base, 'demo')
    tableau.grid(0, 0)
    racine.mainloop()


if __name__ == '__main__':
    main()
