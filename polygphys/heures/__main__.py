#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Exemple de programme de gestion des heures.

Créé le Thu Dec 16 13:37:07 2021

@author: ejetzer
"""

import tkinter

from pathlib import Path

# from . import main

from .vieux.interface import Formulaire

if __name__ == '__main__':
    racine = tkinter.Tk()
    racine.title('Entrée des heures')
    chemin = Path(__file__).parent / 'vieux' / 'Configuration.txt'
    fenêtre = Formulaire(str(chemin), master=racine)
    fenêtre.mainloop()
