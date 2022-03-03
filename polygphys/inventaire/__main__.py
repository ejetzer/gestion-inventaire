#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Exemple d'inventaire.

Créé le Thu Dec 16 13:37:19 2021

@author: ejetzer
"""

import platform

from pathlib import Path

from . import main

CHEMINS = {'Darwin': Path('/Volumes/GeniePhysique/Techniciens/'),
           'Windows': Path(r'Z:'),
           None: Path('~/.inventaire').expanduser().resolve()}
SOUS_CHEMIN = Path('Emile_Jetzer/Inventaire/')

if __name__ == '__main__':
    dossier = CHEMINS.get(platform.system(), CHEMINS[None]) / SOUS_CHEMIN

    if not dossier.exists():
        dossier.mkdir()
        cfg = dossier / 'default.cfg'
        db = dossier / 'inventaire.sqlite'

        with cfg.open('w') as f:
            f.write(f'''[bd]
    adresse = sqlite:///{db}
tables =
    personnes
	locaux
	portes
	etageres
	appareils
	boites
	emprunts
	utilisation_boites
formulaires = 
	personnes
	locaux
	portes
	etageres
	appareils
	boites
	emprunts
	utilisation_boites

[tkinter]
title: Inventaire du département de génie physique à Polytechnique Montréal
''')

        db.touch()
        
    main()
