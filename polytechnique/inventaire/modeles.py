#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Programme ou module pour ...

Créé le Fri Nov 26 15:36:57 2021

@author: ejetzer
"""

import sqlalchemy as sqla

from sqlalchemy import Column, MetaData, Table
from sqlalchemy.orm import declarative_base

from ..outils.database.dtypes import get_type, column

metadata = MetaData(schema='inventaire')

def colonnes_communes():
    return column('index', int, primary_key=True), column('responsable', str)

cols = colonnes_communes() + (column('description', str), column('local', str))
boîtes = Table('boites', metadata, *cols)
