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
from ..outils.interface.onglets import Onglets

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

    print('Préparation de l\'interface...')
    racine = tk.Tk()
    racine.title(config.get('tkinter', 'title', fallback='Inventaire'))

    print('Chargement de la base de données...')
    onglets = Onglets(racine, config, metadata)

    onglets.grid(sticky='nsew')
    racine.mainloop()


if __name__ == '__main__':
    main()
