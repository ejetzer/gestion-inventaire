#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Programme d'inventaire avec base de données.

Created on Mon Nov 15 15:17:28 2021

@author: ejetzer
"""

import tkinter as tk
import configparser as cp

from outils.onglets import Onglets

config = cp.ConfigParser()
config.read(fichier_config := 'référence.config', encoding='utf-8')

racine = tk.Tk()
racine.title(config['tkinter']['title'])

onglets = Onglets(racine, config, fichier_config)
onglets.grid(sticky='nsew')

racine.mainloop()
