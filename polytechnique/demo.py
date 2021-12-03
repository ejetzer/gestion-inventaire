#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Programme d'inventaire avec base de données.

Created on Mon Nov 15 15:17:28 2021

@author: ejetzer
"""

import logging
import sys

ch = logging.StreamHandler(sys.stderr)
ch.setLevel(logging.DEBUG)

fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(fmt)


def main():
    print('Démonstration du module polytechnique:')

    import polytechnique.outils.database
    base, md = polytechnique.outils.database.main()

    import polytechnique.outils.config
    polytechnique.outils.config.logger.addHandler(ch)
    polytechnique.outils.config.logger.setLevel(logging.DEBUG)
    config = polytechnique.outils.config.main()

    import polytechnique.outils.interface.onglets
    racine, onglets = polytechnique.outils.interface.onglets.main(config, md)

    print('Fin.')


if __name__ == '__main__':
    main()
