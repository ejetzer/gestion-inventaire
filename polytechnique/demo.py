#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Programme d'inventaire avec base de données.

Created on Mon Nov 15 15:17:28 2021

@author: ejetzer
"""

from polytechnique.outils.interface.onglets import Onglets
from polytechnique.outils.config import FichierConfig
from polytechnique.outils.database.dtypes import get_type
from polytechnique.outils.database import BaseDeDonnées

def main():
    print('Démonstration du module polytechnique:')

    import polytechnique.outils.database
    base, md = polytechnique.outils.database.main()

    import polytechnique.outils.config
    config = polytechnique.outils.config.main()

    import polytechnique.outils.interface.onglets
    racine, onglets = polytechnique.outils.interface.onglets.main(config, md)

    print('Fin.')

if __name__ == '__main__':
    main()
