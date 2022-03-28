#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""Construire une base de donnée selon un fichier de configuration simple."""

# Bibliothèques standards
import pathlib  # Manipulation de chemins

# Description de signatures de fonctions
from typing import Union, Callable, Any
from functools import partial  # Manipuler des fonctions
from inspect import signature  # Utiliser les signatures de fonctions

# Bibliothèques via PIPy
import sqlalchemy as sqla  # Fonctions et objets de bases de données
import pandas as pd  # Manipulations de données en Python

# Imports relatifs
# Conversion en types internes de différents modules
from ..config import FichierConfig
from .dtypes import get_type

# Certains types de fichiers, pour deviner quelle fonction de lecture
# utiliser quand on importe un fichier dans une base de données.
TYPES_FICHIERS: dict[str, Callable] = {'.xlsx': pd.read_excel,
                                       '.xls': pd.read_excel,
                                       '.csv': pd.read_csv,
                                       '.pickle': pd.read_pickle,
                                       '.txt': pd.read_table}


class BaseDeDonnéesConfig(FichierConfig):

    def default(self):
        return (pathlib.Path(__file__).parent / 'default.cfg').open().read()


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
            https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls
        metadata : sqla.MetaData
            Structure de la base de données.
            https://docs.sqlalchemy.org/en/14/core/schema.html

        Returns
        -------
        None.

        """
        # Adresse de la base de données
        # https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls
        self.adresse = adresse

        # Structure de la base de données
        # https://docs.sqlalchemy.org/en/14/core/schema.html
        self.metadata = metadata

    # Interface de sqlalchemy

    @property
    def tables(self) -> dict[str, sqla.Table]:
        """Liste des tables contenues dans la base de données."""
        res = self.metadata.tables
        return res

    def table(self, table: str) -> sqla.Table:
        """Retourne une table de la base de données."""
        res = self.tables[table]
        return res

    def execute(self, requête, *args, **kargs):
        """Exécute la requête SQL donnée et retourne le résultat."""
        with self.begin() as con:
            res = con.execute(requête, *args, **kargs)
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
        # Si aucune colonne n'est spécifiée, on les prends toutes.
        if not len(columns):
            columns = self.columns(table)

        # Si une liste de colonnes est fournie, on vérifie qu'elles sont
        # toutes présentes dans le tableau.
        # On utilise aussi les objets Column du tableau
        columns = [self.table(table).columns['index']] + list(
            filter(lambda x: x.name in columns, self.table(table).columns))

        requête = sqla.select(columns).select_from(self.table(table))

        for clause in where:
            requête = requête.where(clause)

        with self.begin() as con:
            df = pd.read_sql(requête, con, index_col='index')

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
        requête = self.table(table).update()

        index = values.index.name
        it = values.iterrows()
        for i, rangée in it:
            clause = self.table(table).columns[index] == i
            r = requête.where(clause).values(**rangée)
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
        params = [({'index': i} | {c: v for c, v in r.items()})
                  for i, r in values.iterrows()]
        requête = self.table(table).insert(params)
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
        # Réassigner les indices:
        # On veut s'assurer qu'ils sont tous plus hauts
        # que le dernier indice déjà dans le tableau.
        indice_min = max(self.index(table), default=-1) + 1
        nouvel_index = pd.Index(range(len(values.index)),
                                name='index') + indice_min

        # Faire une copie des valeurs avec le bon index.
        values = values.copy()
        values.index = nouvel_index

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
        requête = self.table(table).delete()

        # Réparation temporaire
        if isinstance(values, pd.DataFrame):
            index = values.index.name
            idx = values.index
        else:
            index = 'index'
            idx = pd.Index([values], name='index')
        for i in idx:
            clause = self.table(table).columns[index] == 1
            r = requête.where(clause)
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
        index = self.index(table)
        existe = values.index.isin(index)

        if existe.any():
            self.update(table, values.loc[existe, :])

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
        return sqla.create_engine(str(self.adresse), future=True)

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
        with self.begin() as con:
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
        with self.begin() as con:
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
        type_champ = self.table(table).columns[champ].type
        type_champ: str = get_type('sqlalchemy', type_champ, 'pandas')
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
        cols = self.columns(table)
        dtypes = map(lambda x: self.dtype(table, x), self.columns(table))
        dtypes = pd.Series(dtypes, index=cols)

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
        res = pd.Index(c.name for c in self.table(
            table).columns if c.name != 'index')

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
        requête = sqla.select([self.table(
            table).columns['index']]).select_from(self.table(table))

        with self.begin() as con:
            résultat = con.execute(requête)
            res = pd.Index(r['index'] for r in résultat)
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
        if columns is None:
            columns = self.columns(table)

        res = self.select(table, columns, where, errors).loc

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
        if columns is None:
            columns = self.columns(table)

        res = self.select(table, columns, where, errors).iloc

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
        return TYPES_FICHIERS[chemin.suffix]

    def read_file(self,
                  table: str,
                  chemin: pathlib.Path,
                  type_fichier: Union[str, Callable] = None):
        """
        Importer un fichier dans la base de données.

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
        if type_fichier is None:
            type_fichier = self.deviner_type_fichier(chemin)
        elif isinstance(type_fichier, str):
            type_fichier = TYPES_FICHIERS[type_fichier]

        df = type_fichier(chemin, index_col='index')

        self.màj(table, df)


class BaseTableau:
    """Encapsulation de la classe BaseDeDonnées."""

    def __init__(self, db: BaseDeDonnées, table: str):
        """
        Encapsule de la classe BaseDeDonnées.

        Avec accès seulement à la table table.

        Parameters
        ----------
        db : BaseDeDonnées
            Une interface à une base de données.
        table : str
            Le nom d'un tableau dans db.

        Returns
        -------
        None.

        """
        self.table: str = table
        self.db: BaseDeDonnées = db

    def __getattr__(self, attr: str) -> Any:
        """
        Obtiens un attribut de self.db ou self.df.

        Facilite l'encapsulation.
        BaseDeDonnées a la priorité, ensuite pandas.DataFrame.

        Parameters
        ----------
        attr : str
            Attribut à obtenir.

        Raises
        ------
        AttributeError
            Si l'attribut ne peut pas être trouvé.

        Returns
        -------
        Any
            L'attribut demandé.

        """
        if hasattr(BaseDeDonnées, attr):
            obj = getattr(self.db, attr)

            if isinstance(obj, Callable):
                sig = signature(obj)

                if len(sig.parameters) == 1 and 'table' in sig.parameters:
                    return partial(obj, self.table)()
                elif 'table' in sig.parameters:
                    return partial(obj, self.table)
                else:
                    return obj
            else:
                return obj
        elif hasattr(pd.DataFrame, attr):
            return getattr(self.df, attr)
        else:
            msg = f'{self!r} de type {type(self)} n\'a pas d\'attribut {attr}\
, ni (self.__db: BaseDeDonnées, self.df: pandas.DataFrame).'
            raise AttributeError(msg)

    @property
    def df(self) -> pd.DataFrame:
        """Le tableau comme pandas.DataFrame."""
        return self.select()

    def append(self, values: Union[pd.Series, pd.DataFrame] = None):
        """
        Ajoute des valeurs au tableau.

        Parameters
        ----------
        values : Union[pd.Series, pd.DataFrame], optional
            Valeurs à ajouter. The default is None.

        Returns
        -------
        None.

        """
        if values is None:
            cols, idx = self.columns, [max(self.index, default=-1) + 1]
            values = pd.DataFrame(None, columns=cols, index=[idx])
        elif isinstance(values, pd.Series):
            cols, idx = self.columns, [max(self.index, default=-1) + 1]
            values = pd.DataFrame([values], index=[idx])

        self.db.append(self.table, values)
