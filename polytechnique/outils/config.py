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

    def __init__(self,
                 chemin: Union[Iterable[Path], Path],
                 inline_comment_prefixes=('#', ';'),
                 **kargs):
        self.__chemin = chemin
        super().__init__(inline_comment_prefixes=inline_comment_prefixes, **kargs)
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

    def getlist(sec: str, clé: str, fallback: list = []):
        """Obtenir une liste, à partir d'une énumération multiligne."""
        if fallback is not None:
            val = self.get(sec, clé, '')
        else:
            val = self.get(sec, clé, '')

        val = list(map(str.strip, val.split('\n')))
        return val


def main() -> FichierConfig:
    print('Ouvrir un fichier de configuration...')
    config = FichierConfig('base.cfg')
    print('Configuration ouverte...')

    return config
