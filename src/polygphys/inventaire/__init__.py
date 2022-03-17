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
from ..outils.reseau import DisqueRéseau

from ..inventaire.modeles import créer_dbs


def main(dossier=None):
    """Programme de gestion d'inventaire."""
    logging.debug('dossier = %r', dossier)

    logging.info('Chargement de la configuration...')

    if dossier is None:
        if len(sys.argv) > 1:
            dossier = Path(sys.argv[1]).resolve()
        else:
            fichier = Path(__file__).expanduser().resolve()
            dossier = fichier.parent

    cfg = dossier / next(x.name for x in dossier.glob('*.cfg'))
    logging.debug('cfg = %r', cfg)

    config = FichierConfig(cfg)
    logging.debug('config = %r', config)

    for sec in config.sections():
        logging.info('[%r]', sec)
        for c, v in config[sec].items():
            logging.info('%r: %r', c, v)

    logging.info('Chargement de la base de données...')

    adresse = config.geturl('bd', 'adresse')
    logging.debug('adresse = %r', adresse)

    metadata = créer_dbs(MetaData())
    base = BaseDeDonnées(adresse, metadata)
    logging.debug('base = %r', base)

    base.initialiser()

    for n, t in base.tables.items():
        logging.info('[%r]', n)
        for c in t.columns:
            logging.info('%r', c)

    logging.info(base.select('boites'))
    logging.info(base.select('appareils'))

    logging.info('Préparation de l\'interface...')
    racine = tk.Tk()
    racine.title(config.get('tkinter', 'title', fallback='Inventaire'))

    logging.info('Chargement de la base de données...')
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
    # Informations du disque réseau
    config_réseau = FichierConfig(Path('~/heures.cfg').expanduser())
    chemin = config_réseau.getpath('Volumes', 'chemin')
    adresse = config_réseau.get('Volumes', 'adresse')
    nom = config_réseau.get('Volumes', 'nom')
    mdp = config_réseau.get('Volumes', 'mdp')

    disque = DisqueRéseau(adresse, chemin, 'Z:', nom, mdp)

    SOUS_CHEMIN = Path('Techniciens/Emile_Jetzer/Inventaire/')

    with disque:

        dossier = disque / SOUS_CHEMIN

        if not dossier.exists():
            dossier.mkdir()
            cfg = dossier / 'default.cfg'
            db = dossier / 'inventaire.sqlite'

            with cfg.open('w') as f:
                with (Path(__file__).parent / 'default.cfg').open('r') as g:
                    f.write(g.read().format(db=db))

            db.touch()

        cfg = dossier / next(x.name for x in dossier.glob('*.cfg'))
        logging.debug('cfg = %r', cfg)

        config = FichierConfig(cfg)
        logging.debug('config = %r', config)

        for sec in config.sections():
            logging.info('[%r]', sec)
            for c, v in config[sec].items():
                logging.info('%r: %r', c, v)

        logging.info('Chargement de la base de données...')

        adresse = f"sqlite:////{dossier / config.get('bd', 'nom')}"
        config.set('bd', 'adresse', adresse)
        logging.debug('adresse = %r', adresse)

        metadata = créer_dbs(MetaData())
        base = BaseDeDonnées(adresse, metadata)
        logging.debug('base = %r', base)

        base.initialiser()

        for n, t in base.tables.items():
            logging.info('[%r]', n)
            for c in t.columns:
                logging.info('%r', c)

        logging.info(base.select('boites'))
        logging.info(base.select('appareils'))

        logging.info('Préparation de l\'interface...')
        racine = tk.Tk()
        racine.title(config.get('tkinter', 'title', fallback='Inventaire'))

        logging.info('Chargement de la base de données...')
        onglets = Onglets(racine, config, metadata)

        onglets.grid(sticky='nsew')
        racine.mainloop()
