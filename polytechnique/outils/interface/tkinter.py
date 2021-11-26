#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Programme ou module pour ...

Créé le Fri Nov 26 10:43:12 2021

@author: ejetzer
"""

import tkinter as tk

from tkinter.simpledialog import askstring, askinteger, askfloat
from typing import Callable, Any, Union

import pandas as pd

from ..database.dtypes import get_type
from ..interface import InterfaceHandler


def demander(question: str = '', dtype: type = str):
    if dtype == str:
        return askstring('?', question)
    elif dtype == int:
        return askinteger('?', question)
    elif dtype == float:
        return askfloat('?', question)

def tkHandler(master: tk.Tk) -> InterfaceHandler:
    def entrée(value: pd.DataFrame, commande: Callable, dtype: str = 'object') -> tk.Entry:
        variable = get_type('pandas', dtype, 'tk')(master, value.iloc[0, 0])
        conversion = get_type('pandas', dtype, 'python')

        variable.trace_add('write', lambda x, i, m, v=variable: commande(pd.DataFrame(conversion(v.get()),
                                                                                      index=value.index,
                                                                                      columns=value.columns,
                                                                                      dtype=dtype)))

        if dtype == 'boolean':
            widget = Tkinter.Checkbutton(master, variable=variable)
        else:
            widget = tk.Entry(master, textvariable=variable)

        return widget

    texte = lambda s: tk.Label(master, text=s)
    bouton = lambda s, c: tk.Button(master, text=s, command=c)

    return InterfaceHandler(entrée, texte, bouton, demander)
