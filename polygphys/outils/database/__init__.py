#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Construire une base de donnée selon un fichier de configuration simple.

Created on Fri Nov  5 14:55:41 2021

@author: ejetzer
"""

import pathlib
import logging

from typing import Union, Callable

import sqlalchemy as sqla
import pandas as pd

from .dtypes import get_type

logger = logging.getLogger(__name__)

TYPES_FICHIERS: dict[str, Callable] = {'.xlsx': pd.read_excel,
                                       '.xls': pd.read_excel,
                                       '.csv': pd.read_csv,
                                       '.pickle': pd.read_pickle,
                                       '.txt': pd.read_table}


class BaseDeDonnées:
    """Lien avec une base de données spécifique."""

    def __init__(self, adresse: str, schema: sqla.MetaData):
        """
        Lien avec la base de donnée se trouvant à adresse.

        Utilise le schema schema.

        Parameters
        ----------
        adresse : str
            Adresse vers la base de données.
        schema : sqla.MetaData
            Structure de la base de données.

        Returns
        -------
        None.

        """
        logger.debug(f"{self!r} {adresse=} {schema=}")
        self.adresse = adresse
        self.__schema = schema

    # Interface de sqlalchemy

    @property
    def tables(self) -> dict[str, sqla.Table]:
        """Liste des tables contenues dans la base de données."""
        logger.debug(f'{self!r} .tables')
        res = self.__schema.tables
        logger.debug(f'\t{res=}')
        return res

    def table(self, table: str) -> sqla.Table:
        """Retourne une table de la base de données"""
        logger.debug(f'{self!r} .table({table=})')
        res = self.tables[table]
        logger.debug(f'\t{res=}')
        return res

    def execute(self, requête, *args, **kargs):
        """Exécute la requête SQL donnée et retourne le résultat."""
        logger.debug(f'{self!r} .execute({requête=}, {args=}, {kargs=}')
        with self.begin() as con:
            logger.debug(f'{self!r} {con=!r}')
            logger.info(f'{self!r} {requête!s}')
            res = con.execute(requête, *args, **kargs)
            logger.debug(f'\t{res=}')
            return res

    def select(self,
               table: str,
               columns: tuple[str] = tuple(),
               where: tuple = tuple(),
               errors: str = 'ignore') -> pd.DataFrame:
        """
        Sélectionne des colonnes et items de la base de données.

        Selon les  critères fournis.

        Parameters
        ----------
        table : str
            Tableau d'où extraire les données.
        columns : tuple[str], optional
            Colonnes à extraire. The default is tuple(). Un tuple vide
            sélectionne toutes les colonnes.
        where : tuple, optional
            Critères supplémentaires. The default is tuple().
        errors : str, optional
            Comportement des erreurs. The default is 'ignore'.

        Returns
        -------
        df : pandas.DataFrame
            Retourne un DataFrame contenant les items et colonnes
            sélectionnées.

        """
        logger.debug(
            f'{self!r} .select({table=}, {columns=}, {where=}, {errors=})')

        # Si aucune colonne n'est spécifiée, on les prends toutes.
        logger.debug(f'{not len(columns)=}')
        if not len(columns):
            columns = self.columns(table)
        logger.debug(f'\t{columns=}')

        # Si une liste de colonnes est fournie, on vérifie qu'elles sont
        # toutes présentes dans le tableau.
        # On utilise aussi les objets Column du tableau
        columns = [self.table(table).columns['index']] + list(
            filter(lambda x: x.name in columns, self.table(table).columns))
        logger.debug(f'{self!r} {columns=}')

        requête = sqla.select(columns).select_from(self.table(table))
        logger.debug(f'{self!r} {requête=!s}')

        logger.debug(f'{self!r} {where=}')
        for clause in where:
            logger.debug(f'\t{requête=}')
            requête = requête.where(clause)
        logger.debug(f'{self!r} {requête=}')

        with self.begin() as con:
            logger.debug(f'{self!r} {con=}')
            logger.info(f'\t{requête!s}')
            df = pd.read_sql(requête, con, index_col='index')
            logger.debug(f'\t{df=}')

        return df

    def update(self, table: str, values: pd.DataFrame):
        """
        Mets à jour des items déjà présents dans la base de données.

        Parameters
        ----------
        table : str
            Tableau où se trouvent les données.
        values : pandas.DataFrame
            DataFrame contenant les valeurs à modifier.
            L'index est le critère de sélection.

        Returns
        -------
        None.

        """
        logger.debug(f'{self!r} .update({table=}, {values=})')

        requête = self.table(table).update()
        logger.debug(f'{self!r} {requête=}')

        index = values.index.name
        it = values.iterrows()
        logger.debug(f'{self!r} {index=} {it=!r}')
        for i, rangée in it:
            logger.debug(f'\t{i=} {rangée=}')
            clause = self.table(table).columns[index] == i
            logger.debug(f'\t{clause=}')
            r = requête.where(clause).values(**rangée)
            logger.debug(f'\t{r=}')
            self.execute(r)

    def insert(self, table: str, values: pd.DataFrame):
        """
        Insère un nouvel élément dans la base de données.

        Parameters
        ----------
        table : str
            Tableau utilisé.
        values : pd.DataFrame
            Valeurs à insérer.

        Returns
        -------
        None.

        """
        logger.debug(f'{self!r} .insert({table=}, {values=})')

        params = [({'index': i} | {c: v for c, v in r.items()})
                  for i, r in values.iterrows()]
        logger.debug(f'{self!r} {params=}')
        requête = self.table(table).insert(params)
        logger.debug(f'{self!r} {requête=!s}')
        self.execute(requête)

    def append(self, table: str, values: pd.DataFrame):
        """
        Ajoute un item à la fin de la base de données.

        Parameters
        ----------
        table : str
            Table où ajouter les données.
        values : pd.DataFrame
            Valuers à ajouter.

        Returns
        -------
        None.

        """
        logger.debug(f'{self!r} .append({table=}, {values=})')

        # Réassigner les indices:
        # On veut s'assurer qu'ils sont tous plus hauts
        # que le dernier indice déjà dans le tableau.
        indice_min = max(self.index(table), default=-1) + 1
        nouvel_index = pd.Index(range(len(values.index)),
                                name='index') + indice_min
        logger.debug(f'{self!r} {indice_min=} {nouvel_index=}')

        # Faire une copie des valeurs avec le bon index.
        values = values.copy()
        values.index = nouvel_index
        logger.debug(f'{self!r} {values=}')

        self.insert(table, values)

    def delete(self, table: str, values: pd.DataFrame):
        """
        Retire une entrée de la base de données.

        L'index de values sert de critère.

        Parameters
        ----------
        table : str
            Tableau d'où retirer l'entrée.
        values : pd.DataFrame
            Valeurs à retirer.

        Returns
        -------
        None.

        """
        logger.debug(f'{self!r} .delete({table=}, {values=})')

        requête = self.table(table).delete()

        # Réparation temporaire
        if isinstance(values, pd.DataFrame):
            index = values.index.name
            idx = values.index
        else:
            index = 'index'
            idx = pd.Index([values], name='index')

        logger.debug(f'{self!r} {requête!s} {index=} {idx=}')
        for i in idx:
            clause = self.table(table).columns[index] == 1
            r = requête.where(clause)
            logger.debug(f'{i=} {clause=} {r=}')
            self.execute(r)

    def màj(self, table: str, values: pd.DataFrame):
        """
        Met à jour des entrées de la base de données.

        Utilise update ou insert selon la préexistence de l'élément.
        L'index de values est utilisé comme critère.

        Parameters
        ----------
        table : str
            Tableau à mettre à jour.
        values : pd.DataFrame
            Valeurs à mettre à jour.

        Returns
        -------
        None.

        """
        logger.debug(f'{self!r} .màj({table=}, {values=})')

        index = self.index(table)
        existe = values.index.isin(index)
        logger.debug(f'{self!r} {index=} {existe=}')

        logger.debug(f'{self!r} {existe.any()=}')
        if existe.any():
            self.update(table, values.loc[existe, :])

        logger.debug(f'{self!r} {not existe.all()=}')
        if not existe.all():
            self.insert(table, values.loc[~existe, :])

    def create_engine(self) -> sqla.engine:
        """
        Créer le moteur de base de données.

        Returns
        -------
        sqlalchemy.engine
            Moteur de base de données.

        """
        logger.debug(f'{self!r} .create_engine {self.adresse=}')
        return sqla.create_engine(str(self.adresse))

    def begin(self):
        """
        Retourne une connection active.

        Eg:
            with instance_BdD.begin() as con:
                ...

        Returns
        -------
        Connection SQLAlchemy
            Connection active..

        """
        logger.debug(f'{self!r} .begin')
        return self.create_engine().begin()

    def initialiser(self, checkfirst: bool = True):
        """
        Créer les tableaux d'une base de données.

        Parameters
        ----------
        checkfirst : bool, optional
            Vérfier ou non l'existence des tableaux et champs.
            The default is True.

        Returns
        -------
        None.

        """
        logger.debug(f'{self!r} .initialiser({checkfirst=})')
        with self.begin() as con:
            logger.debug(f'{self!r} {con=}')
            self.__schema.create_all(con, checkfirst=checkfirst)

    def réinitialiser(self, checkfirst: bool = True):
        """
        Effacer puis créer les tableaux d'une base de données.

        Parameters
        ----------
        checkfirst : bool, optional
            Vérifier ou non l'existence des tableaux et champs.
            The default is True.

        Returns
        -------
        None.

        """
        logger.debug(f'{self!r} .réinitialiser({checkfirst=})')
        with self.begin() as con:
            logger.debug(f'{self!r} {con=}')
            self.__schema.drop_all(con, checkfirst=checkfirst)
            self.__schema.create_all(con)

    # Interface de pandas.DataFrame

    def dtype(self, table: str, champ: str) -> str:
        """
        Retourne le type de données d'un champ dans un tableau.

        Parameters
        ----------
        table : str
            Tableau.
        champ : str
            Champ dont on veut le type.

        Returns
        -------
        type_champ : str
            dtype selon pandas.

        """
        logger.debug(f'{self!r} .dtype({table=}, {champ=})')
        type_champ = self.table(table).columns[champ].type
        logger.debug(f'\t{type_champ=}')
        type_champ: str = get_type('sqlalchemy', type_champ, 'pandas')
        logger.debug(f'\t{type_champ=}')
        return type_champ

    def dtypes(self, table: str) -> pd.Series:
        """
        Retourne les types des colonnes d'un tableau.

        Parameters
        ----------
        table : str
            Tableau dont on veut les types.

        Returns
        -------
        dtypes : pandas.Series
            Series avec les colonnes comme index, les types comme valeurs.

        """
        logger.debug(f'{self!r} .dtypes({table=}')

        cols = self.columns(table)
        logger.debug(f'\t{cols=}')

        dtypes = map(lambda x: self.dtype(table, x), self.columns(table))
        logger.debug(f'\t{dtypes=}')

        dtypes = pd.Series(dtypes, index=cols)
        logger.debug(f'\t{dtypes=}')

        return dtypes

    def columns(self, table: str) -> pd.Index:
        """
        Retourne un index des colonnes présentes dans le tableau.

        Parameters
        ----------
        table : str
            Tableau dont on veut les colonnes.

        Returns
        -------
        res: pandas.Index
            Index des colonnes du tableau..

        """
        logger.debug(f'{self!r} .columns({table=})')

        res = pd.Index(c.name for c in self.table(
            table).columns if c.name != 'index')
        logger.debug(f'\t{res=}')

        return res

    def index(self, table: str) -> pd.Index:
        """
        Retourne l'index d'un tableau (colonne `index`).

        Parameters
        ----------
        table : str
            Tableau dont on veut l'index.

        Returns
        -------
        res : pandas.Index
            Index du tableau.

        """
        logger.debug(f'{self!r} .index({table=})')

        requête = sqla.select(self.table(
            table).columns['index']).select_from(self.table(table))
        logger.debug(f'\t{requête=!s}')

        with self.begin() as con:
            logger.debug(f'\t{con=}')
            résultat = con.execute(requête)
            logger.debug(f'\t{résultat=}')
            res = pd.Index(r['index'] for r in résultat)
            logger.debug(f'\t{res=}')
            return res

    def loc(self,
            table: str,
            columns: tuple[str] = None,
            where: tuple = tuple(),
            errors: str = 'ignore'):
        """
        Retourne un objet de sélection pandas.

        Parameters
        ----------
        table : str
            Tableau à extraire.
        columns : tuple[str], optional
            Colonnes à sélectionner. The default is None.
        where : tuple, optional
            Contraintes supplémentaires. The default is tuple().
        errors : str, optional
            Traitement des erreurs. The default is 'ignore'.

        Returns
        -------
        res : pandas.DataFrame.loc
            Objet de sélection.

        """
        logger.debug(
            f'{self!r} .loc({table=}, {columns=}, {where=}, {errors=})')
        if columns is None:
            columns = self.columns(table)
        logger.debug(f'\t{columns=}')

        res = self.select(table, columns, where, errors).loc
        logger.debug(f'\t{res=}')

        return res

    def iloc(self,
             table: str,
             columns: tuple[str] = tuple(),
             where: tuple = tuple(),
             errors: str = 'ignore'):
        """
        Retourne un objet de sélection numérique pandas.

        Parameters
        ----------
        table : str
            Tableau à extraire.
        columns : tuple[str], optional
            Colonnes à sélectionner. The default is tuple().
        where : tuple, optional
            Contraintes supplémentaires. The default is tuple().
        errors : str, optional
            Traitement des erreurs. The default is 'ignore'.

        Returns
        -------
        res : pandas.DataFrame.iloc
            Objet de sélection numérique.

        """
        logger.debug(
            f'{self!r} .iloc({table=}, {columns=}, {where=}, {errors=})')
        if columns is None:
            columns = self.columns(table)
        logger.debug(f'\t{columns=}')

        res = self.select(table, columns, where, errors).iloc
        logger.debug(f'\t{res=}')

        return res

    def deviner_type_fichier(self, chemin: pathlib.Path) -> Callable:
        """
        Retourne la fonction pandas à utiliser pour importer un fichier.

        La fonction est choisie selon l'extension.

        Parameters
        ----------
        chemin : pathlib.Path
            Chemin du fichier qu'on veut importer.

        Returns
        -------
        Callable
            Fonction du module pandas pour importer un fichier.

        """
        logger.debug(f'{self!r} .deviner_type_fichier({chemin=})')
        return TYPES_FICHIERS[chemin.suffix]

    def read_file(self,
                  table: str,
                  chemin: pathlib.Path,
                  type_fichier: Union[str, Callable] = None):
        """
        Importe un fichier dans la base de données.

        Parameters
        ----------
        table : str
            Tableau dans lequel importer les données.
        chemin : pathlib.Path
            Fichier à importer.
        type_fichier : Union[str, Callable], optional
            Type de fichier. The default is None.
            Si non spécifié, on devine avec l'extension.

        Returns
        -------
        None.

        """
        logger.debug(
            f'{self!r} .read_file({table=}, {chemin=}, {type_fichier=})')

        if type_fichier is None:
            type_fichier = self.deviner_type_fichier(chemin)
        elif isinstance(type_fichier, str):
            type_fichier = TYPES_FICHIERS[type_fichier]
        logger.debug(f'\t{type_fichier=}')

        df = type_fichier(chemin, index_col='index')
        logger.debug(f'{self!r} {df=}')

        self.màj(table, df)


def main(fichier: str = None) -> tuple[BaseDeDonnées, sqla.MetaData]:
    """
    Démonstration du module de base de données.

    Parameters
    -------
    fichier: str
        Chemin vers la base de données.

    Returns
    -------
    base : BaseDeDonnées
        Objet BaseDeDonnées.
    md : sqlalchemy.MetaData
        Structure de base de données.

    """
    logger.info(f'{__file__} main()')

    logger.info('Définition d\'une base de données...')
    md = sqla.MetaData()
    table = sqla.Table('demo', md,
                       sqla.Column('index', get_type('python', int,
                                   'sqlalchemy'), primary_key=False),
                       sqla.Column('desc',
                                   get_type('python', str, 'sqlalchemy')))
    logger.info(f'\t{md=} {table=}')

    logger.info('Ouverture du fichier de base de données...')

    if fichier is None:
        fichier = pathlib.Path(__file__).parent.absolute() / '../../demo.db'

    if 'sqlite' not in fichier:
        adresse = f'sqlite:///{fichier!s}'
    else:
        adresse = fichier

    logger.info(f'\t{adresse=}')
    base = BaseDeDonnées(adresse, md)
    logger.info(f'\t{base=}')

    logger.info('Réinitialiser la base de données...')
    base.réinitialiser()

    logger.info('Base de données définie:')
    for t, T in base.tables.items():
        logger.info(f'\t{t}: {T.columns}')

    logger.info('Ajout de rangées:')
    df = base.select('demo')
    logger.info(f'Départ:\n{df}')

    idx = pd.Index([0, 1, 2], name='index')
    df = pd.DataFrame({'desc': ['test 1', 'test 2', 'encore (3)']}, index=idx)
    logger.info(f'Données à ajouter:\n{df}')

    base.append('demo', df)
    df = base.select('demo')
    logger.info(f'Données ajoutées:\n{df}')

    return base, md
