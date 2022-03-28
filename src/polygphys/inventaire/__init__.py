# -*- coding: utf-8 -*-
"""Programme de gestion d'inventaire."""

# Bibliothèques standard
from pathlib import Path

# Imports relatifs
from ..outils.config import FichierConfig


class InventaireConfig(FichierConfig):
    """Fichier de configuration de programme d'inventaire."""

    def default(self) -> str:
        """
        Retourne le contenu du fichier default.cfg contenu dans le module.

        Returns
        -------
        str
            Contenu de default.cfg.

        """
        return (Path(__file__).parent / 'default.cfg').open().read()
