#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Programme configurable d'entrée des heures.

Créé le Fri Nov 26 15:15:36 2021

@author: ejetzer
"""

import logging

import tkinter as tk

from pathlib import Path

from ..outils.config import FichierConfig
from ..outils.base_de_donnees import BaseDeDonnées
from ..outils.interface_graphique.tableau import Formulaire
from ..outils.interface_graphique import InterfaceHandler
from ..outils.interface_graphique.tkinter import tkHandler
from ..outils.journal import Formats, Journal
from ..outils.reseau import DisqueRéseau

from .modeles import metadata as md


class FeuilleDeTemps:
    """Feuille de temps."""

    def __init__(self, config: FichierConfig, handler: InterfaceHandler):
        self.config = config

        db = BaseDeDonnées(self.adresse, md)
        formulaire = Formulaire(handler, db, self.table)
        self.journal = Journal(logging.INFO, self.dossier, formulaire)

    @property
    def adresse(self):
        return self.config.geturl('FeuilleDeTemps', 'adresse')

    @property
    def table(self):
        return self.config.get('FeuilleDeTemps', 'table')

    @property
    def dossier(self):
        return self.config.getpath('FeuilleDeTemps', 'dossier')

    @property
    def formulaire(self):
        return self.journal.tableau

    @property
    def répertoire(self):
        return self.journal.repo

    @property
    def db(self):
        return self.formulaire.db

    def __enter__(self):
        return self

    def __exit__(self, exception_type, value, traceback):
        return None

    # Méthodes de comptabilité

    def répartition(self):
        pass

    def compte(self):
        pass

    def exporter(self):
        pass


def main(dossier=None):
    """Exemple."""
    logging.basicConfig(level=logging.DEBUG, format=Formats().details)

    chemin = Path('~/heures.cfg').expanduser()
    config = FichierConfig(chemin)

    racine = tk.Tk()

    titre = config.get('tkinter', 'title', fallback='Heures')
    racine.title(titre)

    handler = tkHandler(racine)
    with DisqueRéseau(**config['DisqueRéseau']):
        with FeuilleDeTemps(config, handler) as feuille_de_temps:
            feuille_de_temps.formulaire.grid(0, 0)
            racine.mainloop()


def vieux():
    """
    Programme fonctionnel, mais mal intégré aux fonctionnalités du paquet.

    Returns
    -------
    None.

    """
    from .vieux.interface import Formulaire as VF
    racine = tk.Tk()
    racine.title('Entrée des heures')
    chemin = Path('~').expanduser() / 'heures.cfg'
    fenêtre = VF(str(chemin), master=racine)
    fenêtre.mainloop()
