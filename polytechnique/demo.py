#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Programme d'inventaire avec base de données.

Created on Mon Nov 15 15:17:28 2021

@author: ejetzer
"""

import tkinter as tk
import configparser as cp

from polytechnique.outils.onglets import Onglets
from polytechnique.outils.config import FichierConfig

if __name__ == '__main__':
    config = FichierConfig('référence.config')
    racine = tk.Tk()
    racine.title(config.get('tkinter', 'title', fallback='Demo'))
    onglets = Onglets(racine, config)
    onglets.grid(sticky='nsew')
    racine.mainloop()
