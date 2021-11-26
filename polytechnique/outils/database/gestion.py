# -*- coding: utf-8 -*-

from sqlalchemy import MetaData

from ..outils.database import BaseDeDonnées

def reset(adresse: str, schema: MetaData):
    db = BaseDeDonnées(adresse, schema)
    db.réinitialiser()

def init(adresse: str, schema: MetaData):
    db = BaseDeDonnées(adresse, schema)

    for t in schema.tables:
        if t not in db.tables:
            pass
