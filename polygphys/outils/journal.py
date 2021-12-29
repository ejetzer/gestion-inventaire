#!python
# -*- coding: utf-8 -*-
"""
Journalisation synchrone avec différents modules.

- le module logging
- un répertoire git
- une base de données.

Créé le Mon Dec 20 14:48:04 2021

@author: ejetzer
"""

import logging

from pathlib import Path
from logging import Handler, LogRecord

import pandas as pd

from git import Repo
from dataclasses import dataclass

from .interface.tableau import BaseTableau

logger = logging.getLogger(__name__)


@dataclass
class Formats:
    """Chaîne de format pour la journalisation."""

    default: str = '[%(asctime)s]\t%(levelname)s\t%(name)s\t%(message)s'
    labo: str = '[%(asctime)s]\t%(message)s'
    détails: str = '[%(asctime)s]\t%(levelname)s\t%(name)s\n\tFichier: \
%(filename)s\n\tFonction: %(funcName)s\n\tLigne: %(lineno)s\n\n\t%(message)s'


class Journal(Handler):
    """Journal compatible avec le module logging.

    Maintiens une base de données des changements apportés,
    par un programme ou manuellement. Les changements sont
    aussi sauvegardés dans un répertoire git.
    """

    def __init__(self,
                 level: float,
                 dossier: Path,
                 tableau: BaseTableau):
        """Journal compatible avec le module logging.

        Maintiens une base de données des changements apportés,
        par un programme ou manuellement. Les changements sont
        aussi sauvegardés dans un répertoire git.

        Parameters
        ----------
        level : float
            Niveau des messages envoyés.
        dossier : Path
            Chemin vers le répertoire git.
        tableau : BaseTableau
            Objet de base de données.

        Returns
        -------
        None.

        """
        self.repo: Repo = Repo(dossier)
        self.tableau: BaseTableau = tableau
        logger.debug('repo = %r\ttableau = %r', self.repo, self.tableau)

        super().__init__(level)

    @property
    def fichier(self):
        """Fichier de base de données (pour SQLite)."""
        return self.tableau.adresse

    # Interface avec le répertoire git

    def init(self):
        """Initialise le répertoire git et la base de données."""
        self.repo.init()
        self.tableau.initialiser()

    # Fonctions de logging.Handler

    def flush(self):
        """Ne fais rien."""
        pass

    def emit(self, record: LogRecord):
        """
        Enregistre une nouvelle entrée.

        Cette méthode ne devrait pas être appelée directement.

        Parameters
        ----------
        record : LogRecord
            L'entrée à enregistrer.

        Returns
        -------
        None.

        """
        diff = self.repo.diff(None)
        logger.debug('diff = %r', diff)

        for d in diff:
            if d.new_file:
                self.repo.index.add([d.b_blob])
            elif d.renamed_file:
                self.repo.index.remove([d.a_blob])
                self.repo.index.add([d.b_blob])
            elif d.deleted_file:
                self.repo.index.remove([d.a_blob])

        msg = record.getMessage()
        logger.debug('msg = %r', msg)

        self.repo.index.commit(msg)

        message = pd.DataFrame({'créé': [record.created],
                                'niveau': [record.levelno],
                                'logger': [record.name],
                                'msg': [msg],
                                'head': [self.repo.head.commit.hexsha]})
        logger.debug('message = %r', message)

        self.tableau.append(message)
        logger.debug('tableau = %r', self.tableau)
