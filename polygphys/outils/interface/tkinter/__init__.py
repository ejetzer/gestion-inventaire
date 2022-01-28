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

from ...database.dtypes import get_type
from ...interface import InterfaceHandler

logger = logging.getLogger(__name__)


def tkHandler(master: tk.Tk, editable: bool = True) -> InterfaceHandler:
    """Retourne une instance InterfaceHandler pour tk."""
    logger.debug('master = %r', master)

    def demander(question: str = '', dtype: type = str):
        """Demander une entrée."""
        if dtype == str:
            return askstring('?', question)
        elif dtype == int:
            return askinteger('?', question)
        elif dtype == float:
            return askfloat('?', question)

    def entrée(value: pd.DataFrame,
               commande: Callable,
               dtype: str = 'object',
               editable: bool = editable) -> tk.Entry:
        logger.debug('value = %r\tcommande = %r\tdtype = %r',
                     value, commande, dtype)

        variable = get_type('pandas', dtype, 'tk')(master, value.iloc[0, 0])
        logger.debug('variable = %r', variable)
        conversion = get_type('pandas', dtype, 'python')
        logger.debug('conversion = %r', conversion)

        def F(x, i, m, v=variable):
            logger.debug('v = %r', v)

            res = v.get()
            logger.debug('res = %r', res)

            res = conversion(res)
            logger.debug('res = %r', res)

            arg = pd.DataFrame(res,
                               index=value.index,
                               columns=value.columns,
                               dtype=dtype)
            logger.debug('arg = %r', arg)

            return commande(arg)

        logger.debug('F = %r', F)

        variable.trace_add('write', F)

        logger.debug('dtype = %r', dtype)
        if not editable:
            widget = ttk.Label(master, textvariable=variable)
        elif dtype == 'boolean':
            widget = ttk.Checkbutton(master,
                                     variable=variable)
        elif dtype in ('int64', 'float64'):
            widget = ttk.Spinbox(master, textvariable=variable)
        else:
            widget = ttk.Entry(master, textvariable=variable)
        logger.debug('widget = %r', widget)

        return widget

    def texte(s): return tk.Label(master, text=s)
    def bouton(s, c): return tk.Button(master, text=s, command=c)

    def fenetre(): return tk.Toplevel(master)

    return InterfaceHandler(entrée,
                            texte,
                            bouton,
                            demander,
                            fenetre,
                            tkHandler)
