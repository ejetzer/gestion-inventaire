#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Programme pour afficher et modifier visuellement des DataFrames Pandas.

Created on Tue Nov  2 15:40:02 2021

@author: ejetzer
"""

import itertools as it
import tkinter as tk

import sqlalchemy as db
import pandas as pd


class Tableau:
    """Wrapper for pandas.DataFrame & tkinter.Frame."""

    def __init__(self, master, tableau: pd.DataFrame):
        """Wrap DataFrame & Frame."""
        self.tableau = tableau
        self.master = master

        self.__init_tableau()

    def __init_rangée_titres(self):
        return [tk.Label(self.master, text=col) for col in self.tableau.columns]

    def __init_colonne_index(self):
        return [tk.Label(self.master, text=k) for k, rang in self.tableau.iterrows()]

    def __init_tableau_contenu(self):
        entrées = []

        for k, rang in self.tableau.iterrows():
            entrées.append([])

            for col in rang:
                variable = tk.StringVar(self.master, col)
                variable.trace_add('write', lambda x, i, m, v=variable: self.update_tableau())
                entrée = tk.Entry(self.master, textvariable=variable)
                entrées[-1].append(entrée)

        return entrées

    def __init_tableau(self):
        self.rangée_titres = self.__init_rangée_titres()
        self.colonne_index = self.__init_colonne_index()
        self.tableau_contenu = self.__init_tableau_contenu()

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

        for i, col in enumerate(self.rangée_titres[cols]):
            col.grid(row=row, column=column+i+1)

        for i, (idx, rang) in enumerate(zip(self.colonne_index[rangs], self.tableau_contenu[rangs])):
            idx.grid(row=row+i+1, column=column)

            for j, col in enumerate(rang[cols]):
                col.grid(row=row+i+1, column=column+j+1)


    def update_tableau(self, *args, **kargs):
        for idx, rang in zip(self.colonne_index, self.tableau_contenu):
            for col, val in zip(self.rangée_titres, rang):
                self.tableau.loc[idx['text'], col['text']] = val.get()

    def update_grid(self):
        'Update the grid after a change to the DataFrame'
        for widget in it.chain(self.rangée_titres, self.colonne_index, *self.tableau_contenu):
            widget.destroy()

        self.__init_tableau()
        self.grid(**self.__grid_params)

    def ajouter_rangée(self):
        self.tableau = self.tableau.append(pd.Series(), ignore_index=True)
        self.update_grid()

if __name__ == '__main__':
    racine = tk.Tk()
    racine.title('Base de données')

    canevas = tk.Canvas(racine, width='50c', height='15c')
    défiler_horizontalement = tk.Scrollbar(racine, orient='horizontal', command=canevas.xview)
    défiler_verticalement = tk.Scrollbar(racine, orient='vertical', command=canevas.yview)
    canevas.configure(xscrollcommand=défiler_horizontalement.set,
                      yscrollcommand=défiler_verticalement.set)
    contenant = tk.Frame(canevas)
    contenant.bind('<Configure>', lambda x: canevas.configure(scrollregion=canevas.bbox('all')))

    cadre = pd.read_sql_table('test', 'sqlite:///référence.db', index_col='index')
    tableau = Tableau(contenant, cadre)

    màj = tk.Button(racine, text='Màj', command=lambda: tableau.update_grid())
    rangée = tk.Button(racine, text='+', command=lambda: tableau.ajouter_rangée())

    défiler_horizontalement.grid(row=16, column=1, columnspan=1, sticky='we')
    défiler_verticalement.grid(row=1, column=2, rowspan=15, sticky='ns')
    canevas.grid(row=1, column=1, rowspan=15, sticky='news')
    canevas.create_window((30, 15), window=contenant)
    tableau.grid(0, 0)
    màj.grid(row=0, column=0)
    rangée.grid(row=1, column=0)
    racine.mainloop()

    engine = db.create_engine('sqlite:///référence.db')
    with engine.begin() as con:
        tableau.tableau.to_sql('test', con, if_exists='replace')
