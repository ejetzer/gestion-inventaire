#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Manipulation et affichage de base de données.

Created on Tue Nov  2 15:40:02 2021

@author: ejetzer
"""

import logging

import itertools as it
import tkinter as tk

from typing import Callable, Any, Union
from functools import partial
from inspect import signature

import pandas as pd

from ..database import BaseDeDonnées
from ..database.dtypes import default
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
        logger.debug('db = %r\ttable = %r', db, table)

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
        logger.debug('attr = %r', attr)

        logger.debug('hasattr(BaseDeDonnées, attr) = %r',
                     hasattr(BaseDeDonnées, attr))
        logger.debug('hasattr(pd.DataFrame, attr) = %r',
                     hasattr(pd.DataFrame, attr))
        if hasattr(BaseDeDonnées, attr):
            obj = getattr(self.db, attr)
            logger.debug('obj = %r', obj)

            logger.debug('type(obj) = %r', type(obj))
            if isinstance(obj, Callable):
                sig = signature(obj)
                logger.debug('sig = %r', sig)

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
            msg = f'{self!r} de type {type(self)} n\'a pas d\'attribut {attr}\
, ni (self.__db: BaseDeDonnées, self.df: pandas.DataFrame).'
            raise AttributeError(msg)

    @property
    def df(self) -> pd.DataFrame:
        """Le tableau comme pandas.DataFrame."""
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
        logger.debug('values = %r', values)

        logger.debug('type(values) = %r', type(values))
        if values is None:
            cols, idx = self.columns, [max(self.index, default=-1) + 1]
            values = pd.DataFrame(None, columns=cols, index=[idx])
        elif isinstance(values, pd.Series):
            cols, idx = self.columns, [max(self.index, default=-1) + 1]
            values = pd.DataFrame([values], index=[idx])
        logger.debug('values = %r', values)

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
        logger.debug('handler = %r\tdb = %r\ttable = %r', handler, db, table)
        super().__init__(db, table)
        self.widgets = pd.DataFrame()
        self.commandes = []
        self.handler = handler

    def oublie_pas_la_màj(self, f: Callable, *args) -> Callable:
        """
        Force la mise à jour de la grille.

        À utiliser après un changement à la base de données.

        Parameters
        ----------
        f : Callable
            Fonction à envelopper.
        *args : TYPE
            Arguments transmis à f.

        Returns
        -------
        F : Callable
            Fonction enveloppée.

        """
        logger.debug('f = %r\targs = %r', f, args)

        def F():
            logger.debug('** F() avec f=%r et args=%r.', f, args)
            f(*args)
            self.update_grid()

        logger.debug('F = %r', F)

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
        logger.debug('rangée = %r', rangée)

        a = self.handler.bouton('+', self.oublie_pas_la_màj(self.append))
        b = self.handler.bouton('-', self.oublie_pas_la_màj(self.delete,
                                                            rangée))
        logger.debug('a = %r\tb = %r', a, b)

        return a, b

    def build(self):
        """
        Construire les widgets.

        Returns
        -------
        None.

        """
        self.widgets = self.df.copy()
        logger.debug('widgets = %r', self.widgets)

        colonnes = filter(lambda x: x != 'index', self.columns)
        colonnes = list(map(self.handler.texte, colonnes))
        self.widgets.columns = colonnes
        logger.debug('widgets = %r', self.widgets)

        index = list(map(self.handler.texte, self.index))
        self.widgets.index = index
        logger.debug('widgets = %r', self.widgets)

        I, C = self.widgets.shape
        logger.debug('I = %r\tC = %r', I, C)

        for i, c in it.product(range(I), range(C)):
            logger.debug('i = %r\tc = %r', i, c)

            df = self.iloc()[[i], [c]]
            logger.debug('df = %r', df)

            dtype = self.dtype(self.columns[c])
            logger.debug('dtype = %r', dtype)

            _ = self.handler.entrée(df, self.màj, dtype)
            logger.debug('_ = %r', _)

            self.widgets.iloc[i, c] = _
            logger.debug('widgets = %r', self.widgets)

        self.commandes = list(map(self.build_commandes, self.index))
        logger.debug('commandes = %r', self.commandes)

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
        logger.debug('row = %r\tcolumn = %r', row, column)

        self.__grid_params = {'row': row, 'column': column}

        self.build()

        logger.debug('widgets.columns = %r', self.widgets.columns)
        for i, c in enumerate(self.widgets.columns):
            c.grid(row=row, column=column + i + 3)

        logger.debug('widgets = %r', self.widgets)
        logger.debug('commandes = %r', self.commandes)
        for i, ((idx, rang),
                (plus, moins)) in enumerate(zip(self.widgets.iterrows(),
                                                self.commandes)):
            for k, w in enumerate((plus, moins, idx)):
                w.grid(row=row + i + 1, column=column + k)

            for j, col in enumerate(rang):
                col.grid(row=row + i + 1, column=column + k + j + 1)

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
        return it.chain(self.widgets.columns,
                        self.widgets.index,
                        *self.widgets.values,
                        *self.commandes)

    def destroy_children(self):
        """
        Détruit les widgets.

        Returns
        -------
        None.

        """
        logger.debug('children = %r', self.children)
        for widget in self.children:
            widget.destroy()

    def destroy(self):
        """
        Assure la destruction des enfants avec la notre.

        Returns
        -------
        None.

        """
        self.destroy_children()
        super().destroy()

    def update_grid(self):
        """
        Met l'affichage à jour.

        Returns
        -------
        None.

        """
        self.destroy_children()
        self.grid(**self.__grid_params)


class TableauFiltré(Tableau):

    def __init__(self,
                 handler: InterfaceHandler,
                 db: BaseDeDonnées,
                 table: str):
        self.filtres = []
        super().__init__(handler, db, table)

    @property
    def df(self):
        """Le tableau comme pandas.DataFrame."""
        logger.debug(f'{self!r} .df')
        return self.db.select(self.table, where=self.filtres)


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
        logger.debug('handler = %r\tdb = %r\ttable = %r', handler, db, table)
        super().__init__(db, table)
        self.widgets = pd.DataFrame()
        self.commandes = []
        self.handler = handler

    def oublie_pas_la_màj(self, f: Callable, *args):
        """
        Force la mise à jour de la grille.

        À utiliser après un changement à la base de données.
        """
        logger.debug('f = %r\targs = %r', f, args)

        def F():
            logger.debug('** F() avec %r et %r.', f, args)
            f(*args)
            self.update_grid()

        logger.debug('F = %r', F)

        return F

    def effacer(self):
        """
        Effacer les champs du formulaire.

        Returns
        -------
        None.

        """
        self.update_grid()

    def soumettre(self):
        """
        Rentre les données dans la base de données.

        Returns
        -------
        None.

        """

        _ = {}
        for c, v in self.widgets.loc[0, :].items():
            if hasattr(v, 'get'):
                _[c.cget('text')] = v.get()
            elif isinstance(v, tk.Checkbutton):
                _[c.cget('text')] = v.instate(['selected'])

        _ = pd.Series(_)
        logger.debug('_ = %r', _)

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
        a = self.handler.bouton('Effacer', self.effacer)
        logger.debug('a = %r', a)

        b = self.handler.bouton('Soumettre', self.soumettre)
        logger.debug('b = %r', b)

        return a, b

    def build(self):
        """
        Construire tous les widgets.

        Returns
        -------
        None.

        """

        self.widgets = pd.DataFrame(None, columns=self.columns, index=[0])
        logger.debug('widgets = %r', self.widgets)

        colonnes = filter(lambda x: x != 'index', self.columns)
        colonnes = list(map(self.handler.texte, colonnes))
        self.widgets.columns = colonnes
        logger.debug('widgets = %r', self.widgets)

        logger.debug('colonnes = %r', colonnes)
        for n, col in zip(self.columns, colonnes):
            dtype = self.dtype(n)
            logger.debug('dtype = %r', dtype)

            df = pd.DataFrame(default(dtype),
                              columns=[col],
                              index=[max(self.index, default=0) + 1])
            logger.debug('df = %r', df)

            _ = self.handler.entrée(df, lambda x: None, dtype)
            logger.debug('_ = %r', _)

            self.widgets.loc[0, col] = _
        logger.debug('widgets = %r', self.widgets)

        logger.debug('commandes = %r', self.commandes)
        self.commandes = self.build_commandes()

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
        logger.debug('row = %r\tcolumn = %r', row, column)
        self.__grid_params = {'row': row, 'column': column}

        self.build()

        for j, (c, v) in enumerate(zip(self.widgets.columns,
                                       self.widgets.loc[0, :])):
            c.grid(row=row + j, column=column)
            v.grid(row=row + j, column=column + 1)

        for i, c in enumerate(self.commandes):
            c.grid(row=row + j + 1, column=column + i)

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
        return it.chain(self.widgets.columns,
                        *self.widgets.values,
                        self.commandes)

    def destroy_children(self):
        """
        Détruire les enfants.

        Returns
        -------
        None.

        """
        for widget in self.children:
            logger.debug('widget = %r', widget)
            widget.destroy()

    def destroy(self):
        """
        Détruire les enfants, puis nous.

        Returns
        -------
        None.

        """
        self.destroy_children()
        super().destroy()

    def update_grid(self):
        """
        Update the grid after a change to the DataFrame.

        Returns
        -------
        None.

        """
        self.destroy_children()
        self.grid(**self.__grid_params)


class Filtre(Formulaire):

    def __init__(self,
                 handler: InterfaceHandler,
                 tableau: TableauFiltré):
        self.tableau = tableau
        super().__init__(handler, tableau.db, tableau.table)

    def build(self):
        """
        Construire tous les widgets.

        Returns
        -------
        None.

        """
        self.fenetre = self.handler.fenetre()
        self.handler2 = self.handler.handler(self.fenetre)

        self.widgets = pd.DataFrame(
            None, columns=self.columns, index=[0, 1, 2])
        logger.debug('widgets = %r', self.widgets)

        colonnes = filter(lambda x: x != 'index', self.columns)
        colonnes = list(map(self.handler2.texte, colonnes))
        self.widgets.columns = colonnes
        logger.debug('widgets = %r', self.widgets)

        logger.debug('colonnes = %r', colonnes)
        for n, col in zip(self.columns, colonnes):
            dtype = self.dtype(n)
            logger.debug('dtype = %r', dtype)

            df = pd.DataFrame(default(dtype),
                              columns=[col],
                              index=[max(self.index, default=0) + 1])
            logger.debug('df = %r', df)

            _ = self.handler2.entrée(df, lambda x: None, dtype)
            logger.debug('_ = %r', _)

            self.widgets.loc[0, col] = _
        logger.debug('widgets = %r', self.widgets)

        logger.debug('commandes = %r', self.commandes)
        self.commandes = self.build_commandes()

    def build_commandes(self) -> tuple:
        """
        Construit les widgets de commandes.

        Eg: boutons.

        Returns
        -------
        tuple
            Boutons créés.

        """
        a = self.handler2.bouton('Effacer', self.effacer)
        logger.debug('a = %r', a)

        b = self.handler2.bouton('Filtrer', self.filtrer)
        logger.debug('b = %r', b)

        return a, b

    def build_button(self):
        self.bouton = self.handler.bouton('Filtre', self.afficher_filtre)

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
        logger.debug('row = %r\tcolumn = %r', row, column)
        self.__grid_params = {'row': row, 'column': column}

        self.build_button()

        self.bouton.grid(**self.__grid_params)

    def afficher_filtre(self):
        self.build()

        for j, (c, v) in enumerate(zip(self.widgets.columns,
                                       self.widgets.loc[0, :])):
            c.grid(row=j, column=0)
            v.grid(row=j, column=1)

        for i, c in enumerate(self.commandes):
            c.grid(row=j + 1, column=i)

    def destroy_children(self):
        super().destroy_children()
        self.bouton.destroy()

    def filtrer(self):
        clauses = []

        for c, w in zip(self.columns, self.widgets.loc[0, :]):
            col = self.tables[self.table].columns[c]
            val = w.get()

            logger.debug('col = %r, widget = %r', col, val)

            if val:
                clause = col == w.get()
                logger.debug('clause: %r', clause)
                clauses.append(clause)

        self.tableau.filtres = clauses
        self.tableau.update_grid()


class Graphe(Tableau):

    def build(self):
        pass

    def grid(self):
        pass

    def pack(self):
        pass

    def update_grid(self):
        pass


def main(dossier=None):
    """Exemple d'affichage de base de données."""
    import polygphys.outils.database
    import sys
    import pathlib
    import logging

    logging.basicConfig(level=logging.DEBUG)

    if dossier is None:
        if len(sys.argv) > 1:
            dossier = pathlib.Path(sys.argv[1]).resolve()
        else:
            fichier = pathlib.Path(__file__).expanduser().resolve()
            dossier = fichier.parent.parent.parent

    logger.debug('__file__ = %r', __file__)
    logger.debug('fichier = %r', fichier)
    logger.debug('dossier = %r', dossier)

    base, md = polygphys.outils.database.main(dossier)

    import polygphys.outils.interface.tkinter
    import tkinter

    # logger.info('Test d\'interface...')
    # racine = tkinter.Tk()
    # handler = polygphys.outils.interface.tkinter.tkHandler(racine)

    # logger.info('Tableau...')
    # tableau = Tableau(handler, base, 'demo')
    # logger.info(f'{tableau.index=}')

    # tableau.grid(0, 0)

    # racine.mainloop()

#     logger.info(
#         'On réouvre, pour montrer que les changements sont bien soumis à la \
# base de données...')
#     racine = tkinter.Tk()
#     handler = polygphys.outils.interface.tkinter.tkHandler(racine)
#     tableau = Tableau(handler, base, 'demo')
#     tableau.grid(0, 0)
#     racine.mainloop()

#     logger.info('On teste le formulaire...')
#     racine = tkinter.Tk()
#     handler = polygphys.outils.interface.tkinter.tkHandler(racine)
#     formulaire = Formulaire(handler, base, 'demo')
#     formulaire.grid(0, 0)
#     racine.mainloop()

#     logger.info(
#         'On réouvre, pour montrer que les changements sont bien soumis à la \
# base de données...')
#     racine = tkinter.Tk()
#     handler = polygphys.outils.interface.tkinter.tkHandler(racine)
#     tableau = Tableau(handler, base, 'demo')
#     tableau.grid(0, 0)
#     racine.mainloop()

    logger.info('On essaie le filtre!')
    racine = tkinter.Tk()
    handler = polygphys.outils.interface.tkinter.tkHandler(racine)
    tableau = TableauFiltré(handler, base, 'demo')
    filtre = Filtre(handler, tableau)
    filtre.grid(0, 0)
    tableau.grid(1, 1)
    racine.mainloop()


if __name__ == '__main__':
    main()
