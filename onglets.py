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

from afficher_dataframe import Tableau

class OngletBaseDeDonnées(tk.Frame):

    def __init__(self, master, base_de_données, table, *args, **kargs):
        self.base_de_données = base_de_données
        self.table = table

        super().__init__(master, *args, **kargs)

        self.build()

    def build(self):
        canevas = tk.Canvas(self, width='50c', height='15c')
        défiler_horizontalement = tk.Scrollbar(self, orient='horizontal', command=canevas.xview)
        défiler_verticalement = tk.Scrollbar(self, orient='vertical', command=canevas.yview)
        canevas.configure(xscrollcommand=défiler_horizontalement.set,
                          yscrollcommand=défiler_verticalement.set)
        contenant = tk.Frame(canevas)
        contenant.bind('<Configure>', lambda x: canevas.configure(scrollregion=canevas.bbox('all')))

        cadre = pd.read_sql_table(self.table, 'sqlite:///référence.db', index_col='index')
        tableau = Tableau(contenant, cadre)

        màj = tk.Button(self, text='Màj', command=lambda: tableau.update_grid())
        rangée = tk.Button(self, text='+', command=lambda: tableau.ajouter_rangée())

        self.canevas = canevas
        self.défiler = [défiler_horizontalement, défiler_verticalement]
        self.contenant = contenant
        self.df = cadre
        self.tableau = tableau
        self.boutons = [màj, rangée]

    def subgrid(self):
        self.défiler[0].grid(row=16, column=1, columnspan=1, sticky='we')
        self.défiler[1].grid(row=1, column=2, rowspan=15, sticky='ns')
        self.canevas.grid(row=1, column=1, rowspan=15, sticky='news')
        self.canevas.create_window((30, 15), window=self.contenant)
        self.tableau.grid(0, 0)
        self.boutons[0].grid(row=0, column=0)
        self.boutons[1].grid(row=1, column=0)

    def grid(self, *args, **kargs):
        self.subgrid()
        super().grid(*args, **kargs)



def générer_onglets(onglets, fichier_config):
    config = cp.ConfigParser()
    config.read(fichier_config)

    base_de_données = 'sqlite:///référence.db'
    for nom_table in config.sections():
        onglet = OngletBaseDeDonnées(onglets, base_de_données, nom_table)
        onglets.add(onglet, text=nom_table)
        onglet.subgrid()

if __name__ == '__main__':
    racine = tk.Tk()
    racine.title('Bases de données')

    onglets = ttk.Notebook(racine)
    générer_onglets(onglets, 'référence.config')
    onglets.grid(sticky='nsew')

    racine.mainloop()
