#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Programme ou module pour ...

Créé le Fri Nov 26 15:15:36 2021

@author: ejetzer
"""

import logging
import sys

import tkinter as tk

from pathlib import Path

from ..outils.config import FichierConfig, logger as logcfg
from ..outils.database import BaseDeDonnées, logger as logdb
from ..outils.database.dtypes import logger as logdt
from ..outils.interface.df import logger as logdf
from ..outils.interface.onglets import Onglets, logger as logong
from ..outils.interface.tkinter import logger as logtk

from ..inventaire.modeles import metadata

logger = logging.getLogger(__name__)


def main(cfg='~/Documents/Polytechnique/Inventaire/inventaire.cfg'):
    """Programme de gestion d'inventaire."""
    h = logging.StreamHandler(sys.stderr)
    f = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    h.setFormatter(f)

    logger.addHandler(h)
    logcfg.addHandler(h)
    logdf.addHandler(h)
    logdt.addHandler(h)
    logdb.addHandler(h)
    logong.addHandler(h)
    logtk.addHandler(h)

    h.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    logcfg.setLevel(logging.DEBUG)
    logdf.setLevel(logging.WARNING)
    logdt.setLevel(logging.DEBUG)
    logdb.setLevel(logging.DEBUG)
    logong.setLevel(logging.WARNING)
    logtk.setLevel(logging.WARNING)

    logger.debug(f'{__name__} .main({cfg=})')

    logger.info('Chargement de la configuration...')

    cfg = Path(cfg).expanduser()
    logger.debug(f'{cfg=}')

    config = FichierConfig(cfg)
    logger.debug(f'{config=}')

    for sec in config.sections():
        logger.info(f'[{sec}]')
        for c, v in config[sec].items():
            logger.info(f'{c}: {v}')

    logger.info('Chargement de la base de données...')

    adresse = config.geturl('bd', 'adresse')
    logger.debug(f'{adresse=}')

    base = BaseDeDonnées(adresse, metadata)
    logger.debug(f'{base=}')

    base.initialiser()

    for n, t in base.tables.items():
        logger.info(f'[{n}]')
        for c in t.columns:
            logger.info(f'{c}')

    logger.info(base.select('boites'))
    logger.info(base.select('inventaire'))

    logger.info('Préparation de l\'interface...')
    racine = tk.Tk()
    racine.title(config.get('tkinter', 'title', fallback='Inventaire'))

    logger.info('Chargement de la base de données...')
    onglets = Onglets(racine, config, metadata)

    onglets.grid(sticky='nsew')
    racine.mainloop()
