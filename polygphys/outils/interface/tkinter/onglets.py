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
from ...journal import Formats


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
        logging.debug('master = %r\tconfig = %r', master, config)
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

    def build_champ(self, sec, champ, valeur):
        champ_var = tk.StringVar(self, value=champ)
        valeur_var = tk.StringVar(self, value=valeur)

        champ_var.trace_add(
            'write',
            lambda x, i, m, v=champ_var: self.update_config())
        valeur_var.trace_add(
            'write',
            lambda x, i, m, v=valeur_var: self.update_config())

        champ_entrée = ttk.Entry(self, textvariable=champ_var)
        valeur_entrée = ttk.Entry(self, textvariable=valeur_var)

        boutons = (ttk.Button(self, text='+', command=lambda: self.ajouter_champ(sec)),
                   ttk.Button(self, text='-', command=lambda: self.retirer_champ(sec, champ)))

        return champ_entrée, valeur_entrée, boutons

    def retirer_champ(self, sec, champ):
        self.champs[sec][champ].destroy()
        self.valeurs[sec][champ].destroy()
        self.boutons[sec][1][champ][0].destroy()
        self.boutons[sec][1][champ][1].destroy()
        del self.champs[sec][champ]
        del self.valeurs[sec][champ]
        del self.boutons[sec][1][champ]
        self.update_config()
        self.update_grid()

    def ajouter_champ(self, sec, champ='Nouveau champ', valeur=None):
        c, v, b = self.build_champ(sec, champ, valeur)
        self.champs[sec][champ] = c
        self.valeurs[sec][champ] = v
        self.boutons[sec][1][champ] = b
        self.update_config()
        self.update_grid()

    def build_section(self, sec=None):
        logging.debug('titre = %r', sec)

        section = self.config[sec]
        logging.debug('section = %r', section)

        titre_var = tk.StringVar(self, value=sec)
        titre_var.trace_add(
            'write',
            lambda x, i, m, v=titre_var: self.update_config())
        titre = ttk.Entry(self, textvariable=titre_var)

        bouton = ttk.Button(self, text='-', command=lambda: 1)

        champs, valeurs, boutons = {}, {}, {}
        for champ, valeur in section.items():
            c, v, b = self.build_champ(sec, champ, valeur)
            champs[champ] = c
            valeurs[champ] = v
            boutons[champ] = b

        return titre, champs, valeurs, boutons, bouton

    def retirer_section(self, sec):
        del self.titres[sec]
        del self.champs[sec]
        del self.valeurs[sec]
        del self.boutons[sec]
        self.update_config()
        self.update_grid()

    def build(self):
        """
        Construire les widgets.

        Returns
        -------
        None.

        """
        self.titres, self.champs, self.valeurs, self.boutons = {}, {}, {}, {}

        logging.debug('self.config.sections() = %r', self.config.sections())
        for sec in self.config.sections():
            t, cs, vs, bs, b = self.build_section(sec)
            self.titres[sec] = t
            self.champs[sec] = cs
            self.valeurs[sec] = vs
            self.boutons[sec] = [b, bs]

    def update_config(self):
        """
        Mettre la configuration à jour.

        Returns
        -------
        None.

        """
        logging.debug('self.champs = %r', self.champs)

        # Effacer les sections non présentes
        for sec in self.config.sections():
            if sec not in map(lambda x: x.get(), self.titres.values()):
                self.config.remove_section(sec)

        # Vérifier que les sections présentes existent
        for sec in map(lambda x: x.get(), self.titres.values()):
            if sec not in self.config.sections():
                self.config.add_section(sec)

        # Pour chaque section présente
        for sec in map(lambda x: x.get(), self.titres.values()):
            # effacer les champs non-existants
            for champ in map(lambda x: x.get(), self.champs[sec].values()):
                if champ not in self.config.options(sec):
                    self.config.set(sec, champ, '')
            # vérifier les valeurs des champs
        for section in self.champs:
            for clé in list(self.champs[section].keys()):
                nouvelle_clé = self.champs[section][clé].get()
                valeur = self.valeurs[section][clé].get()
                self.config[section][nouvelle_clé] = valeur

                self.champs[section][nouvelle_clé] = self.champs[section][clé]
                self.valeurs[section][nouvelle_clé] = self.valeurs[section][clé]

        self.config.write()

    def subgrid(self):
        """
        Affichage des widgets.

        Returns
        -------
        None.

        """
        self.build()
        logging.debug('self.titre_étiquettes = %r', self.titres)

        colonne = 0
        for titre, étiquette in self.titres.items():
            logging.debug('titre = %r\tétiquette = %r', titre, étiquette)
            étiquette.grid(row=0, column=colonne,
                           columnspan=3, sticky=tk.W+tk.E)
            self.boutons[titre][0].grid(
                row=0, column=colonne+3)

            rangée = 1
            logging.debug('self.champs = %r', self.champs)
            for étiquette, entrée in self.champs[titre].items():
                entrée.grid(row=rangée, column=colonne)
                self.valeurs[titre][étiquette].grid(
                    row=rangée, column=colonne+1)
                self.boutons[titre][1][étiquette][0].grid(
                    row=rangée, column=colonne+2)
                self.boutons[titre][1][étiquette][1].grid(
                    row=rangée, column=colonne+3)
                rangée += 1

            colonne += 4

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
        logging.debug('args = %r\tkargs = %r', args, kargs)
        self.subgrid()
        super().grid(*args, **kargs)

    def update_grid(self):
        self.destroy_children()
        self.subgrid()

    def destroy_children(self):
        del self.titres
        del self.champs
        del self.valeurs
        del self.boutons


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
        logging.debug('master = %r\tdb = %r\ttable = %r\targs = %r\tconfig = %r\
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
        logging.debug('res = %r', res)
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
        logging.debug('self.canevas = %r', self.canevas)

        défiler_horizontalement = tk.Scrollbar(
            self, orient='horizontal', command=self.canevas.xview)
        logging.debug('défiler_horizontalement = %r', défiler_horizontalement)

        défiler_verticalement = tk.Scrollbar(
            self, orient='vertical', command=self.canevas.yview)
        logging.debug('défiler_verticalement = %r', défiler_verticalement)

        self.canevas.configure(xscrollcommand=défiler_horizontalement.set,
                               yscrollcommand=défiler_verticalement.set)

        self.contenant = tk.Frame(self.canevas)
        logging.debug('self.contenant = %r', self.contenant)

        self.contenant.bind('<Configure>', lambda x: self.canevas.configure(
            scrollregion=self.canevas.bbox('all')))

        self.tableau = Tableau(tkHandler(self.contenant), self.db, self.table)
        logging.debug('self.tableau = %r', self.tableau)

        màj = tk.Button(self, text='Màj',
                        command=lambda: self.tableau.update_grid())
        logging.debug('màj = %r', màj)

        importer = tk.Button(self, text='Importer',
                             command=self.importer)
        logging.debug('importer = %r', importer)

        exporter = tk.Button(self, text='Exporter',
                             command=self.exporter)
        logging.debug('exporter = %r', exporter)

        modèle = tk.Button(self, text='Modèle',
                           command=self.exporter_modèle)
        logging.debug('modèle = %r', modèle)

        self.défiler = [défiler_horizontalement, défiler_verticalement]
        logging.debug('self.défiler = %r', self.défiler)

        self.boutons = [màj, importer, exporter, modèle]
        logging.debug('self.boutons = %r', self.boutons)

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
        logging.debug('args = %r\tkargs = %r', args, kargs)

        self.subgrid()
        super().grid(*args, **kargs)


class OngletBaseDeDonnéesFiltrée(OngletBaseDeDonnées):

    def build(self):
        """Construit les widgets."""
        self.canevas = tk.Canvas(self, width='50c', height='15c')
        logging.debug('self.canevas = %r', self.canevas)

        défiler_horizontalement = tk.Scrollbar(
            self, orient='horizontal', command=self.canevas.xview)
        logging.debug('défiler_horizontalement = %r', défiler_horizontalement)

        défiler_verticalement = tk.Scrollbar(
            self, orient='vertical', command=self.canevas.yview)
        logging.debug('défiler_verticalement = %r', défiler_verticalement)

        self.canevas.configure(xscrollcommand=défiler_horizontalement.set,
                               yscrollcommand=défiler_verticalement.set)

        self.contenant = tk.Frame(self.canevas)
        logging.debug('self.contenant = %r', self.contenant)

        self.contenant.bind('<Configure>', lambda x: self.canevas.configure(
            scrollregion=self.canevas.bbox('all')))

        h = tkHandler(self.contenant)

        self.tableau = Tableau(h, self.db, self.table)
        logging.debug('self.tableau = %r', self.tableau)

        self.filtre = Filtre(h, self.tableau)
        logging.debug('self.filtre = %r', self.filtre)

        màj = tk.Button(self, text='Màj',
                        command=lambda: self.tableau.update_grid())
        logging.debug('màj = %r', màj)

        importer = tk.Button(self, text='Importer',
                             command=self.importer)
        logging.debug('importer = %r', importer)

        exporter = tk.Button(self, text='Exporter',
                             command=self.exporter)
        logging.debug('exporter = %r', exporter)

        modèle = tk.Button(self, text='Modèle',
                           command=self.exporter_modèle)
        logging.debug('modèle = %r', modèle)

        self.défiler = [défiler_horizontalement, défiler_verticalement]
        logging.debug('self.défiler = %r', self.défiler)

        self.boutons = [màj, importer, exporter, modèle]
        logging.debug('self.boutons = %r', self.boutons)

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
        logging.debug('master = %r\tdb = %r\ttable = %r\targs = %r\
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
        logging.debug('res = %r', res)
        return res

    def build(self):
        """
        Construire les widgets.

        Returns
        -------
        None.

        """
        self.canevas = tk.Canvas(self, width='50c', height='15c')
        logging.debug('self.canevas = %r', self.canevas)

        défiler_horizontalement = tk.Scrollbar(
            self, orient='horizontal', command=self.canevas.xview)
        logging.debug('défiler_horizontalement = %r', défiler_horizontalement)

        défiler_verticalement = tk.Scrollbar(
            self, orient='vertical', command=self.canevas.yview)
        logging.debug('défiler_verticalement = %r', défiler_verticalement)

        self.canevas.configure(xscrollcommand=défiler_horizontalement.set,
                               yscrollcommand=défiler_verticalement.set)

        self.contenant = tk.Frame(self.canevas)
        self.contenant.bind('<Configure>', lambda x: self.canevas.configure(
            scrollregion=self.canevas.bbox('all')))
        logging.debug('self.contenant = %r', self.contenant)

        self.formulaire = Formulaire(
            tkHandler(self.contenant), self.db, self.table)
        logging.debug('self.formulaire = %r', self.formulaire)

        self.défiler = [défiler_horizontalement, défiler_verticalement]
        logging.debug('self.défiler = %r', self.défiler)

    def subgrid(self):
        """Affiche les widgets."""
        self.défiler[0].grid(row=16, column=1, columnspan=1, sticky='we')
        self.défiler[1].grid(row=1, column=2, rowspan=15, sticky='ns')
        self.canevas.grid(row=1, column=1, rowspan=15, sticky='news')
        self.canevas.create_window((30, 15), window=self.contenant)
        self.formulaire.grid(0, 0)

    def grid(self, *args, **kargs):
        """Affiche le formulaire."""
        logging.debug('args = %r\tkargs = %r', args, kargs)
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
        logging.debug('master = %r\tconfig = %r\tschema = %r\t',
                      master, config, schema)

        super().__init__(master)
        self.onglets = []

        onglet = OngletConfig(self, config)
        logging.debug('onglet = %r', onglet)
        self.add(onglet, text=Path(onglet.chemin).name)

        db = BaseDeDonnées(config.geturl(
            'bd', 'adresse', dialect=dialect), schema)
        logging.debug('db = %r', db)

        tables = config.getlist('bd', 'tables')
        logging.debug('tables = %r', tables)
        for nom_table in tables:
            logging.debug('nom_table = %r', nom_table)
            onglet = OngletBaseDeDonnées(
                self, db, nom_table, config=config)
            logging.debug('onglet = %r', onglet)
            self.add(onglet, text=nom_table)

        formulaires = config.getlist('bd', 'formulaires')
        logging.debug('formulaires = %r', formulaires)
        for nom_formulaire in formulaires:
            logging.debug('nom_formulaire = %r', nom_formulaire)
            onglet = OngletFormulaire(self, db, nom_formulaire)
            logging.debug('onglet = %r', onglet)
            self.add(onglet, text=f'[F] {nom_formulaire}')

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
        logging.debug('obj = %r\targs = %r\tkargs = %r', obj, args, kargs)
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
        logging.debug('args = %r\tkargs = %r', args, kargs)

        logging.debug('self.children = %r', self.children)
        for onglet in self.children.values():
            logging.debug('onglet = %r', onglet)
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
    logging.basicConfig(format=Formats().détails, level=logging.DEBUG)

    if dossier is None:
        if len(sys.argv) > 1:
            dossier = pathlib.Path(sys.argv[1]).resolve()
        else:
            fichier = pathlib.Path(__file__).expanduser().resolve()
            dossier = fichier.parent.parent.parent.parent
    logging.debug('dossier = %r', dossier)

    if config is None:
        import polygphys.outils.config
        config = polygphys.outils.config.main(dossier)
    logging.debug('config = %r', config)

    if md is None:
        import polygphys.outils.database
        base, md = polygphys.outils.database.main(dossier)
    logging.debug('md = %r', md)

    logging.info('Création de l\'interface...')
    racine = tk.Tk()
    logging.debug('racine = %r', racine)
    racine.title(config.get('tkinter', 'title', fallback='Demo'))

    # adresse_relative = config.geturl('bd', 'adresse')
    # segments = adresse_relative.split('///', 1)
    # adresse_corrigée = segments[0] + '///' + str(dossier / segments[1])
    # logging.debug('adresse_corrigée: %r', adresse_corrigée)
    # config.set('bd', 'adresse', adresse_corrigée)

    onglets = Onglets(racine, config, md)
    logging.debug('onglets = %r', onglets)
    logging.info('Interface créée.')

    logging.info('Affichage...')
    onglets.grid(sticky='nsew')
    racine.mainloop()

    # config.set('bd', 'adresse', adresse_relative)

    return racine, onglets


if __name__ == '__main__':
    main()
