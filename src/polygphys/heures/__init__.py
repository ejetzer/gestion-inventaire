#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Programme configurable d'entrée des heures.

Créé le Fri Nov 26 15:15:36 2021

@author: ejetzer
"""

import logging
import sys

import tkinter as tk

from pathlib import Path

from ..outils.config import FichierConfig
from ..outils.database import BaseDeDonnées
from ..outils.interface.tableau import Formulaire
from ..outils.interface.tkinter import tkHandler
from ..outils.journal import Formats

from ..heures.modeles import metadata

logger = logging.getLogger(__name__)


def main(dossier=None):
    """Exemple."""
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)

    fmt = logging.Formatter(Formats().default)
    ch.setFormatter(fmt)

    logger.info('Chargement de la configuration...')
    logger.info('L\'adresse est %r.', dossier)

    if dossier is None:
        if len(sys.argv) > 1:
            dossier = Path(sys.argv[1]).resolve()
        else:
            fichier = Path(__file__).expanduser().resolve()
            dossier = fichier.parent

    cfg = dossier / next(dossier.glob('*.cfg'))
    config = FichierConfig(cfg)

    for sec in config.sections():
        logger.info('[%r]', sec)
        for c, v in config[sec].items():
            logger.info('%r: %r', c, v)

    logger.info('Chargement de la base de données...')
    base = BaseDeDonnées(config.geturl('bd', 'adresse'), metadata)
    base.initialiser()

    for n, t in base.tables.items():
        logger.info('[%r]', n)
        for c in t.columns:
            logger.info('%r', c)
    logger.info(base.select('heures'))

    logger.info('Préparation de l\'interface...')
    racine = tk.Tk()
    racine.title(config.get('tkinter', 'title', fallback='Heures'))

    handler = tkHandler(racine)
    formulaire = Formulaire(handler, base, 'heures')

    formulaire.grid(0, 0)
    racine.mainloop()

def vieux():
    from .vieux.interface import Formulaire as VF
    racine = tk.Tk()
    racine.title('Entrée des heures')
    chemin = Path('~').expanduser() / 'heures.cfg'
    fenêtre = VF(str(chemin), master=racine)
    fenêtre.mainloop()
