#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  2 15:40:02 2021

@author: ejetzer
"""

import tkinter as tk
import sqlite3 as db
import pandas as pd


class Tableau(tk.Frame):

    def __init__(self, master=None, données: pd.DataFrame = None, *args, **kargs):
        self.données = données.copy()

        super().__init__(master, *args, **kargs)

    def grid(self,
             row: int,
             column: int,
             rowspan: int = None,
             columnspan: int = None,
             *args,
             firstrow: int = 0,
             firstcolumn: int = 0,
             **kargs):

        défaut_span = self.données.shape

        if rowspan is None:
            rowspan = défaut_span[0] + 1
        elif columnspan is None:
            columnspan = défaut_span[1] + 1

        tableau = self.données.iloc[firstrow:firstrow+rowspan, firstcolumn:firstcolumn+columnspan]

        colonnes = tableau.columns

        for i, col in enumerate(colonnes):
            pass

        for i, rang in enumerate(tableau.iterrows()):
            pass

        super().grid(row=row, column=column, columnspan=columnspan, rowspan=rowspan)
