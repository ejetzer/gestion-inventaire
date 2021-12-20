#!python
# -*- coding: utf-8 -*-
"""
Programme ou module pour ...

Créé le Mon Dec 20 14:48:04 2021

@author: ejetzer
"""

from pathlib import Path

import pandas as pd

from git import Repo

from .interface.df import BaseTableau


class Journal:

    def __init__(self, dossier: Path, tableau: BaseTableau):
        self.repo: Repo = Repo(dossier)
        self.tableau: BaseTableau = tableau

    @property
    def fichier(self):
        return self.tableau.adresse

    # Interface avec le répertoire git

    def init(self):
        self.repo.init()
        self.tableau.initialiser()

    def commit(self):
        self.repo.index.add(self.__fichiers + [self.fichier])
        self.repo.index.commit(self.__message)
        self.tableau.append(self.__messages)

    # Fonctions de journal

    def entrer(self,
               message: str,
               fichiers: list[str]):
        messages = pd.DataFrame(columns=('message', 'fichier'))

        for f in fichiers:
            messages.append({'message': message, 'fichier': f},
                            ignore_index=True)

        self.__message = message
        self.__entrée = messages.copy(True)
        self.__fichiers = fichiers[:]

    def __enter__(self):
        return self

    def __exit__(self, t, value, traceback):
        if t is None:
            self.commit()
            return True
