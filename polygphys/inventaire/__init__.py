#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Programme de gestion d'inventaire.

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
from ..outils.interface.tableau import logger as logdf
from ..outils.interface.tkinter.onglets import Onglets, logger as logong
from ..outils.interface.tkinter import logger as logtk
from ..outils.journal import Formats

from ..inventaire.modeles import metadata

logger = logging.getLogger(__name__)
loggers = [logcfg, logdb, logdt, logdf, logong, logtk]
log_format = Formats().détails
niveau = logging.DEBUG


def main(dossier=None):
    """Programme de gestion d'inventaire."""
    h = logging.StreamHandler(sys.stdout)
    f = logging.Formatter(log_format)
    h.setFormatter(f)

    logger.addHandler(h)
    logger.setLevel(niveau)
    for journal in loggers:
        journal.addHandler(h)
        journal.setLevel(niveau)

    logger.debug('dossier = %r', dossier)

    logger.info('Chargement de la configuration...')

    if dossier is None:
        if len(sys.argv) > 1:
            dossier = Path(sys.argv[1]).resolve()
        else:
            fichier = Path(__file__).expanduser().resolve()
            dossier = fichier.parent

    cfg = dossier / next(x.name for x in dossier.glob('*.cfg'))
    logger.debug('cfg = %r', cfg)

    config = FichierConfig(cfg)
    logger.debug('config = %r', config)

    for sec in config.sections():
        logger.info('[%r]', sec)
        for c, v in config[sec].items():
            logger.info('%r: %r', c, v)

    logger.info('Chargement de la base de données...')

    adresse = config.geturl('bd', 'adresse')
    logger.debug('adresse = %r', adresse)

    base = BaseDeDonnées(adresse, metadata)
    logger.debug('base = %r', base)

    base.initialiser()

    for n, t in base.tables.items():
        logger.info('[%r]', n)
        for c in t.columns:
            logger.info('%r', c)

    logger.info(base.select('boites'))
    logger.info(base.select('inventaire'))

    logger.info('Préparation de l\'interface...')
    racine = tk.Tk()
    racine.title(config.get('tkinter', 'title', fallback='Inventaire'))

    logger.info('Chargement de la base de données...')
    onglets = Onglets(racine, config, metadata)

    onglets.grid(sticky='nsew')
    racine.mainloop()
