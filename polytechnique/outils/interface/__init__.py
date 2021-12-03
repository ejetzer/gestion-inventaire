#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Outils de création d'interface graphique, en particulier pour des bases de données.

Créé le Fri Nov 26 10:41:14 2021

@author: ejetzer
"""

import pathlib

from typing import Callable, Any, Union


@dataclass
class InterfaceHandler:
    """
    Classe de base pour créer des widgets d'interface.

    Ne devrait pas être utilisé directement, mais toujours surclassé.

    entrée: Callable[[str, Callable, type], Any]
    Une fonction qui retourne un widget d'entrée de données.
    Le troisième argument est le type de l'entrée demandée.

    texte: Callable[[str], Any]
    Une fonction retournant un widget d'affichage de texte.

    bouton: Callable[[str, Callable], Any]
    Une fonction retournant un bouton.
    Le second argument est la fonction appelée par le déclenchement du bouton.

    demander: Callable[[str, type], Callable]
    Une fonction affichant un invite d'entrée d'informations.
    Le second argument est le type de l'entrée demandée.

    """

    entrée: Callable[[str, Callable, type], Any]
    texte: Callable[[str], Any]
    bouton: Callable[[str, Callable], Any]
    demander: Callable[[str, type], Callable]
