#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suivre les modifications à des fichiers Excel contenant les résultats de
formulaires.

Created on Wed Feb 23 15:15:44 2022

@author: emilejetzer
"""

import subprocess

import tkinter as tk
import configparser as cp

from pathlib import Path
from datetime import datetime as dt
from subprocess import run

import pandas as pd

from ..config import FichierConfig


class MSFormConfig(FichierConfig):

    def default(self):
        return f'''[default]
    auto: True
    class: {type(self)}

[formulaire]
    chemin: ./form.xlsx
    colonnes: date, nom

[màj]
    dernière:
'''


class MSForm:

    def __init__(self, config: cp.ConfigParser):
        self.config = config

    @property
    def fichier(self):
        return self.config.get('formulaire', 'chemin')

    @property
    def colonnes(self):
        return self.config.get('formulaire', 'colonnes')

    @property
    def dernière_mise_à_jour(self):
        self.config.get('màj', 'dernière')

    def convertir_champs(self, vieux_champs: pd.DataFrame) -> pd.DataFrame:
        return vieux_champs.rename(self.config.options('conversion'), axis=1)

    def nettoyer(self, cadre: pd.DataFrame) -> pd.DataFrame:
        return cadre

    def nouvelles_entrées(self) -> pd.DataFrame:
        cadre = pd.read_excel(self.fichier, usecols=self.colonnes)
        cadre = self.nettoyer(cadre)
        return cadre.loc[cadre.date >= self.dernière_mise_à_jour.date()]

    def action(self, cadre: pd.DataFrame):
        pass

    def mise_à_jour(self):
        cadre = self.nouvelles_entrées()
        self.config.set('màj', 'dernière', dt.now().isoformat())
        self.action(cadre)
