#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Construire une base de donnée selon un fichier de configuration simple.

Created on Fri Nov  5 14:55:41 2021

@author: ejetzer
"""

import pathlib
import logging
import sys

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

    def __init__(self, adresse: str, metadata: sqla.MetaData):
        """
        Lien avec la base de donnée se trouvant à adresse.

        Utilise le schema schema.

        Parameters
        ----------
        adresse : str
            Adresse vers la base de données.
        metadata : sqla.MetaData
            Structure de la base de données.

        Returns
        -------
        None.

        """
        logging.debug('adresse = %r\tmetadata = %r', adresse, metadata)
        self.adresse = adresse
        self.metadata = metadata

    # Interface de sqlalchemy

    @property
    def tables(self) -> dict[str, sqla.Table]:
        """Liste des tables contenues dans la base de données."""
        res = self.metadata.tables
        logging.debug('res = %r', res)
        return res

    def table(self, table: str) -> sqla.Table:
        """Retourne une table de la base de données"""
        logging.debug('table = %r', table)
        res = self.tables[table]
        logging.debug('res = %r', res)
        return res

    def execute(self, requête, *args, **kargs):
        """Exécute la requête SQL donnée et retourne le résultat."""
        logging.debug('requête = %r\targs = %r\tkargs = %r',
                      requête, args, kargs)
        with self.begin() as con:
            logging.debug('con = %r', con)
            logging.info('requête = %s', requête)
            res = con.execute(requête, *args, **kargs)
            logging.debug('res = %r', res)
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
        logging.debug('table = %r\tcolumns = %r\twhere = %r\terrors = %r',
                      table, columns, where, errors)

        # Si aucune colonne n'est spécifiée, on les prends toutes.
        logging.debug('not len(columns) = %r', not len(columns))
        if not len(columns):
            columns = self.columns(table)
        logging.debug('columns = %r', columns)

        # Si une liste de colonnes est fournie, on vérifie qu'elles sont
        # toutes présentes dans le tableau.
        # On utilise aussi les objets Column du tableau
        columns = [self.table(table).columns['index']] + list(
            filter(lambda x: x.name in columns, self.table(table).columns))
        logging.debug('columns = %r', columns)

        requête = sqla.select(columns).select_from(self.table(table))
        logging.debug('requête = %s', requête)

        logging.debug('where = %r', where)
        for clause in where:
            logging.debug('clause = %r', clause)
            requête = requête.where(clause)
            logging.debug('requête = %r', requête)
        logging.debug('requête = %r', requête)

        with self.begin() as con:
            logging.debug('con = %r', con)
            logging.info('requête = %s', requête)
            df = pd.read_sql(requête, con, index_col='index')
            logging.debug('df = %r', df)

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
        logging.debug('table = %r\tvalues = %r', table, values)

        requête = self.table(table).update()
        logging.debug('requête = %r', requête)

        index = values.index.name
        it = values.iterrows()
        logging.debug('index = %r\tit = %r', index, it)
        for i, rangée in it:
            logging.debug('i = %r\trangée = %r', i, rangée)
            clause = self.table(table).columns[index] == i
            logging.debug('clause = %r', clause)
            r = requête.where(clause).values(**rangée)
            logging.debug('r = %r', r)
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
        logging.debug('table = %r\tvalues = %r', table, values)

        params = [({'index': i} | {c: v for c, v in r.items()})
                  for i, r in values.iterrows()]
        logging.debug('params = %r', params)
        requête = self.table(table).insert(params)
        logging.debug('requête = %s', requête)
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
        logging.debug('table = %r\tvalues = %r', table, values)

        # Réassigner les indices:
        # On veut s'assurer qu'ils sont tous plus hauts
        # que le dernier indice déjà dans le tableau.
        indice_min = max(self.index(table), default=-1) + 1
        nouvel_index = pd.Index(range(len(values.index)),
                                name='index') + indice_min
        logging.debug('indice_min = %r\tnouvel_index = %r',
                      indice_min, nouvel_index)

        # Faire une copie des valeurs avec le bon index.
        values = values.copy()
        values.index = nouvel_index
        logging.debug('values = %r', values)

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
        logging.debug('table = %r\tvalues = %r', table, values)

        requête = self.table(table).delete()

        # Réparation temporaire
        if isinstance(values, pd.DataFrame):
            index = values.index.name
            idx = values.index
        else:
            index = 'index'
            idx = pd.Index([values], name='index')

        logging.debug('requête = %s\tindex = %r\tidx = %r',
                      requête, index, idx)
        for i in idx:
            clause = self.table(table).columns[index] == 1
            r = requête.where(clause)
            logging.debug('i = %r\tclause = %r\tr = %s',
                          i, clause, r)
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
        logging.debug('table = %r\tvalues = %r', table, values)

        index = self.index(table)
        existe = values.index.isin(index)
        logging.debug('index = %r\texiste = %r', index, existe)

        logging.debug('existe.any() = %r', existe.any())
        if existe.any():
            self.update(table, values.loc[existe, :])

        logging.debug('not existe.all() = %r', not existe.all())
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
        logging.debug('adresse = %r', self.adresse)
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
        logging.debug('checkfirst = %r', checkfirst)
        with self.begin() as con:
            logging.debug('con = %r', con)
            self.metadata.create_all(con, checkfirst=checkfirst)

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
        logging.debug('checkfirst = %r', checkfirst)
        with self.begin() as con:
            logging.debug('con = %r', con)
            self.metadata.drop_all(con, checkfirst=checkfirst)
            self.metadata.create_all(con)

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
        logging.debug('table = %r\tchamp = %r', table, champ)
        type_champ = self.table(table).columns[champ].type
        logging.debug('type_champ = %r', type_champ)
        type_champ: str = get_type('sqlalchemy', type_champ, 'pandas')
        logging.debug('type_champ = %r', type_champ)
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
        logging.debug('table = %r', table)

        cols = self.columns(table)
        logging.debug('cols = %r', cols)

        dtypes = map(lambda x: self.dtype(table, x), self.columns(table))
        logging.debug('dtypes = %r', dtypes)

        dtypes = pd.Series(dtypes, index=cols)
        logging.debug('dtypes = %r', dtypes)

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
        logging.debug('table = %r', table)

        res = pd.Index(c.name for c in self.table(
            table).columns if c.name != 'index')
        logging.debug('res = %r', res)

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
        logging.debug('table = %r', table)

        requête = sqla.select([self.table(
            table).columns['index']]).select_from(self.table(table))
        logging.debug('requête = %s', requête)

        with self.begin() as con:
            logging.debug('con = %r', con)
            résultat = con.execute(requête)
            logging.debug('résultat = %r', résultat)
            res = pd.Index(r['index'] for r in résultat)
            logging.debug('res = %r', res)
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
        logging.debug('table = %r\tcolumns = %r\twhere = %r\terrors = %r',
                      table, columns, where, errors)
        if columns is None:
            columns = self.columns(table)
        logging.debug('columns = %r', columns)

        res = self.select(table, columns, where, errors).loc
        logging.debug('res = %r', res)

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
        logging.debug('table = %r\tcolumns = %r\twhere = %r\terrors = %r',
                      table, columns, where, errors)
        if columns is None:
            columns = self.columns(table)
        logging.debug('columns = %r', columns)

        res = self.select(table, columns, where, errors).iloc
        logging.debug('res = %r', res)

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
        logging.debug('chemin = %r', chemin)
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
        logging.debug('table = %r\tchemin = %r\ttype_fichier = %r',
                      table, chemin, type_fichier)

        if type_fichier is None:
            type_fichier = self.deviner_type_fichier(chemin)
        elif isinstance(type_fichier, str):
            type_fichier = TYPES_FICHIERS[type_fichier]
        logging.debug('type_fichier = %r', type_fichier)

        df = type_fichier(chemin, index_col='index')
        logging.debug('df = %r', df)

        self.màj(table, df)


def main(dossier: str = None) -> tuple[BaseDeDonnées, sqla.MetaData]:
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
    logging.basicConfig(level=logging.DEBUG)
    logging.info('%s main()', __file__)

    logging.info('Définition d\'une base de données...')
    md = sqla.MetaData()
    table = sqla.Table('demo', md,
                       sqla.Column('index', get_type('python', int,
                                                     'sqlalchemy'), primary_key=False),
                       sqla.Column('desc',
                                   get_type('python', str, 'sqlalchemy')))
    logging.info('%r %r', md, table)

    logging.info('Ouverture du fichier de base de données...')

    if dossier is None:
        if len(sys.argv) > 1:
            dossier = pathlib.Path(sys.argv[1]).resolve()
        else:
            fichier = pathlib.Path(__file__).expanduser().resolve()
            dossier = fichier.parent.parent.parent
            logging.info('fichier = %r', fichier)

    logging.info('dossier = %r', dossier)

    if not len(list(dossier.glob('*.db'))):
        (dossier / 'test.db').touch()

    logging.debug('*.db: %s', list(dossier.glob('*.db')))

    fichier = dossier / next(dossier.glob('*.db'))
    logging.info('fichier = %r', fichier)

    adresse = f'sqlite:////{fichier!s}'

    logging.info('adresse = %r', adresse)
    base = BaseDeDonnées(adresse, md)
    logging.info('base = %r', base)

    logging.info('Réinitialiser la base de données...')
    base.réinitialiser()

    logging.info('Base de données définie:')
    for t, T in base.tables.items():
        logging.info('%r: %r', t, T.columns)

    logger.info('Ajout de rangées:')
    df = base.select('demo')
    logging.info('Départ:\n%s', df)

    idx = pd.Index([0, 1, 2], name='index')
    df = pd.DataFrame({'desc': ['test 1', 'test 2', 'encore (3)']}, index=idx)
    logging.info('Données à ajouter:\n%s', df)

    base.append('demo', df)
    df = base.select('demo')
    logging.info('Données ajoutées:\n%s', df)

    return base, md
