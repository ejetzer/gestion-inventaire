#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Programme ou module pour ...

Créé le Fri Nov 26 10:43:12 2021

@author: ejetzer
"""

import logging

import tkinter as tk

from tkinter import ttk
from tkinter.simpledialog import askstring, askinteger, askfloat
from typing import Callable

import pandas as pd

from ..database.dtypes import get_type
from ..interface import InterfaceHandler

logger = logging.getLogger(__name__)


def demander(question: str = '', dtype: type = str):
    """Demander une entrée."""
    if dtype == str:
        return askstring('?', question)
    elif dtype == int:
        return askinteger('?', question)
    elif dtype == float:
        return askfloat('?', question)


def tkHandler(master: tk.Tk) -> InterfaceHandler:
    """Retourne une instance InterfaceHandler pour tk."""
    logger.debug(f'{__name__} .tkHandler {master=}')

    def entrée(value: pd.DataFrame,
               commande: Callable,
               dtype: str = 'object') -> tk.Entry:
        logger.debug(f'{__name__} .tkHandler {value=} {commande=} {dtype=}')

        variable = get_type('pandas', dtype, 'tk')(master, value.iloc[0, 0])
        logger.debug(f'{__name__} .tkHandler {variable=}')
        conversion = get_type('pandas', dtype, 'python')

        def F(x, i, m, v=variable):
            logger.debug(f'{__name__} .tkHandler.F {v=}')

            res = v.get()
            logger.debug(f'{__name__} .tkHandler.F {res=}')

            res = conversion(res)
            logger.debug(f'{__name__} .tkHandler.F {res=}')

            arg = pd.DataFrame(res,
                               index=value.index,
                               columns=value.columns,
                               dtype=dtype)
            logger.debug(f'{__name__} .tkHandler.F {arg=}')

            return commande(arg)

        logger.debug(f'{__name__} .tkHandler {F=}')

        variable.trace_add('write', F)

        logger.debug(f'{__name__} .tkHandler {dtype=}')
        if dtype == 'boolean':
            widget = ttk.Checkbutton(master,
                                     variable=variable,
                                     onvalue=1,
                                     offvalue=0)
        elif dtype in ('int64', 'float64'):
            widget = ttk.Spinbox(master, textvariable=variable)
        else:
            widget = ttk.Entry(master, textvariable=variable)
        logger.debug(f'{__name__} .tkHandler {widget=}')

        return widget

    def texte(s): return tk.Label(master, text=s)
    def bouton(s, c): return tk.Button(master, text=s, command=c)

    return InterfaceHandler(entrée, texte, bouton, demander)
