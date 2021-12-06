#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Programme d'inventaire avec base de données.

Created on Mon Nov 15 15:17:28 2021

@author: ejetzer
"""

import logging
import sys

logger = logging.getLogger(__name__)

ch = logging.StreamHandler(sys.stderr)
ch.setLevel(logging.INFO)

fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(fmt)


def main():
    """Exemple des fonctionnalités du module."""
    logger.info('Démonstration du module polytechnique:')

    import polytechnique.outils.database
    polytechnique.outils.database.logger.addHandler(ch)
    polytechnique.outils.database.logger.setLevel(logging.DEBUG)
    base, md = polytechnique.outils.database.main()

    import polytechnique.outils.config
    polytechnique.outils.config.logger.addHandler(ch)
    polytechnique.outils.config.logger.setLevel(logging.DEBUG)
    config = polytechnique.outils.config.main()

    import polytechnique.outils.interface.onglets
    polytechnique.outils.interface.onglets.logger.addHandler(ch)
    polytechnique.outils.interface.onglets.logger.setLevel(logging.DEBUG)
    racine, onglets = polytechnique.outils.interface.onglets.main(config, md)

    logger.info('Fin.')


if __name__ == '__main__':
    main()
