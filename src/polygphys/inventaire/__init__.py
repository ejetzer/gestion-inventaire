#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Programme de gestion d'inventaire.

Créé le Fri Nov 26 15:15:36 2021

@author: ejetzer
"""

import logging
import sys
import platform

import tkinter as tk

from pathlib import Path

from sqlalchemy import MetaData

from ..outils.config import FichierConfig
from ..outils.database import BaseDeDonnées
from ..outils.interface.tkinter.onglets import Onglets
from ..outils.journal import Formats

from ..inventaire.modeles import créer_dbs

logger = logging.getLogger(__name__)
log_format = Formats().détails
niveau = logging.DEBUG


def main(dossier=None):
    """Programme de gestion d'inventaire."""
    h = logging.StreamHandler(sys.stdout)
    f = logging.Formatter(log_format)
    h.setFormatter(f)

    logging.basicConfig(handlers=[h], level=niveau)

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

    metadata = créer_dbs(MetaData())
    base = BaseDeDonnées(adresse, metadata)
    logger.debug('base = %r', base)

    base.initialiser()

    for n, t in base.tables.items():
        logger.info('[%r]', n)
        for c in t.columns:
            logger.info('%r', c)

    logger.info(base.select('boites'))
    logger.info(base.select('appareils'))

    logger.info('Préparation de l\'interface...')
    racine = tk.Tk()
    racine.title(config.get('tkinter', 'title', fallback='Inventaire'))

    logger.info('Chargement de la base de données...')
    onglets = Onglets(racine, config, metadata)

    onglets.grid(sticky='nsew')
    racine.mainloop()


def script():
    """
    Script pour inventaire partagé.

    Returns
    -------
    None.

    """
    CHEMINS = {'Darwin': Path('/Volumes/GeniePhysique/Techniciens/'),
               'Windows': Path(r'Z:'),
               None: Path('~/.inventaire').expanduser().resolve()}
    SOUS_CHEMIN = Path('Emile_Jetzer/Inventaire/')

    dossier = CHEMINS.get(platform.system(), CHEMINS[None]) / SOUS_CHEMIN

    if not dossier.exists():
        dossier.mkdir()
        cfg = dossier / 'default.cfg'
        db = dossier / 'inventaire.sqlite'

        with cfg.open('w') as f:
            with (Path(__file__).parent / 'default.cfg').open('r') as g:
                f.write(g.read().format(db=db))

        db.touch()

    main(dossier)
