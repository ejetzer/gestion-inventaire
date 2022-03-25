#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Programme de gestion d'inventaire.

Créé le Fri Nov 26 15:15:36 2021

@author: ejetzer
"""

import tkinter as tk
import keyring
import getpass

from pathlib import Path

from sqlalchemy import MetaData

from ..outils.config import FichierConfig
from ..outils.database import BaseDeDonnées
from ..outils.interface.tkinter.onglets import Onglets
from ..outils.reseau import DisqueRéseau
from ..inventaire.modeles import créer_dbs


class InventaireConfig(FichierConfig):

    def default(self):
        return (Path(__file__).parent / 'default.cfg').open().read()


def main():
    fichier_config = Path('~/inventaire.cfg').expanduser()
    config_locale = InventaireConfig(fichier_config)

    chemin = config_locale.get('disque', 'chemin')
    chemin = str(Path(chemin).expanduser())
    config_locale.set('disque', 'chemin', chemin)

    adresse = config_locale.get('disque', 'adresse')
    nom = config_locale.get('disque', 'nom')
    mdp = keyring.get_password('system',
                               mdp_id := f'polygphys.inventaire.main.disque.{adresse}.{nom}')

    if mdp is None:
        mdp = getpass.getpass('mdp>')
        keyring.set_password('system', mdp_id, mdp)

    with DisqueRéseau(**config_locale['disque'], mdp=mdp) as disque:
        config_disque = InventaireConfig(disque / 'inventaire.cfg')

        metadata = créer_dbs(MetaData())
        nom = config_disque.get('bd', 'nom',
                                fallback=config_locale.get('bd',
                                                           'nom'))
        adresse = f'sqlite:///{disque / nom}'
        config_disque.set('bd', 'adresse', adresse)
        base_de_données = BaseDeDonnées(adresse, metadata)
        base_de_données.initialiser()

        racine = tk.Tk()
        titre = config_disque.get('tkinter', 'titre',
                                  fallback=config_locale.get('tkinter',
                                                             'titre'))
        racine.title(titre)
        onglets = Onglets(racine, config_disque, metadata)
        onglets.grid(sticky='nsew')
        racine.mainloop()
