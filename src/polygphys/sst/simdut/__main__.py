# -*- coding: utf-8 -*-
"""Transmettre les nouvelles inscriptions au SIMDUT."""

# Bibliothèque standard
from pathlib import Path
import time

# Bibliothèque PIPy
import schedule

# Imports relatifs
from . import SSTSIMDUTInscriptionConfig, SSTSIMDUTInscriptionForm
from ...outils.reseau import OneDrive

chemin_config = Path('~').expanduser() / 'simdut.cfg'
config = SSTSIMDUTInscriptionConfig(chemin_config)

dossier = OneDrive('',
                   config.get('onedrive', 'organisation'),
                   config.get('onedrive', 'sous-dossier'),
                   partagé=True)
fichier = dossier / config.get('formulaire', 'nom')
config.set('formulaire', 'chemin', str(fichier))

formulaire = SSTSIMDUTInscriptionForm(config)

schedule.every().monday.at('09:00').do(formulaire.mise_à_jour)

formulaire.mise_à_jour()
while True:
    schedule.run_pending()
    time.sleep(1)
