# -*- coding: utf-8 -*-
"""
Programme ou module pour ...

Créé le Thu Jan 13 09:45:19 2022

@author: ejetzer
"""

import tkinter

import pyvisa as visa

from ..interface.tableau import Tableau


class Gestionnaire:

    def __init__(self):
        self.rm = visa.ResourceManager()

    def list_resources(self):
        return self.rm.list_resources()

    def open(self, nom: str) -> visa.Resource:
        return Appareil(nom)

    def grid(self):
        pass

    def pack(self):
        pass


class Appareil:

    def __init__(self, nom: str, root: tkinter.Tk = None):
        self.nom = nom
        self.resource: visa.Resource = None
        self.root: tkinter.Tk = root

    def open(self):
        rm: visa.ResourceManager = visa.ResourceManager()
        self.resource = rm.open_resource(self.nom)

    def close(self):
        self.resource.close()

    def read(self) -> str:
        return self.resource.read()

    def write(self, m: str):
        self.resource.write(m)

    def query(self, q: str) -> str:
        return self.resource.query(q)

    def get(self):
        pass

    def set(self):
        pass

    def grid(self):
        pass

    def pack(self):
        pass

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def export(self):
        pass


class Expérience:
    pass
