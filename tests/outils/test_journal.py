#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 17:06:28 2022

@author: emilejetzer
"""


def test_import():
    import polygphys.outils.journal


def test_Formats():
    from polygphys.outils.journal import Formats

    Formats()


def test_Journal():
    from polygphys.outils.journal import Journal
    from polygphys.outils.interface.tableau import BaseTableau
    from polygphys.outils.database import BaseDeDonnées
    from pathlib import Path
    import sqlalchemy as sqla
    from polygphys.outils.database.dtypes import column
    from polygphys.outils.database.modeles import col_index
    import logging

    dossier = Path('temp/')
    if not dossier.exists():
        dossier.mkdir()

    adresse = 'sqlite:///'
    md = sqla.MetaData()
    sqla.Table('test', md, col_index(), column('test', str))

    bd = BaseDeDonnées(adresse, md)
    bd.réinitialiser()

    try:
        tableau = BaseTableau(bd, 'test')
        Journal(logging.DEBUG, dossier, tableau)
    finally:
        dossier.unlink()
