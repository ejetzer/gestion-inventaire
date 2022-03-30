# -*- coding: utf-8 -*-
"""
Module utilitaire pour des tâches de laboratoire.

    - `outils` fournis les outils
    - les autres sous-modules sont des applications configurables
    - et des exemples.
"""

# Bibliothèque standard
from pathlib import Path  # Manipuler facilement des chemins

# Imports relatifs
# Gérer facilement des configurations complexes
from .outils.config import FichierConfig


class DemoConfig(FichierConfig):
    """Configuration pour une démonstration des capacités du module."""

    def default(self) -> str:
        """
        Retourne le modèle de configuration par défaut.

        :return: Le modèle de configuration par défaut.
        :rtype: str

        """
        return (Path(__file__).parent / 'demo.cfg').open().read()
