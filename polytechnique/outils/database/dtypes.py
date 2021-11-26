#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Programme ou module pour ...

Créé le Fri Nov 26 11:46:07 2021

@author: ejetzer
"""

import pathlib
import datetime

import itertools as it

from typing import Union, Any, Callable

import sqlalchemy as sqla
import pandas as pd
import tkinter as tk

from ..config import FichierConfig

TYPES: tuple[dict[str, Union[str, type]]] = ({'config': None,
                                              'python': str,
                                              'pandas': 'object',
                                              'sqlalchemy': sqla.PickleType,
                                              'tk': tk.StringVar},
                                             {'config': 'datetime.date',
                                              'python': datetime.date,
                                              'pandas': 'datetime64[D]',
                                              'sqlalchemy': sqla.Date,
                                              'tk': tk.StringVar},
                                             {'config': 'datetime.datetime',
                                              'python': datetime.datetime,
                                              'pandas': 'datetime64[ns]',
                                              'sqlalchemy': sqla.DateTime,
                                              'tk': tk.StringVar},
                                             {'config': 'datetime.time',
                                              'python': datetime.time,
                                              'pandas': 'datetime64[ns]',
                                              'sqlalchemy': sqla.Time,
                                              'tk': tk.StringVar},
                                             {'config': 'datetime.timedelta',
                                              'python': datetime.timedelta,
                                              'pandas': 'period[ns]',
                                              'sqlalchemy': sqla.Interval,
                                              'tk': tk.StringVar},
                                             {'config': 'str',
                                              'python': str,
                                              'pandas': 'string',
                                              'sqlalchemy': sqla.UnicodeText,
                                              'tk': tk.StringVar},
                                             {'config': 'int',
                                              'python': int,
                                              'pandas': 'int64',
                                              'sqlalchemy': sqla.BigInteger,
                                              'tk': tk.StringVar},
                                             {'config': 'float',
                                              'python': float,
                                              'pandas': 'float64',
                                              'sqlalchemy': sqla.Float,
                                              'tk': tk.StringVar},
                                             {'config': 'bool',
                                              'python': bool,
                                              'pandas': 'boolean',
                                              'sqlalchemy': sqla.Boolean,
                                              'tk': tk.StringVar},
                                             {'config': 'pathlib.Path',
                                              'python': pathlib.Path,
                                              'pandas': 'object',
                                              'sqlalchemy': sqla.PickleType,
                                              'tk': tk.StringVar})

#DATE_TYPES: tuple[str] = ('datetime64[D]', 'datetime64[ns]')

def get_type(de: str, t: Union[type, str], à: str) -> Union[type, str]:
    for s in filter(lambda x: x[de] == t, TYPES):
        return s[à]
    return next(filter(lambda x: x['config'] == None, TYPES))[à]
