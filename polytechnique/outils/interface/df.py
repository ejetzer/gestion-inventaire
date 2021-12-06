#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Programme pour afficher et modifier visuellement des DataFrames Pandas.

Created on Tue Nov  2 15:40:02 2021

@author: ejetzer
"""

import logging

import itertools as it

from typing import Callable, Any, Union
from functools import partial
from inspect import signature

import pandas as pd

from ..database import BaseDeDonnées
from ..interface import InterfaceHandler

logger = logging.getLogger(__name__)


class BaseTableau:
    """Encapsulation de la classe BaseDeDonnées."""

    def __init__(self, db: BaseDeDonnées, table: str):
        """
        Encapsule de la classe BaseDeDonnées.

        Avec accès seulement à la table table.

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
        logger.debug('{self!r} __init__({db=}, {table=})')
        self.table: str = table
        self.db: BaseDeDonnées = db

    def __getattr__(self, attr: str) -> Any:
        """
        Obtiens un attribut de self.db ou self.df.

        Facilite l'encapsulation.
        BaseDeDonnées a la priorité, ensuite pandas.DataFrame.

        Parameters
        ----------
        attr : str
            Attribut à obtenir.

        Raises
        ------
        AttributeError
            Si l'attribut ne peut pas être trouvé.

        Returns
        -------
        Any
            L'attribut demandé.

        """
        logger.debug(f'{self!r} __getattr__({attr=})')

        logger.debug(f'\t{hasattr(BaseDeDonnées, attr)=}')
        logger.debug(f'\t{hasattr(pd.DataFrame, attr)=}')
        if hasattr(BaseDeDonnées,  attr):
            obj = getattr(self.db, attr)
            logger.debug(f'\t{obj=}')

            logger.debug(f'\t{type(obj)=}')
            if isinstance(obj, Callable):
                sig = signature(obj)
                logger.debug(f'\t{sig=}')

                if len(sig.parameters) == 1 and 'table' in sig.parameters:
                    return partial(obj, self.table)()
                elif 'table' in sig.parameters:
                    return partial(obj, self.table)
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
        """Le tableau comme pandas.DataFrame."""
        logger.debug(f'{self!r} .df')
        return self.select()

    def append(self, values: Union[pd.Series, pd.DataFrame] = None):
        """
        Ajoute des valeurs au tableau.

        Parameters
        ----------
        values : Union[pd.Series, pd.DataFrame], optional
            Valeurs à ajouter. The default is None.

        Returns
        -------
        None.

        """
        logger.debug(f'{self!r} .append({values=})')

        logger.debug(f'\t{type(values)=}')
        if values is None:
            cols, idx = self.columns, [max(self.index, default=0) + 1]
            values = pd.DataFrame(None, columns=cols, index=[idx])
        elif isinstance(values, pd.Series):
            cols, idx = self.columns, [max(self.index, default=0) + 1]
            values = pd.DataFrame([values], index=[idx])
        logger.debug(f'\t{values=}')

        self.db.append(self.table, values)


class Tableau(BaseTableau):
    """Encapsulation de InterfaceHandler, avec héritage de BaseTableau."""

    def __init__(self,
                 handler: InterfaceHandler,
                 db: BaseDeDonnées,
                 table: str):
        """
        Encapsule InterfaceHandler & BaseDeDonnées.

        Parameters
        ----------
        handler : InterfaceHandler
            Instance de InterfaceHandler.
        db : BaseDeDonnées
            Base de Données à gérer.
        table : str
            Tableau à gérer.

        Returns
        -------
        None.

        """
        logger.debug(f'{self!r} .__init__({handler=}, {db=}, {table=})')
        super().__init__(db, table)
        self.__widgets = pd.DataFrame()
        self.__commandes = []
        self.__handler = handler

    def oublie_pas_la_màj(self, f: Callable, *args):
        """
        Force la mise à jour de la grille.

        À utiliser après un changement à la base de données.
        """
        logger.debug(f'{self!r} .oublie_pas_la_màj({f=}, {args=})')

        def F():
            logger.debug(f'** F() avec {f=} et {args=}.')
            f(*args)
            self.update_grid()

        logger.debug(f'\t{F=}')

        return F

    def build_commandes(self, rangée: int) -> tuple:
        """
        Construire les widgets de boutons.

        Eg: soummettre des données, effacer, etc.

        Parameters
        ----------
        rangée : int
            Rangée des widgets.

        Returns
        -------
        tuple
            Les widgets.

        """
        logger.debug(f'{self!r} .build_commandes({rangée=})')

        a = self.__handler.bouton('+', self.oublie_pas_la_màj(self.append))
        b = self.__handler.bouton('-', self.oublie_pas_la_màj(self.delete,
                                                              rangée))
        logger.debug(f'\t{a=} {b=}')

        return a, b

    def build(self):
        """
        Construire les widgets.

        Returns
        -------
        None.

        """
        logger.debug(f'{self!r} .build')

        self.__widgets = self.df.copy()
        logger.debug(f'\t{self.__widgets=}')

        colonnes = filter(lambda x: x != 'index', self.columns)
        colonnes = list(map(self.__handler.texte, colonnes))
        self.__widgets.columns = colonnes
        logger.debug(f'\t{self.__widgets=}')

        index = list(map(self.__handler.texte, self.index))
        self.__widgets.index = index
        logger.debug(f'\t{self.__widgets=}')

        I, C = self.__widgets.shape
        logger.debug(f'\t{I=}, {C=}')

        for i, c in it.product(range(I), range(C)):
            logger.debug(f'\t\t{i=}, {c=}')

            df = self.iloc()[[i], [c]]
            logger.debug(f'\t\t{df=}')

            _ = self.__handler.entrée(df, self.màj)
            logger.debug(f'\t\t{_=}')

            self.__widgets.iloc[i, c] = _
            logger.debug(f'\t\t{self.__widgets=}')

        self.__commandes = list(map(self.build_commandes, self.index))
        logger.debug(f'\t{self.__commandes=}')

    @property
    def rowspan(self):
        """Retourne le nombre de rangées + 1 (pour l'index)."""
        return self.shape[0] + 2

    @property
    def columnspan(self):
        """Retourne le nombre de colonnes + 1 (pour l'en-tête)."""
        return self.shape[1] + 2

    def grid(self, row: int, column: int):
        """
        Display the DataFrame.

        Parameters
        ----------
        row : int
            Rangée initiale.
        column : int
            Colonne initiale.

        Returns
        -------
        None.

        """
        logger.debug(f'{self!r} .grid({row=}, {column=})')

        self.__grid_params = {'row': row, 'column': column}

        self.build()

        logger.debug(f'\t{self.__widgets.columns=}')
        for i, c in enumerate(self.__widgets.columns):
            c.grid(row=row, column=column+i+3)

        logger.debug(f'\t{self.__widgets=}')
        logger.debug(f'\t{self.__commandes=}')
        for i, ((idx, rang),
                (plus, moins)) in enumerate(zip(self.__widgets.iterrows(),
                                                self.__commandes)):
            for k, w in enumerate((plus, moins, idx)):
                w.grid(row=row+i+1, column=column+k)

            for j, col in enumerate(rang):
                col.grid(row=row+i+1, column=column+k+j+1)

    def pack(self, *args, **kargs):
        pass

    @property
    def children(self):
        """
        Retourne tous les widgets de l'affichage.

        Returns
        -------
        itertools.chain
            Itérateur de tous les widgets.

        """
        logger.debug(f'{self!r} .children')
        return it.chain(self.__widgets.columns,
                        self.__widgets.index,
                        *self.__widgets.values,
                        *self.__commandes)

    def destroy_children(self):
        """
        Détruit les widgets.

        Returns
        -------
        None.

        """
        logger.debug(f'{self!r} .destroy_children')
        logger.debug(f'\t{self.children=}')
        for widget in self.children:
            widget.destroy()

    def destroy(self):
        """
        Assure la destruction des enfants avec la notre.

        Returns
        -------
        None.

        """
        logger.debug(f'{self!r} .destroy')
        self.destroy_children()
        super().destroy()

    def update_grid(self):
        """
        Met l'affichage à jour.

        Returns
        -------
        None.

        """
        logger.debug(f'{self!r} .update_grid')
        self.destroy_children()
        self.grid(**self.__grid_params)


class Formulaire(BaseTableau):
    """Formulaire d'entrée de données."""

    def __init__(self,
                 handler: InterfaceHandler,
                 db: BaseDeDonnées,
                 table: str):
        """
        Crée un formulaire d'entrée de données.

        Parameters
        ----------
        handler : InterfaceHandler
            Gestionnaire d'interface.
        db : BaseDeDonnées
            Base de donnée.
        table : str
            Tableau.

        Returns
        -------
        None.

        """
        logger.debug(f'{self!r} .__init__({handler=}, {db=}, {table=})')
        super().__init__(db, table)
        self.__widgets = pd.DataFrame()
        self.__commandes = []
        self.__handler = handler

    def oublie_pas_la_màj(self, f: Callable, *args):
        """
        Force la mise à jour de la grille.

        À utiliser après un changement à la base de données.
        """
        logger.debug(f'{self!r} .oublie_pas_la_màj({f=}, {args=})')

        def F():
            logger.debug(f'** F() avec {f=} et {args=}.')
            f(*args)
            self.update_grid()

        logger.debug(f'\t{F=}')

        return F

    def effacer(self):
        """
        Effacer les champs du formulaire.

        Returns
        -------
        None.

        """
        logger.debug(f'{self!r} .effacer')
        self.update_grid()
        # TODO: rentrer la date automatiquement

    def soumettre(self):
        """
        Rentre les données dans la base de données.

        Returns
        -------
        None.

        """
        logger.debug(f'{self!r} .soumettre')

        _ = pd.Series({c.cget('text'): [v.get()] for c, v
                       in self.__widgets.loc[0, :].items()})
        logger.debug(f'\t{_=}')

        self.append(_)
        self.effacer()

    def build_commandes(self) -> tuple:
        """
        Construit les widgets de commandes.

        Eg: boutons.

        Returns
        -------
        tuple
            Boutons créés.

        """
        logger.debug(f'{self!r} .build_commandes')

        a = self.__handler.bouton('Effacer', self.effacer)
        logger.debug(f'\t{a=}')

        b = self.__handler.bouton('Soumettre', self.soumettre)
        logger.debug(f'\t{b=}')

        return a, b

    def build(self):
        """
        Construire tous les widgets.

        Returns
        -------
        None.

        """
        logger.debug(f'{self!r} .build')

        self.__widgets = pd.DataFrame(None, columns=self.columns, index=[0])
        logger.debug(f'\t{self.__widgets=}')

        colonnes = filter(lambda x: x != 'index', self.columns)
        colonnes = list(map(self.__handler.texte, colonnes))
        self.__widgets.columns = colonnes
        logger.debug(f'\t{self.__widgets=}')

        logger.debug(f'\t{colonnes=}')
        for col in colonnes:
            df = pd.DataFrame(None,
                              columns=[col],
                              index=[max(self.index, default=0)+1])
            logger.debug(f'\t\t{df=}')

            n = self.__handler.entrée(df, lambda x: None)
            logger.debug(f'\t\t{n=}')

            self.__widgets.loc[0, col] = n
        logger.debug(f'\t{self.__widgets=}')

        logger.debug(f'\t{self.__commandes=}')
        self.__commandes = self.build_commandes()

    @ property
    def rowspan(self):
        """Retourne le nombre de rangées + 1 (pour l'index)."""
        return self.shape[1] + 2

    @ property
    def columnspan(self):
        """Retourne le nombre de colonnes + 1 (pour l'en-tête)."""
        return 2

    def grid(self, row: int, column: int):
        """
        Affiche le formulaire.

        Parameters
        ----------
        row : int
            Rangée initiale.
        column : int
            Colonne initiale.

        Returns
        -------
        None.

        """
        logger.debug(f'{self!r} .grid({row=}, {column=})')
        self.__grid_params = {'row': row, 'column': column}

        self.build()

        for j, (c, v) in enumerate(zip(self.__widgets.columns,
                                       self.__widgets.loc[0, :])):
            c.grid(row=row+j, column=column)
            v.grid(row=row+j, column=column+1)

        for i, c in enumerate(self.__commandes):
            c.grid(row=row+j+1, column=column+i)

    def pack(self, *args, **kargs):
        pass

    @ property
    def children(self):
        """
        Liste les widgets.

        Returns
        -------
        itertools.chain
            Widgets.

        """
        logger.debug(f'{self!r} .children')
        return it.chain(self.__widgets.columns,
                        *self.__widgets.values,
                        self.__commandes)

    def destroy_children(self):
        """
        Détruire les enfants.

        Returns
        -------
        None.

        """
        logger.debug(f'{self!r} .destroy_children')
        for widget in self.children:
            logger.debug(f'\t{widget=}')
            widget.destroy()

    def destroy(self):
        """
        Détruire les enfants, puis nous.

        Returns
        -------
        None.

        """
        logger.debug(f'{self!r} .destroy')
        self.destroy_children()
        super().destroy()

    def update_grid(self):
        """
        Update the grid after a change to the DataFrame.

        Returns
        -------
        None.

        """
        logger.debug(f'{self!r} .update_grid')
        self.destroy_children()
        self.grid(**self.__grid_params)


def main():
    """Exemple d'affichage de base de données."""
    import polytechnique.outils.database
    base, md = polytechnique.outils.database.main()

    import polytechnique.outils.interface.tkinter
    import tkinter

    logger.info('Test d\'interface...')
    racine = tkinter.Tk()
    handler = polytechnique.outils.interface.tkinter.tkHandler(racine)

    logger.info('Tableau...')
    tableau = Tableau(handler, base, 'demo')
    logger.info(f'{tableau.index=}')

    tableau.grid(0, 0)

    racine.mainloop()

    logger.info(
        'On réouvre, pour montrer que les changements sont bien soumis à la base de données...')
    racine = tkinter.Tk()
    handler = polytechnique.outils.interface.tkinter.tkHandler(racine)
    tableau = Tableau(handler, base, 'demo')
    tableau.grid(0, 0)
    racine.mainloop()

    logger.info('On teste le formulaire...')
    racine = tkinter.Tk()
    handler = polytechnique.outils.interface.tkinter.tkHandler(racine)
    formulaire = Formulaire(handler, base, 'demo')
    formulaire.grid(0, 0)
    racine.mainloop()

    logger.info(
        'On réouvre, pour montrer que les changements sont bien soumis à la base de données...')
    racine = tkinter.Tk()
    handler = polytechnique.outils.interface.tkinter.tkHandler(racine)
    tableau = Tableau(handler, base, 'demo')
    tableau.grid(0, 0)
    racine.mainloop()


if __name__ == '__main__':
    main()
