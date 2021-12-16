#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Programme ou module pour ...

Créé le Fri Nov 26 15:15:36 2021

@author: ejetzer
"""

import tkinter as tk

from pathlib import Path

from ..outils.config import FichierConfig
from ..outils.database import BaseDeDonnées
from ..outils.interface.df import Formulaire
from ..outils.interface.tkinter import tkHandler

from ..heures.modeles import metadata


def main(cfg='~/Documents/Polytechnique/Heures/heures.cfg'):
    print('Chargement de la configuration...')
    print(f'L\'adresse est {cfg}.')

    cfg = Path(cfg).expanduser()
    config = FichierConfig(cfg)

    for sec in config.sections():
        print(f'[{sec}]')
        for c, v in config[sec].items():
            print(f'{c}: {v}')

    print('Chargement de la base de données...')
    base = BaseDeDonnées(config.get('bd', 'adresse'), metadata)
    base.initialiser()

    for n, t in base.tables.items():
        print(f'[{n}]')
        for c in t.columns:
            print(f'{c}')
    print(base.select('heures'))

    print('Préparation de l\'interface...')
    racine = tk.Tk()
    racine.title(config.get('tkinter', 'title', fallback='Heures'))

    handler = tkHandler(racine)
    formulaire = Formulaire(handler, base, 'heures')

    formulaire.grid(0, 0)
    racine.mainloop()
