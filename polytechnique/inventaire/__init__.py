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
from ..outils.interface.onglets import Onglets, OngletBaseDeDonnées

from .modeles import metadata

def main(cfg='~/Documents/Polytechnique/Inventaire/inventaire.cfg'):
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
    print(base.select('boites'))
    print(base.select('inventaire'))

    print('Préparation de l\'interface...')
    racine = tk.Tk()
    racine.title(config.get('tkinter', 'title', fallback='Inventaire'))

    print('Chargement de la base de données...')
    onglets = Onglets(racine, config, metadata)

    onglets.grid(sticky='nsew')
    racine.mainloop()


if __name__ == '__main__':
    main()
