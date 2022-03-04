# -*- coding: utf-8 -*-
"""
Programme ou module pour ...

Créé le Thu Jan 13 09:45:19 2022

@author: ejetzer
"""

import tkinter

from pathlib import Path

import pyvisa as visa

from ..config import FichierConfig


class Gestionnaire:
    """Gestionnaire d'appareils."""

    def __init__(self):
        """
        Gestionnaire d'appareils.

        Returns
        -------
        None.

        """
        self.rm = visa.ResourceManager()

    def list_resources(self):
        """
        Appareils disponibles.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        return self.rm.list_resources()

    def open(self, nom: str) -> visa.Resource:
        """
        Ouvrir un appareil.

        Parameters
        ----------
        nom : str
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        return Appareil(nom)

    def grid(self):
        """
        Afficher le contrôleur.

        Returns
        -------
        None.

        """
        pass

    def pack(self):
        """
        Afficher le contrôleur.

        Returns
        -------
        None.

        """
        pass


class Appareil:
    """Appareil."""

    def __init__(self, nom: str, root: tkinter.Tk = None):
        """
        Appareil.

        Parameters
        ----------
        nom : str
            DESCRIPTION.
        root : tkinter.Tk, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        None.

        """
        self.nom = nom
        self.resource: visa.Resource = None
        self.root: tkinter.Tk = root

    def open(self):
        """
        Ouvrir la connection.

        Returns
        -------
        None.

        """
        rm: visa.ResourceManager = visa.ResourceManager()
        self.resource = rm.open_resource(self.nom)

    def close(self):
        """
        Fermer la connection.

        Returns
        -------
        None.

        """
        self.resource.close()

    def read(self) -> str:
        """
        Lire l'entrée.

        Returns
        -------
        str
            DESCRIPTION.

        """
        return self.resource.read()

    def write(self, m: str):
        """
        Écrire.

        Parameters
        ----------
        m : str
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.resource.write(m)

    def query(self, q: str) -> str:
        """
        Écrire, puis attendre la réponse.

        Parameters
        ----------
        q : str
            DESCRIPTION.

        Returns
        -------
        str
            DESCRIPTION.

        """
        return self.resource.query(q)

    def get(self):
        """
        Obtenir une information.

        Returns
        -------
        None.

        """
        pass

    def set(self):
        """
        Ajuster un réglage.

        Returns
        -------
        None.

        """
        pass

    def grid(self):
        """
        Afficher l'appareil.

        Returns
        -------
        None.

        """
        pass

    def pack(self):
        """
        Afficher l'appareil.

        Returns
        -------
        None.

        """
        pass

    def __enter__(self):
        """
        Ouvrir la connection de manière sécuritaire.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Fermer la connection.

        Parameters
        ----------
        exc_type : TYPE
            DESCRIPTION.
        exc_value : TYPE
            DESCRIPTION.
        traceback : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.close()

    def export(self):
        """
        Exporter les données.

        Returns
        -------
        None.

        """
        pass


class Expérience:
    """Montage et prise de mesures."""

    def __init__(self, fichier_config: Path):
        """
        Montage et prise de mesures.

        Parameters
        ----------
        fichier_config : Path
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.config = FichierConfig(fichier_config)

    def run(self):
        """
        Prendre des mesures.

        Returns
        -------
        None.

        """
        pass
