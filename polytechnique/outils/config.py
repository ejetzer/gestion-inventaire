#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Enveloppe pour les fichiers de configuration, permettant de garder en mémoire le chemin du fichier.

Created on Mon Nov 22 14:22:36 2021

@author: ejetzer
"""

from pathlib import Path
from configparser import ConfigParser
from typing import Union, Iterable


class FichierConfig(ConfigParser):

    def __init__(self, chemin: Union[Iterable[Path], Path]):
        self.__chemin = chemin
        super().__init__()
        self.read()

    @property
    def chemin(self):
        return self.__chemin

    def read(self):
        super().read(self.__chemin, encoding='utf-8')

    def write(self):
        chemins = (self.__chemin,) if isinstance(self.__chemin, (Path, str)) else self.__chemin

        for chemin in chemins:
            with open(chemin, 'r', encoding='utf-8') as f:
                super().write(f)

    def __setitem__(self, section, options):
        super().__setitem__(section, options)
        self.write()
