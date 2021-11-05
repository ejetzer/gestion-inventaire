#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Programme pour afficher et modifier visuellement des DataFrames Pandas.

Created on Tue Nov  2 15:40:02 2021

@author: ejetzer
"""

import tkinter as tk
import sqlalchemy as db
import pandas as pd


class Tableau(tk.Frame):

    def __init__(self, master, tableau: pd.DataFrame, *args, **kargs):
        self.tableau = tableau.copy()

        super().__init__(master, *args, **kargs)
        self.__init_tableau(self.tableau)

    def __init_rangée_titres(self, tableau: pd.DataFrame):
        return [tk.Label(self, text=col) for col in tableau.columns]

    def __init_colonne_index(self, tableau: pd.DataFrame):
        return [tk.Label(self, text=k) for k, rang in tableau.iterrows()]

    def __init_tableau_contenu(self, tableau: pd.DataFrame):
        entrées = []

        for k, rang in tableau.iterrows():
            entrées.append([])

            for col in rang:
                variable = tk.StringVar(self, col)
                variable.trace_add('write', lambda x, i, m, v=variable: self.update_tableau())
                entrée = tk.Entry(self, textvariable=variable)
                entrées[-1].append(entrée)

        return entrées

    def __init_tableau(self, tableau):
        self.rangée_titres = self.__init_rangée_titres(tableau)
        self.colonne_index = self.__init_colonne_index(tableau)
        self.tableau_contenu = self.__init_tableau_contenu(tableau)

    def grid(self,
             row: int,
             column: int,
             rowspan: int = None,
             columnspan: int = None,
             *args,
             firstrow: int = 0,
             firstcolumn: int = 0,
             **kargs):

        défaut_span = self.tableau.shape

        if rowspan is None: rowspan = défaut_span[0] + 1
        if columnspan is None: columnspan = défaut_span[1] + 1

        cols = slice(firstcolumn, firstcolumn+columnspan)
        rangs = slice(firstrow, firstrow+rowspan)

        for i, col in enumerate(self.rangée_titres[cols]):
            col.grid(row=0, column=i+1)

        for i, (idx, rang) in enumerate(zip(self.colonne_index[rangs], self.tableau_contenu[rangs])):
            idx.grid(row=i+1, column=0)

            for j, col in enumerate(rang[cols]):
                col.grid(row=i+1, column=j+1)

        super().grid(row=row, column=column, columnspan=columnspan, rowspan=rowspan)

    def update_tableau(self, *args, **kargs):
        for idx, rang in zip(self.colonne_index, self.tableau_contenu):
            for col, val in zip(self.rangée_titres, rang):
                self.tableau.loc[idx['text'], col['text']] = val.get()

if __name__ == '__main__':
    racine = tk.Tk()
    cadre = pd.read_sql_table('test', 'sqlite:///référence.db', index_col='index')
    tableau = Tableau(racine, cadre)
    tableau.grid(0, 0)
    racine.mainloop()

    engine = db.create_engine('sqlite:///référence.db')
    with engine.begin() as con:
        tableau.tableau.to_sql('test', con, if_exists='replace')
