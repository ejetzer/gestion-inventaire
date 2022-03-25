#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 15:56:35 2022

@author: emilejetzer
"""

from polygphys.inventaire.modeles import créer_dbs
import sqlalchemy
import getpass

mdp = getpass.getpass('mdp>')
moteur = sqlalchemy.create_engine(
    f'mysql+pymysql://emilejetzer:{mdp}@132.207.44.77:3306/test_schema', future=True)

with moteur.connect() as c:
    pass


metadata = créer_dbs(sqlalchemy.MetaData())
metadata.create_all(moteur)
