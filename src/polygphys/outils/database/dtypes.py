#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Description et manipulation de types de données.

Créé le Fri Nov 26 11:46:07 2021

@author: ejetzer
"""

import pathlib
import datetime
import logging

from typing import Union, Any

import sqlalchemy as sqla
import tkinter as tk

logger = logging.getLogger(__name__)


TYPES: tuple[dict[str, Union[str, type]]] = ({'config': None,
                                              'python': str,
                                              'pandas': 'object',
                                              'sqlalchemy': sqla.PickleType(),
                                              'tk': tk.StringVar},
                                             {'config': 'datetime.date',
                                              'python': datetime.date,
                                              'pandas': 'datetime64[D]',
                                              'sqlalchemy': sqla.Date(),
                                              'tk': tk.StringVar},
                                             {'config': 'datetime.datetime',
                                              'python': datetime.datetime,
                                              'pandas': 'datetime64[ns]',
                                              'sqlalchemy': sqla.DateTime(),
                                              'tk': tk.StringVar},
                                             {'config': 'datetime.time',
                                              'python': datetime.time,
                                              'pandas': 'datetime64[ns]',
                                              'sqlalchemy': sqla.Time(),
                                              'tk': tk.StringVar},
                                             {'config': 'datetime.timedelta',
                                              'python': datetime.timedelta,
                                              'pandas': 'period[ns]',
                                              'sqlalchemy': sqla.Interval(),
                                              'tk': tk.StringVar},
                                             {'config': 'str',
                                              'python': str,
                                              'pandas': 'string',
                                              'sqlalchemy': sqla.UnicodeText(),
                                              'tk': tk.StringVar},
                                             {'config': 'int',
                                              'python': int,
                                              'pandas': 'int64',
                                              'sqlalchemy': sqla.BigInteger(),
                                              'tk': tk.IntVar},
                                             {'config': 'float',
                                              'python': float,
                                              'pandas': 'float64',
                                              'sqlalchemy': sqla.Float(),
                                              'tk': tk.DoubleVar},
                                             {'config': 'bool',
                                              'python': bool,
                                              'pandas': 'boolean',
                                              'sqlalchemy': sqla.Boolean(),
                                              'tk': tk.IntVar},
                                             {'config': 'pathlib.Path',
                                              'python': pathlib.Path,
                                              'pandas': 'object',
                                              'sqlalchemy': sqla.PickleType(),
                                              'tk': tk.StringVar})

# DATE_TYPES: tuple[str] = ('datetime64[D]', 'datetime64[ns]')


def get_type(de: str, t: Union[Any, type, str], à: str) -> Union[type, str]:
    """
    Retourne un type ou description de type dans le bon format.

    Parameters
    ----------
    de : str
        Format de départ.
    t : Union[Any, type, str]
        Type ou description de type dans le format de départ.
    à : str
        Format final.

    Returns
    -------
    Union[type, str]
        Type ou description de type.

    """
    logger.debug('de = %r\tt = %r\tà = %r', de, t, à)

    def comp(x):
        logger.debug('x[de] = %r', x[de])
        logger.debug('type(x[de]) = %r', type(x[de]))
        logger.debug('t = %r', t)

        return x[de] == t

    for s in filter(comp, TYPES):
        logger.debug('s[à] = %r', s[à])
        return s[à]

    return next(filter(lambda x: x['config'] is None, TYPES))[à]


def default(dtype: str) -> Any:
    """
    Retourne la valeur par défaut pour un type.

    Parameters
    ----------
    dtype : str
        Type de données Pandas.

    Returns
    -------
    Any
        Valeur par défaut du type.

    """
    if 'period' in dtype:
        return datetime.timedelta(0)
    elif 'date' in dtype or 'time' in dtype:
        return datetime.datetime.now()
    else:
        return get_type('pandas', dtype, 'python')()


def column(name: str, dtype: type = str, *args, **kargs) -> sqla.Column:
    """
    Retourne une description de colonne du bon type et nom.

    Parameters
    ----------
    name : str
        Nom de la colonne.
    dtype : type, optional
        Type de la colonne. The default is str.
    *args : TYPE
        Arguments supplémentaires transmis au constructeur de colonne.
    **kargs : TYPE
        Arguments supplémentaires transmis au constructeur de colonne.

    Returns
    -------
    sqlalchemy.Column
        Description de colonne.

    """
    def_val = default(get_type('python', dtype, 'pandas'))
    dtype = get_type('python', dtype, 'sqlalchemy')

    if 'default' not in kargs:
        kargs['default'] = def_val

    return sqla.Column(name, dtype, *args, **kargs)
