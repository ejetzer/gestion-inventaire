#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
msforms.

Suivre les modifications à des fichiers Excel contenant les résultats de
formulaires.

Created on Wed Feb 23 15:15:44 2022

@author: emilejetzer
"""

# import tkinter as tk
import configparser as cp

# from pathlib import Path
from datetime import datetime as dt
# from subprocess import run

import pandas as pd

from ..config import FichierConfig


class MSFormConfig(FichierConfig):
    """Configuration de formulaire."""

    def default(self):
        """
        Configuration par défaut.

        Returns
        -------
        None.

        """
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
    """Formulaire."""

    def __init__(self, config: cp.ConfigParser):
        """
        Formulaire.

        Parameters
        ----------
        config : cp.ConfigParser
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.config = config

    @property
    def fichier(self):
        """
        Fichier des données.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        return self.config.get('formulaire', 'chemin')

    @property
    def colonnes(self):
        """
        Champs du formulaire.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        return self.config.get('formulaire', 'colonnes')

    @property
    def dernière_mise_à_jour(self):
        """
        Dernière mise à jour.

        Returns
        -------
        None.

        """
        self.config.get('màj', 'dernière')

    def convertir_champs(self, vieux_champs: pd.DataFrame) -> pd.DataFrame:
        """
        Convertir les champs.

        Parameters
        ----------
        vieux_champs : pd.DataFrame
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        return vieux_champs.rename(self.config.options('conversion'), axis=1)

    def nettoyer(self, cadre: pd.DataFrame) -> pd.DataFrame:
        """
        Nettoyer les données.

        Parameters
        ----------
        cadre : pd.DataFrame
            DESCRIPTION.

        Returns
        -------
        cadre : TYPE
            DESCRIPTION.

        """
        return cadre

    def nouvelles_entrées(self) -> pd.DataFrame:
        """
        Charger les nouvelles entrées.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        cadre = pd.read_excel(self.fichier, usecols=self.colonnes)
        cadre = self.nettoyer(cadre)
        return cadre.loc[cadre.date >= self.dernière_mise_à_jour.date()]

    def action(self, cadre: pd.DataFrame):
        """
        Action à définir.

        Parameters
        ----------
        cadre : pd.DataFrame
            DESCRIPTION.

        Returns
        -------
        None.

        """
        pass

    def mise_à_jour(self):
        """
        Mise à jour.

        Returns
        -------
        None.

        """
        cadre = self.nouvelles_entrées()
        self.config.set('màj', 'dernière', dt.now().isoformat())
        self.action(cadre)
