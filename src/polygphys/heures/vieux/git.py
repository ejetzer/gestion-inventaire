#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manipulation de répertoires git.
Created on Mon Oct  4 18:18:45 2021

@author: ejetzer
"""

from subprocess import run
from pathlib import Path


class Repository:
    """Répertoire git."""

    def __init__(self, path: Path):
        """
        Répertoire git.

        Parameters
        ----------
        path : Path
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.path = path

    def init(self):
        """
        Initialiser un répertoire.

        Returns
        -------
        None.

        """
        run(['git', 'init'], cwd=self.path)

    def clone(self, other: str):
        """
        Cloner un répertoire.

        Parameters
        ----------
        other : str
            DESCRIPTION.

        Returns
        -------
        None.

        """
        run(['git', 'clone', other], cwd=self.path)

    def add(self, *args):
        """
        Ajouter un fichier à commettre.

        Parameters
        ----------
        *args : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        run(['git', 'add'] + list(args), cwd=self.path)

    def rm(self, *args):
        """
        Retirer un fichier.

        Parameters
        ----------
        *args : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        run(['git', 'rm'] + list(args), cwd=self.path)

    def commit(self, msg: str, *args):
        """
        Commettre les changements.

        Parameters
        ----------
        msg : str
            DESCRIPTION.
        *args : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        run(['git', 'commit', '-m', msg] + list(args), cwd=self.path)

    def pull(self):
        """
        Télécharger les changements lointains.

        Returns
        -------
        None.

        """
        run(['git', 'pull'], cwd=self.path)

    def push(self):
        """
        Pousser les changements locaux.

        Returns
        -------
        None.

        """
        run(['git', 'push'], cwd=self.path)

    def status(self):
        """
        Évaluer l'état du répertoire.

        Returns
        -------
        None.

        """
        run(['git', 'status'], cwd=self.path)

    def log(self):
        """
        Afficher l'historique.

        Returns
        -------
        None.

        """
        run(['git', 'log'], cwd=self.path)

    def branch(self, b: str = ''):
        """
        Passer à une nouvelle branche.

        Parameters
        ----------
        b : str, optional
            DESCRIPTION. The default is ''.

        Returns
        -------
        None.

        """
        run(['git', 'branch', b], cwd=self.path)


if __name__ == '__main__':
    path = Path('~/Desktop/test').expanduser()
    assert path.exists()
    repo = Repository(path)
    repo.init()
    with (path / 'test.txt').open('a') as f:
        f.write('hahaha')
    repo.add('test.txt')
    repo.commit('Ajout d\'un test')
    repo.status()
