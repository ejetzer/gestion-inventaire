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
    config = InventaireConfig(fichier_config)

    nom = config.get('bd', 'nom')
    utilisateur = config.get('bd', 'utilisateur')
    mdp_id = f'polygphys.inventaire.main.bd.{nom}.{utilisateur}'
    mdp = keyring.get_password('system', mdp_id)

    if mdp is None:
        mdp = getpass.getpass('mdp>')
        keyring.set_password('system', mdp_id, mdp)

    metadata = créer_dbs(MetaData())
    adresse = f'mysql+pymysql://{utilisateur}:{mdp}@{nom}'
    config.set('bd', 'adresse', adresse.replace('%', '%%'))
    base_de_données = BaseDeDonnées(adresse, metadata)
    base_de_données.initialiser()

    racine = tk.Tk()
    titre = config.get('tkinter', 'titre')
    racine.title(titre)
    onglets = Onglets(racine, config, metadata, dialect='mysql')
    onglets.grid(sticky='nsew')
    racine.mainloop()
