#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 17:05:47 2022

@author: emilejetzer
"""


def test_import():
    import polygphys.outils.database
    import polygphys.outils.database.dtypes
    import polygphys.outils.database.gestion
    import polygphys.outils.database.modeles


def test_dtypes():
    from polygphys.outils.database.dtypes import get_type, default, column
    import sqlalchemy as sqla

    assert get_type('config', 'bool', 'python') is bool
    assert default('string') == ''
    assert column('test', str).name == 'test'


def test_modeles():
    from polygphys.outils.database.modeles import col_index
    import sqlalchemy as sqla

    assert col_index().name == 'index'


def test_BaseDeDonnées_tables():
    from polygphys.outils.database import BaseDeDonnées
    from polygphys.outils.database.dtypes import column
    from polygphys.outils.database.modeles import col_index
    import sqlalchemy as sqla

    adresse = 'sqlite:///'
    md = sqla.MetaData()
    sqla.Table('test', md, col_index(), column('test', str))

    bd = BaseDeDonnées(adresse, md)
    bd.réinitialiser()

    assert list(bd.tables.keys()) == ['test']


def test_BaseDeDonnées_index():
    from polygphys.outils.database import BaseDeDonnées
    from polygphys.outils.database.dtypes import column
    from polygphys.outils.database.modeles import col_index
    import sqlalchemy as sqla

    adresse = 'sqlite:///'
    md = sqla.MetaData()
    sqla.Table('test', md, col_index(), column('test', str))

    bd = BaseDeDonnées(adresse, md)
    bd.réinitialiser()

    assert list(bd.index('test')) == []


def test_BaseDeDonnées_append():
    from polygphys.outils.database import BaseDeDonnées
    from polygphys.outils.database.dtypes import column
    from polygphys.outils.database.modeles import col_index
    import sqlalchemy as sqla
    import pandas as pd

    adresse = 'sqlite:///'
    md = sqla.MetaData()
    sqla.Table('test', md, col_index(), column('test', str))

    bd = BaseDeDonnées(adresse, md)
    bd.réinitialiser()

    ajout = pd.DataFrame({'test': ['a', 'b', 'c']})
    bd.append('test', ajout)

    assert bd.loc('test')['test', 1] == 'a'
