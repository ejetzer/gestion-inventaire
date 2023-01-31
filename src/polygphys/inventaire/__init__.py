# -*- coding: utf-8 -*-
"""Programme de gestion d'inventaire."""

# Bibliothèques standard
import tkinter as tk

from pathlib import Path

# Imports relatifs
from ..outils.config import FichierConfig
from ..outils.interface_graphique.tkinter import Tableau
from ..outils.interface_graphique.tkinter.onglets import OngletBaseDeDonnées


class InventaireConfig(FichierConfig):
    """Fichier de configuration de programme d'inventaire."""

    def default(self) -> str:
        """
        Retourne le contenu du fichier default.cfg contenu dans le module.

        Returns
        -------
        str
            Contenu de default.cfg.

        """
        return (Path(__file__).parent / 'default.cfg').open().read()


class TableauInventaire(Tableau):
    pass


class OngletInventaire(OngletBaseDeDonnées):

    def __init__(self, master, db, *args, config: FichierConfig = None, **kargs):
        table = 'inventaire'
        super().__init__(master, db, table, *args, config=config, **kargs)

    def build(self):
        """Construit les widgets."""
        self.canevas = tk.Canvas(self, width='50c', height='15c')
        défiler_horizontalement = tk.Scrollbar(
            self, orient='horizontal', command=self.canevas.xview)
        défiler_verticalement = tk.Scrollbar(
            self, orient='vertical', command=self.canevas.yview)
        self.canevas.configure(xscrollcommand=défiler_horizontalement.set,
                               yscrollcommand=défiler_verticalement.set)

        self.contenant = tk.Frame(self.canevas)

        self.contenant.bind('<Configure>', lambda x: self.canevas.configure(
            scrollregion=self.canevas.bbox('all')))

        self.tableau = Tableau(tkHandler(self.contenant), self.db, self.table)

        màj = tk.Button(self, text='Màj',
                        command=lambda: self.tableau.update_grid())

        importer = tk.Button(self, text='Importer',
                             command=self.importer)

        exporter = tk.Button(self, text='Exporter',
                             command=self.exporter)

        modèle = tk.Button(self, text='Modèle',
                           command=self.exporter_modèle)

        self.défiler = [défiler_horizontalement, défiler_verticalement]

        self.boutons = [màj, importer, exporter, modèle]
