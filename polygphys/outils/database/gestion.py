# -*- coding: utf-8 -*-
"""Migration et gestion particulière de bases de données."""

from sqlalchemy import MetaData

from ..outils.database import BaseDeDonnées


def reset(adresse: str, schema: MetaData):
    """Réinitialiser une base de données."""
    db = BaseDeDonnées(adresse, schema)
    db.réinitialiser()


def init(adresse: str, schema: MetaData):
    """Initialiser une base de données."""
    db = BaseDeDonnées(adresse, schema)

    for t in schema.tables:
        if t not in db.tables:
            pass


def migrer(adresse: str, a: MetaData, b: MetaData):
    """Migrer d'une structure à une autre."""
    pass
