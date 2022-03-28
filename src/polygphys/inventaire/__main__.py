# -*- coding: utf-8 -*-
"""Programme de gestion et suivi d'inventaire."""

# Bibliothèques standards
import getpass
import tkinter as tk

from pathlib import Path

# Bibliothèques PIPy
import keyring

from sqlalchemy import MetaData

# Imports relatifs
from . import InventaireConfig
from .modeles import créer_dbs
from ..outils.database import BaseDeDonnées
from ..outils.interface.tkinter import Onglets

# Obtenir le fichier de configuration
# Un bon endroit où le placer est le répertoire racine de l'utilisateur.
fichier_config = Path('~/inventaire.cfg').expanduser()
config = InventaireConfig(fichier_config)

# Le mot de passe ne devrait pas être gardé dans le fichier de configuration.
# On utilise le module keyring pour le garder dans le trousseau.
# Le mot de passe reste accessible à tous les programmes Python,
# donc il faut faire attention à ce qu'on exécute comme code sur
# l'ordinateur.
nom = config.get('bd', 'nom')
utilisateur = config.get('bd', 'utilisateur')
mdp_id = f'polygphys.inventaire.main.bd.{nom}.{utilisateur}'
mdp = keyring.get_password('system', mdp_id)

if mdp is None:
    mdp = getpass.getpass('mdp>')
    keyring.set_password('system', mdp_id, mdp)

# On crée la structure de la base de données
metadata = créer_dbs(MetaData())

# On configure l'adresse de la base de données
adresse = f'mysql+pymysql://{utilisateur}:{mdp}@{nom}'
config.set('bd', 'adresse', adresse.replace('%', '%%'))

# On se connecte et on initialise la base de données
base_de_données = BaseDeDonnées(adresse, metadata)
base_de_données.initialiser()

# Configuration de l'interface graphique
racine = tk.Tk()
titre = config.get('tkinter', 'titre')
racine.title(titre)

# Onglets va créer l'affichage pour les tableaux et formulaires
# définis dans le fichier de configuration.
onglets = Onglets(racine, config, metadata, dialect='mysql')

# Aller!
onglets.grid(sticky='nsew')
racine.mainloop()
