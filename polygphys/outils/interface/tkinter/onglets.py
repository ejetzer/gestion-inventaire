#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Afficher différentes bases de données dans différents onglets.

Created on Tue Nov  9 15:37:45 2021

@author: ejetzer
"""

import pathlib
import logging
import sys

import tkinter as tk

from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from pathlib import Path

import sqlalchemy as sqla

from ..tableau import Tableau, Formulaire, Filtre
from ..tkinter import tkHandler
from ...database import BaseDeDonnées
from ...config import FichierConfig

logger = logging.getLogger(__name__)


class OngletConfig(tk.Frame):
    """Onglet de configuration."""

    def __init__(self, master: tk.Frame, config: FichierConfig):
        """
        Crée un onglet de configuration.

        Parameters
        ----------
        master : tk.Frame
            Maître dans tk.
        config : FichierConfig
            Configuration.

        Returns
        -------
        None.

        """
        logger.debug('master = %r\tconfig = %r', master, config)
        self.config = config

        super().__init__(master)
        self.build()

    def __repr__(self):
        """Affiche les informations de base sur l'objet."""
        return f'<{type(self)} at {hex(id(self))}>'

    @property
    def chemin(self) -> pathlib.Path:
        """
        Retourne le chemin vers le fichier de configuration.

        Returns
        -------
        pathlib.Path
            Chemin vers le fichier de configuration.

        """
        return self.config.chemin

    def build(self):
        """
        Construire les widgets.

        Returns
        -------
        None.

        """

        self.titre_étiquettes = {}
        self.champs = {}

        logger.debug('self.config.sections() = %r', self.config.sections())
        for titre in self.config.sections():
            logger.debug('titre = %r', titre)

            section = self.config[titre]
            logger.debug('section = %r')

            titre_étiquette = tk.Label(self, text=titre)
            self.titre_étiquettes[titre] = titre_étiquette
            self.champs[titre] = {}
            logger.debug('self.titre_étiquettes = %r', self.titre_étiquettes)
            logger.debug('self.champs = %r', self.champs)

            logger.debug('section.items() = %r', section.items())
            for champ, valeur in section.items():
                logger.debug('champ = %r\tvaleur = %r', champ, valeur)

                champ_étiquette = tk.Label(self, text=champ)
                champ_variable = tk.StringVar(self, valeur)
                champ_variable.trace_add(
                    'write',
                    lambda x, i, m, v=champ_variable: self.update_config())
                champ_entrée = tk.Entry(self, textvariable=champ_variable)

                self.champs[titre][champ] = (champ_étiquette, champ_entrée)
                logger.debug('self.champs = %r', self.champs)

    def update_config(self):
        """
        Mettre la configuration à jour.

        Returns
        -------
        None.

        """

        logger.debug('self.champs = %r', self.champs)
        for section in self.champs:
            logger.debug('section = %r', section)

            for clé, valeur in self.champs[section]:
                logger.debug('clé = %r\tvaleur = %r', clé, valeur)
                self.config[section][clé] = valeur

        self.config.write()

    def subgrid(self):
        """
        Affichage des widgets.

        Returns
        -------
        None.

        """
        logger.debug('self.titre_étiquettes = %r', self.titre_étiquettes)
        colonne = 0
        for titre, étiquette in self.titre_étiquettes.items():
            logger.debug('titre = %r\tétiquette = %r', titre, étiquette)
            étiquette.grid(row=0, column=colonne, columnspan=2)
            rangée = 1

            logger.debug('self.champs = %r', self.champs)
            for étiquette, entrée in self.champs[titre].values():
                logger.debug('étiquette = %r\tentrée = %r', étiquette, entrée)
                étiquette.grid(row=rangée, column=colonne)
                entrée.grid(row=rangée, column=colonne+1)
                rangée += 1

            colonne += 2

    def grid(self, *args, **kargs):
        """
        Affichage de l'onglet.

        Parameters
        ----------
        *args : TYPE
            Arguments transmis à tk.Frame.grid.
        **kargs : TYPE
            Arguments transmis à tk.Frame.grid..

        Returns
        -------
        None.

        """
        logger.debug('args = %r\tkargs = %r', args, kargs)
        self.subgrid()
        super().grid(*args, **kargs)


class OngletBaseDeDonnées(tk.Frame):
    """Onglet de base de données (affichage tableur)."""

    def __init__(self,
                 master: tk.Tk,
                 db: BaseDeDonnées,
                 table: str,
                 *args,
                 config: FichierConfig = None,
                 **kargs):
        """
        Crée un onglet de base de données.

        Parameters
        ----------
        master : tk.Tk
            Maître tk pour l'affichage.
        db : BaseDeDonnées
            Base de données à afficher.
        table : str
            Tableau à afficher.
        *args : TYPE
            Arguments transmis au parent tk.Frame.
        config : FichierConfig, optional
            Configuration externe. The default is None.
        **kargs : TYPE
            Arguments transmis au parent tk.Frame.

        Returns
        -------
        None.

        """
        logger.debug('master = %r\tdb = %r\ttable = %r\targs = %r\tconfig = %r\
\tkargs = %r', master, db, table, args, config, kargs)
        self.config = config
        self.table = table
        self.db = db

        super().__init__(master, *args, **kargs)
        self.build()

    def __repr__(self):
        """Affiche les informations de base sur l'objet."""
        return f'<{type(self)} at {hex(id(self))}>'

    @property
    def adresse(self):
        """Adresse de la base de données."""
        res = self.config.get('bd', 'adresse', fallback='test.db')
        logger.debug('res = %r', res)
        return res

    def importer(self):
        chemin = Path(askopenfilename())
        self.tableau.read_file(chemin)

    def exporter(self):
        chemin = asksaveasfilename()
        self.tableau.to_excel(chemin, self.table)

    def exporter_modèle(self):
        chemin = asksaveasfilename()
        self.tableau.loc()[[], :].to_excel(chemin, self.table)

    def build(self):
        """Construit les widgets."""
        self.canevas = tk.Canvas(self, width='50c', height='15c')
        logger.debug('self.canevas = %r', self.canevas)

        défiler_horizontalement = tk.Scrollbar(
            self, orient='horizontal', command=self.canevas.xview)
        logger.debug('défiler_horizontalement = %r', défiler_horizontalement)

        défiler_verticalement = tk.Scrollbar(
            self, orient='vertical', command=self.canevas.yview)
        logger.debug('défiler_verticalement = %r', défiler_verticalement)

        self.canevas.configure(xscrollcommand=défiler_horizontalement.set,
                               yscrollcommand=défiler_verticalement.set)

        self.contenant = tk.Frame(self.canevas)
        logger.debug('self.contenant = %r', self.contenant)

        self.contenant.bind('<Configure>', lambda x: self.canevas.configure(
            scrollregion=self.canevas.bbox('all')))

        self.tableau = Tableau(tkHandler(self.contenant), self.db, self.table)
        logger.debug('self.tableau = %r', self.tableau)

        màj = tk.Button(self, text='Màj',
                        command=lambda: self.tableau.update_grid())
        logger.debug('màj = %r', màj)

        importer = tk.Button(self, text='Importer',
                             command=self.importer)
        logger.debug('importer = %r', importer)

        exporter = tk.Button(self, text='Exporter',
                             command=self.exporter)
        logger.debug('exporter = %r', exporter)

        modèle = tk.Button(self, text='Modèle',
                           command=self.exporter_modèle)
        logger.debug('modèle = %r', modèle)

        self.défiler = [défiler_horizontalement, défiler_verticalement]
        logger.debug('self.défiler = %r', self.défiler)

        self.boutons = [màj, importer, exporter, modèle]
        logger.debug('self.boutons = %r', self.boutons)

    def subgrid(self):
        """Afficher les widgets."""
        self.défiler[0].grid(row=16, column=1, columnspan=1, sticky='we')
        self.défiler[1].grid(row=1, column=2, rowspan=15, sticky='ns')
        self.canevas.grid(row=1, column=1, rowspan=15, sticky='news')
        self.canevas.create_window((30, 15), window=self.contenant)
        self.tableau.grid(0, 0)

        for i, b in enumerate(self.boutons):
            b.grid(row=i, column=0)

    def grid(self, *args, **kargs):
        """Afficher le tableau."""
        logger.debug('args = %r\tkargs = %r', args, kargs)

        self.subgrid()
        super().grid(*args, **kargs)


class OngletBaseDeDonnéesFiltrée(OngletBaseDeDonnées):

    def build(self):
        """Construit les widgets."""
        self.canevas = tk.Canvas(self, width='50c', height='15c')
        logger.debug('self.canevas = %r', self.canevas)

        défiler_horizontalement = tk.Scrollbar(
            self, orient='horizontal', command=self.canevas.xview)
        logger.debug('défiler_horizontalement = %r', défiler_horizontalement)

        défiler_verticalement = tk.Scrollbar(
            self, orient='vertical', command=self.canevas.yview)
        logger.debug('défiler_verticalement = %r', défiler_verticalement)

        self.canevas.configure(xscrollcommand=défiler_horizontalement.set,
                               yscrollcommand=défiler_verticalement.set)

        self.contenant = tk.Frame(self.canevas)
        logger.debug('self.contenant = %r', self.contenant)

        self.contenant.bind('<Configure>', lambda x: self.canevas.configure(
            scrollregion=self.canevas.bbox('all')))

        h = tkHandler(self.contenant)

        self.tableau = Tableau(h, self.db, self.table)
        logger.debug('self.tableau = %r', self.tableau)

        self.filtre = Filtre(h, self.tableau)
        logger.debug('self.filtre = %r', self.filtre)

        màj = tk.Button(self, text='Màj',
                        command=lambda: self.tableau.update_grid())
        logger.debug('màj = %r', màj)

        importer = tk.Button(self, text='Importer',
                             command=self.importer)
        logger.debug('importer = %r', importer)

        exporter = tk.Button(self, text='Exporter',
                             command=self.exporter)
        logger.debug('exporter = %r', exporter)

        modèle = tk.Button(self, text='Modèle',
                           command=self.exporter_modèle)
        logger.debug('modèle = %r', modèle)

        self.défiler = [défiler_horizontalement, défiler_verticalement]
        logger.debug('self.défiler = %r', self.défiler)

        self.boutons = [màj, importer, exporter, modèle]
        logger.debug('self.boutons = %r', self.boutons)

    def subgrid(self):
        """Afficher les widgets."""
        self.défiler[0].grid(row=16, column=1, columnspan=1, sticky='we')
        self.défiler[1].grid(row=1, column=2, rowspan=15, sticky='ns')
        self.canevas.grid(row=1, column=1, rowspan=15, sticky='news')
        self.canevas.create_window((30, 15), window=self.contenant)
        self.filtre.grid(0, 0)
        self.tableau.grid(1, 0)

        for i, b in enumerate(self.boutons):
            b.grid(row=i, column=0)


class OngletFormulaire(tk.Frame):
    """Afficher un formulaire d'entrée de données."""

    def __init__(self,
                 master: tk.Tk,
                 db: BaseDeDonnées,
                 table: str,
                 *args,
                 config: FichierConfig = None,
                 **kargs):
        """
        Crée un formulaire d'entrée de données.

        Parameters
        ----------
        master : tk.Tk
            Maître d'interface tk.
        db : BaseDeDonnées
            Base de données.
        table : str
            Tableau où on veut entrer des données.
        *args : TYPE
            Arguments transmis au parent tk.Frame.
        config : FichierConfig, optional
            Fichier de configuration externe. The default is None.
        **kargs : TYPE
            Arguments transmis au parent tk.Frame.

        Returns
        -------
        None.

        """
        logger.debug('master = %r\tdb = %r\ttable = %r\targs = %r\
\tconfig = %r\tkargs = %r', master, db, table, args, config, kargs)

        self.config = config
        self.table = table
        self.db = db

        super().__init__(master, *args, **kargs)
        self.build()

    def __repr__(self):
        """Affiche les informations de base sur l'objet."""
        return f'<{type(self)} at {hex(id(self))}>'

    @property
    def adresse(self):
        """Adresse de la base de données."""
        res = self.config.get('bd', 'adresse', fallback='test.db')
        logger.debug('res = %r', res)
        return res

    def build(self):
        """
        Construire les widgets.

        Returns
        -------
        None.

        """
        self.canevas = tk.Canvas(self, width='50c', height='15c')
        logger.debug('self.canevas = %r', self.canevas)

        défiler_horizontalement = tk.Scrollbar(
            self, orient='horizontal', command=self.canevas.xview)
        logger.debug('défiler_horizontalement = %r', défiler_horizontalement)

        défiler_verticalement = tk.Scrollbar(
            self, orient='vertical', command=self.canevas.yview)
        logger.debug('défiler_verticalement = %r', défiler_verticalement)

        self.canevas.configure(xscrollcommand=défiler_horizontalement.set,
                               yscrollcommand=défiler_verticalement.set)

        self.contenant = tk.Frame(self.canevas)
        self.contenant.bind('<Configure>', lambda x: self.canevas.configure(
            scrollregion=self.canevas.bbox('all')))
        logger.debug('self.contenant = %r', self.contenant)

        self.formulaire = Formulaire(
            tkHandler(self.contenant), self.db, self.table)
        logger.debug('self.formulaire = %r', self.formulaire)

        self.défiler = [défiler_horizontalement, défiler_verticalement]
        logger.debug('self.défiler = %r', self.défiler)

    def subgrid(self):
        """Affiche les widgets."""
        self.défiler[0].grid(row=16, column=1, columnspan=1, sticky='we')
        self.défiler[1].grid(row=1, column=2, rowspan=15, sticky='ns')
        self.canevas.grid(row=1, column=1, rowspan=15, sticky='news')
        self.canevas.create_window((30, 15), window=self.contenant)
        self.formulaire.grid(0, 0)

    def grid(self, *args, **kargs):
        """Affiche le formulaire."""
        logger.debug('args = %r\tkargs = %r', args, kargs)
        self.subgrid()
        super().grid(*args, **kargs)


class Onglets(ttk.Notebook):
    """Groupe d'onglets."""

    def __init__(self,
                 master: tk.Frame,
                 config: FichierConfig,
                 schema: sqla.MetaData,
                 dialect: str = 'sqlite'):
        """
        Crée un groupe d'onglets.

        Parameters
        ----------
        master : tkinter.Frame
            Maître dans l'interface tkinter.
        config : FichierConfig
            Configuration externe.
        schema : sqlalchemy.MetaData
            Structure de base de données.

        Returns
        -------
        None.

        """
        logger.debug('master = %r\tconfig = %r\tschema = %r\t',
                     master, config, schema)

        super().__init__(master)
        self.onglets = []

        onglet = OngletConfig(self, config)
        logger.debug('onglet = %r', onglet)
        self.add(onglet, text=onglet.chemin)

        db = BaseDeDonnées(config.geturl(
            'bd', 'adresse', dialect=dialect), schema)
        logger.debug('db = %r', db)

        tables = config.getlist('bd', 'tables')
        logger.debug('tables = %r', tables)
        for nom_table in tables:
            logger.debug('nom_table = %r', nom_table)
            onglet = OngletBaseDeDonnées(
                self, db, nom_table, config=config)
            logger.debug('onglet = %r', onglet)
            self.add(onglet, text=nom_table)

        formulaires = config.getlist('bd', 'formulaires')
        logger.debug('formulaires = %r', formulaires)
        for nom_formulaire in formulaires:
            logger.debug('nom_formulaire = %r', nom_formulaire)
            onglet = OngletFormulaire(self, db, nom_formulaire)
            logger.debug('onglet = %r', onglet)
            self.add(onglet, text=f'[Formulaire] {nom_formulaire}')

    def __repr__(self):
        """Affiche les informations de base sur l'objet."""
        return f'<{type(self)} at {hex(id(self))}>'

    def add(self, obj: tk.Frame, *args, **kargs):
        """
        Ajouter un onglet.

        Parameters
        ----------
        obj : tk.Frame
            Onglet à ajouter.
        *args : TYPE
            Arguments transmis à la méthode add du parent tk.Frame.
        **kargs : TYPE
            Arguments transmis à la méthode add du parent tk.Frame.

        Returns
        -------
        None.

        """
        logger.debug('obj = %r\targs = %r\tkargs = %r', obj, args, kargs)
        self.onglets.append(obj)
        super().add(obj, *args, **kargs)

    def grid(self, *args, **kargs):
        """
        Afficher les onglets.

        Parameters
        ----------
        *args : TYPE
            Arguments transmis à la méthode grid du parent tk.Frame.
        **kargs : TYPE
            Arguments transmis à la méthode grid du parent tk.Frame.

        Returns
        -------
        None.

        """
        logger.debug('args = %r\tkargs = %r', args, kargs)

        logger.debug('self.children = %r', self.children)
        for onglet in self.children.values():
            logger.debug('onglet = %r', onglet)
            onglet.subgrid()

        super().grid(*args, **kargs)


def main(config: FichierConfig = None, md: sqla.MetaData = None, dossier=None):
    """
    Exemple simple d'afficahge d'onglets.

    Parameters
    ----------
    config : FichierConfig, optional
        Fichier de configuration externe. The default is None.
    md : sqla.MetaData, optional
        Structure de base de données. The default is None.

    Returns
    -------
    racine : TYPE
        Objet tkinter, racine de l'afficahge.
    onglets : TYPE
        L'instance Onglets.

    """
    logger.debug('config = %r\tmd = %r', config, md)

    if dossier is None:
        if len(sys.argv) > 1:
            dossier = pathlib.Path(sys.argv[1]).resolve()
        else:
            fichier = pathlib.Path(__file__).expanduser().resolve()
            dossier = fichier.parent.parent.parent.parent

    if config is None:
        import polygphys.outils.config
        config = polygphys.outils.config.main(dossier)
    logger.debug('config = %r', config)

    if md is None:
        import polygphys.outils.database
        base, md = polygphys.outils.database.main(dossier)
    logger.debug('md = %r', md)

    logger.info('Création de l\'interface...')
    racine = tk.Tk()
    logger.debug('racine = %r', racine)
    racine.title(config.get('tkinter', 'title', fallback='Demo'))

    onglets = Onglets(racine, config, md)
    logger.debug('onglets = %r', onglets)
    logger.info('Interface créée.')

    logger.info('Affichage...')
    onglets.grid(sticky='nsew')
    racine.mainloop()

    return racine, onglets


if __name__ == '__main__':
    main()
