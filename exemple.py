# -*- coding: utf-8 -*-
"""
Résumé en une ligne de la fonctionnalité du module ou script.

Résumé plus complet: on veut élaborer, donner des exemples d'utilisation
et des références à des inspirations, modules similaires, etc. C'est un bon
endroit pour justifier certaines décisions qui affectent le module en entier,
comme le choix de certains sous-modules, etc.
"""

# Bibliothèques standards
import sys  # Accès à des fonctions systèmes

from pathlib import Path  # Manipulation de chemins et de fichiers

# Bibliothèques PIPy
import sqlalchemy as sqla

from pandas import DataFrame

# Constantes
PI: float = 3.1415

# Classes


class ClasseUtile:
    """Description rapide de la classe."""

    pass

# Fonctions globales


def fonction_utile(a: str, b: str, c: str):
    """
    Description de la fonctionnalité de la fonction.

    Description plus élaborée de la fonctionnalité.

    :param a: DESCRIPTION
    :type a: str
    :param b: DESCRIPTION
    :type b: str
    :param c: DESCRIPTION
    :type c: str
    :return: DESCRIPTION
    :rtype: TYPE

    """
    return a + b + c


def main():
    """
    Fonction principale, pour un script.

    :return: DESCRIPTION
    :rtype: TYPE

    """


if __name__ == '__main__':
    main()
