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

import sqlalchemy as db
import pandas as pd

from .df import Tableau, tkHandler
from .db import BaseDeDonnées
from .config import FichierConfig

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

    def __init__(self, master: tk.Tk, config: FichierConfig, table: str, *args, **kargs):
        self.config = config
        self.table = table

        super().__init__(master, *args, **kargs)
        self.build()

    @property
    def adresse(self):
        return self.config.get('bd', 'adresse', fallback='test.db')

    def build(self):
        canevas = tk.Canvas(self, width='50c', height='15c')
        défiler_horizontalement = tk.Scrollbar(self, orient='horizontal', command=canevas.xview)
        défiler_verticalement = tk.Scrollbar(self, orient='vertical', command=canevas.yview)
        canevas.configure(xscrollcommand=défiler_horizontalement.set,
                          yscrollcommand=défiler_verticalement.set)
        contenant = tk.Frame(canevas)
        contenant.bind('<Configure>', lambda x: canevas.configure(scrollregion=canevas.bbox('all')))

        self.tableau = Tableau(tkHandler(contenant), BaseDeDonnées(self.config), self.table)

        màj = tk.Button(self, text='Màj', command=lambda: self.tableau.update_grid())

        self.canevas = canevas
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

    def __init__(self, master, config):
        super().__init__(master)

        onglet = OngletConfig(self, config)
        self.add(onglet, text=onglet.chemin)

        tables = filter(lambda x: x in config.sections(),
                        config.get('bd', 'tables').strip().split('\n'))
        for nom_table in tables:
            onglet = OngletBaseDeDonnées(self, config, nom_table)
            self.add(onglet, text=nom_table)

    def grid(self, *args, **kargs):
        for onglet in self.children.values():
            onglet.subgrid()

        super().grid(*args, **kargs)


if __name__ == '__main__':
    racine = tk.Tk()
    racine.title('Bases de données')

    config = FichierConfig('référence.config')

    onglets = Onglets(racine, config)
    onglets.grid(sticky='nsew')

    racine.mainloop()
