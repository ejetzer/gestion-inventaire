#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Programme ou module pour ...

Créé le Fri Nov 26 10:42:59 2021

@author: ejetzer
"""

import tkinter as tk

from tkinter.simpledialog import askstring, askinteger, askfloat
from typing import Callable, Any, Union

import pandas as pd

from ..database.dtypes import get_type
from ..interface import InterfaceHandler


class HTMLÉlémentInterface:

    def __init__(self, master, tag: str, attrs: dict[str, str], contenu: list=None):
        self.master = master
        self.tag = tag
        self.attrs = attrs
        self.contenu = contenu

    def grid(row: int, column: int):
        return str(self)

    def __repr__(self):
        return f'<Élément {tag}>'

    def __str__(self):
        attributs = ' '.join(f'{a}="{b}"' for a, b in self.attrs.items())
        if contenu is None:
            return f'<{self.tag} {attributs} />'
        elif isinstance(contenu, list):
            return f'<{self.tag} {attributs}>\n' + '\n'.join(str(e) for e in self.contenu) + f'</{self.tag}>'

class HTMLTable(HTMLÉlémentInterface):

    def __init__(self, master=None):
        super().__init__(master, 'table')
        self.grille = [[]]

    def grid(row: int, column: int):
        return str(self)



class HTMLCellule(HTMLÉlémentInterface):

    def __init__(self, master: HTMLTable = None):
        super().__init__(master, 'td')

    def grid(row: int, column: int):
        while row >= len(self.master.grille):
            self.master.grille.append([])
        while column >= len(self.master.grille[row]):
            self.master.grille[row].append(None)
        self.master.grille[row][column] = self

        return super().grid(row, column)

class HTMLEntrée(HTMLCellule):

    def __init__(self, master: HTMLTable, texte: str, commande: Callable):
        pass


class HTMLTexte(HTMLCellule):

    def __init__(self, master: HTMLTable, texte: str):
        pass


class HTMLBouton(HTMLCellule):

    def __init__(self, master: HTMLTable, texte: str, commande: Callable):
        pass
