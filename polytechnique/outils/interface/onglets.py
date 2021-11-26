#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Afficher différentes bases de données dans différents onglets.
Created on Tue Nov  9 15:37:45 2021

@author: ejetzer
"""

import pathlib

import configparser as cp
import tkinter as tk

from tkinter import ttk
from typing import Callable

import sqlalchemy as sqla
import pandas as pd

from .df import Tableau
from .tkinter import tkHandler
from ..database import BaseDeDonnées
from ..config import FichierConfig

class OngletConfig(tk.Frame):

    def __init__(self, master, config: FichierConfig):
        self.config = config

        super().__init__(master)
        self.build()

    @property
    def chemin(self):
        return self.config.chemin

    def build(self):
        self.titre_étiquettes = {}
        self.champs = {}
        for titre in self.config.sections():
            section = self.config[titre]

            titre_étiquette = tk.Label(self, text=titre)
            self.titre_étiquettes[titre] = titre_étiquette
            self.champs[titre] = {}

            for champ, valeur in section.items():
                champ_étiquette = tk.Label(self, text=champ)
                champ_variable = tk.StringVar(self, valeur)
                champ_variable.trace_add('write', lambda x, i, m, v=champ_variable: self.update_config())
                champ_entrée = tk.Entry(self, textvariable=champ_variable)

                self.champs[titre][champ] = (champ_étiquette, champ_entrée)

    def update_config(self):
        for section in self.champs:
            for clé, valeur in self.champs[section]:
                self.config[section][clé] = valeur

        self.config.write()

    def subgrid(self):
        colonne = 0
        for titre, étiquette in self.titre_étiquettes.items():
            étiquette.grid(row=0, column=colonne, columnspan=2)
            rangée = 1

            for étiquette, entrée in self.champs[titre].values():
                étiquette.grid(row=rangée, column=colonne)
                entrée.grid(row=rangée, column=colonne+1)
                rangée += 1

            colonne += 2

    def grid(self, *args, **kargs):
        self.subgrid()
        super().grid(*args, **kargs)


class OngletBaseDeDonnées(tk.Frame):

    def __init__(self, master: tk.Tk, db: BaseDeDonnées, table: str, *args, config: FichierConfig = None, **kargs):
        self.config = config
        self.table = table
        self.db = db

        super().__init__(master, *args, **kargs)
        self.build()

    @property
    def adresse(self):
        return self.config.get('bd', 'adresse', fallback='test.db')

    def build(self):
        self.canevas = tk.Canvas(self, width='50c', height='15c')
        défiler_horizontalement = tk.Scrollbar(self, orient='horizontal', command=self.canevas.xview)
        défiler_verticalement = tk.Scrollbar(self, orient='vertical', command=self.canevas.yview)
        self.canevas.configure(xscrollcommand=défiler_horizontalement.set,
                               yscrollcommand=défiler_verticalement.set)
        self.contenant = tk.Frame(self.canevas)
        self.contenant.bind('<Configure>', lambda x: self.canevas.configure(scrollregion=self.canevas.bbox('all')))

        self.tableau = Tableau(tkHandler(self.contenant), self.db, self.table)

        màj = tk.Button(self, text='Màj', command=lambda: self.tableau.update_grid())

        self.défiler = [défiler_horizontalement, défiler_verticalement]
        self.boutons = [màj]

    def subgrid(self):
        self.défiler[0].grid(row=16, column=1, columnspan=1, sticky='we')
        self.défiler[1].grid(row=1, column=2, rowspan=15, sticky='ns')
        self.canevas.grid(row=1, column=1, rowspan=15, sticky='news')
        self.canevas.create_window((30, 15), window=self.contenant)
        self.tableau.grid(0, 0)
        for i, b in enumerate(self.boutons):
            b.grid(row=i, column=0)

    def grid(self, *args, **kargs):
        self.subgrid()
        super().grid(*args, **kargs)


class Onglets(ttk.Notebook):

    def __init__(self, master, config, schema):
        super().__init__(master)

        onglet = OngletConfig(self, config)
        self.add(onglet, text=onglet.chemin)

        tables = config.get('bd', 'tables').strip().split('\n')
        db = BaseDeDonnées(config.get('bd', 'adresse'), schema)
        for nom_table in tables:
            onglet = OngletBaseDeDonnées(self, db, nom_table, config=config)
            self.add(onglet, text=nom_table)

    def grid(self, *args, **kargs):
        for onglet in self.children.values():
            onglet.subgrid()

        super().grid(*args, **kargs)


def main(config: FichierConfig = None, md: sqla.MetaData = None):
    if config is None:
        import polytechnique.outils.config
        config = polytechnique.outils.config.main()

    if md is None:
        import polytechnique.outils.database
        base, md = polytechnique.outils.database.main()

    print('Création de l\'interface...')
    racine = tk.Tk()
    racine.title(config.get('tkinter', 'title', fallback='Demo'))
    onglets = Onglets(racine, config, md)
    print('Interface créée.')

    print('Affichage...')
    onglets.grid(sticky='nsew')
    racine.mainloop()

    return racine, onglets

if __name__ == '__main__':
    main()
