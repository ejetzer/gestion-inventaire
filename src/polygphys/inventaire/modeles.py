# -*- coding: utf-8 -*-
"""Modèles de bases de données d'inventaire."""

# Bibliothèques standards
from datetime import date  # Pour des comparaisons de dates

# Bibliothèques PIPy
# Pour les descriptions de schemas
from sqlalchemy import MetaData, Table, ForeignKey

# Imports relatifs
# Facilite la description de colones
from ..outils.base_de_donnees.dtypes import column
from ..outils.base_de_donnees import modeles  # Structures déjà prêtes
# Index standard du paquet
from ..outils.base_de_donnees.modeles import col_index

# TODO Utiliser le ORM pour définir les tables.


def appareils(metadata: MetaData) -> Table:
    """
    Table d'appareils, avec informations connexes.

    Les informations voulues sont:
        - L'identifiant unique de l'appareil dans le système
        - Le responsable de l'appareil
        - La place de rangement de l'appareil
        - Les numéros de série, de modèle et de fournisseur
        - Le fournisseur & fabricant
        - La désignation de l'appareil
        - Etc.

    :param metadata: Le schéma SQL à utiliser et modifier
    :type metadata: MetaData
    :return: La table créée, avec le nom «appareils»
    :rtype: Table

    """
    # Pour pouvoir désigner des responsables de manière unique
    matricule = metadata.tables['personnes'].columns['index']

    # Pour désigner des emplacements de manière unique
    designation = metadata.tables['etageres'].columns['index']

    # Liste de toutes les colonnes
    cols = [col_index(),  # Index
            column('responsable', int, ForeignKey(
                matricule, onupdate='CASCADE')),  # Personne responsable
            column('place', int, ForeignKey(designation)),  # Rangement

            # Description de l'appareil
            column('numéro de série', str),
            column('numéro de modèle', str),
            column('fournisseur', str),
            column('fabricant', str),
            column('fonctionnel', bool),  # Pour trouver ceux à réparer
            column('informations supplémentaires', str),
            column('nom', str),
            column('description', str)
            ]

    return Table('appareils', metadata, *cols)


def consommables(metadata: MetaData) -> Table:
    matricule = metadata.tables['personnes'].columns['index']
    designation = metadata.tables['etageres'].columns['index']
    cols = [col_index(),
            column('responsable', int, ForeignKey(matricule)),
            column('place', int, ForeignKey(designation)),
            column('numéro de fabricant', str),
            column('numéro de fournisseur', str),
            column('fournisseur', str),
            column('fabricant', str),
            column('commander', bool),
            column('informations supplémentaires', str),
            column('nom', str),
            column('description', str)
            ]

    return Table('consommables', metadata, *cols)


def boites(metadata: MetaData) -> Table:
    """
    Lister des boîtes de transport.

    Parameters
    ----------
    metadata : MetaData
        DESCRIPTION.

    Returns
    -------
    Table
        DESCRIPTION.

    """
    matricule = metadata.tables['personnes'].columns['index']
    designation = metadata.tables['etageres'].columns['index']
    cols = [col_index(),
            column('responsable', int, ForeignKey(matricule)),
            column('place', int, ForeignKey(designation)),
            column('description', str),
            column('dimensions', str)
            ]

    return Table('boites', metadata, *cols)


def emprunts(metadata: MetaData) -> Table:
    """
    Lister des emprunts.

    Parameters
    ----------
    metadata : MetaData
        DESCRIPTION.

    Returns
    -------
    Table
        DESCRIPTION.

    """
    appareil = metadata.tables['appareils'].columns['index']
    personnes = metadata.tables['personnes'].columns['index']
    cols = [col_index(),
            column('appareil', int, ForeignKey(appareil)),
            column('responsable', int, ForeignKey(personnes)),
            column('emprunteur', int, ForeignKey(personnes)),
            column('date emprunt', date),
            column('date retour', date),
            column('retourné', bool),
            column('détails', str)
            ]

    return Table('emprunts', metadata, *cols)


def utilisation_boites(metadata: MetaData) -> Table:
    """
    Lister des boîtes utilisées.

    Parameters
    ----------
    metadata : MetaData
        DESCRIPTION.

    Returns
    -------
    Table
        DESCRIPTION.

    """
    boite = metadata.tables['appareils'].columns['index']
    personnes = metadata.tables['personnes'].columns['index']
    cols = [col_index(),
            column('boite', int, ForeignKey(boite)),
            column('responsable', int, ForeignKey(personnes)),
            column('emprunteur', int, ForeignKey(personnes)),
            column('date emprunt', date),
            column('date retour', date),
            column('retourné', bool),
            column('détails', str)
            ]

    return Table('utilisation_boites', metadata, *cols)


def créer_dbs(metadata: MetaData):
    """
    Créer les bases de données.

    Parameters
    ----------
    metadata : MetaData
        DESCRIPTION.

    Returns
    -------
    metadata : TYPE
        DESCRIPTION.

    """
    modeles.créer_dbs(metadata)

    appareils(metadata)
    consommables(metadata)
    boites(metadata)
    emprunts(metadata)
    utilisation_boites(metadata)

    return metadata


if __name__ == '__main__':
    md = créer_dbs(MetaData())
    print(md)
    for t, T in md.tables.items():
        print(t)
        for c in T.columns:
            print('\t', c)
