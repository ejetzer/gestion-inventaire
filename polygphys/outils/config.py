#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Enveloppe pour les fichiers de configuration.

Permet de garder en mémoire le chemin du fichier.

Created on Mon Nov 22 14:22:36 2021

@author: ejetzer
"""

import logging

from pathlib import Path
from configparser import ConfigParser
from typing import Union, Iterable
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class FichierConfig(ConfigParser):
    """Garde ConfigParser synchronisé avec un fichier."""

    def __init__(self,
                 chemin: Union[Iterable[Path], Path],
                 inline_comment_prefixes=('#', ';'),
                 **kargs):
        """
        Sous-classe de configparser.ConfigParser.

        Garde le fichier de configuration synchrone avec l'objet Python.

        Parameters
        ----------
        chemin : Union[Iterable[Path], Path]
            Le chemin vers le fichier de configuration.
        inline_comment_prefixes : TYPE, optional
            Début de commentaire. The default is ('#', ';').
        **kargs : TYPE
            Autres paramètres transmis au parent.

        Returns
        -------
        None.

        """
        logger.debug(
            f'{self!r} {chemin=!r} {inline_comment_prefixes=!r} {kargs=!r}')
        self.chemin = chemin
        super().__init__(inline_comment_prefixes=inline_comment_prefixes,
                         **kargs)
        self.read()

    def read(self):
        """
        Lis le fichier de configuration associé à l'objet.

        Returns
        -------
        None.

        """
        logger.debug(f'{self!r} .read({self.chemin=})')
        super().read(self.chemin, encoding='utf-8')

    def write(self):
        """
        Écris au fichier les changements à l'objet Python.

        Returns
        -------
        None.

        """
        logger.debug(f'{self!r} FichierConfig.write({self.chemin=})')
        chemins = (self.chemin,) if isinstance(
            self.chemin, (Path, str)) else self.chemin
        logger.debug(f'{chemins!r}')

        for chemin in chemins:
            with open(chemin, 'w', encoding='utf-8') as f:
                logger.debug(f'{f!r}')
                super().write(f)

    def set(self, section: str, option: str, value: str):
        """
        Change la valeur d'un champ.

        Parameters
        ----------
        section : str
            Section du fichier de configuration.
        option : str
            Champ à modifier.
        value : str
            Valeur à assigner.

        Returns
        -------
        None.

        """
        logger.debug(f'{self!r}[{section!r}][{option!r}] = {value!r}')
        super().set(section, option, value)
        self.write()

    def getlist(self,
                sec: str,
                clé: str,
                fallback: list = tuple()) -> list[str]:
        """
        Transforme une énumération en une liste Python.

        Parameters
        ----------
        sec : str
            Section du fichier de configuration.
        clé : str
            Champ à obtenir.
        fallback : list, optional
            Valeur par défaut. The default is [].

        Returns
        -------
        list[str]
            DESCRIPTION.

        """
        logger.debug(f'{self!r} .getlist({sec=}, {clé=}, {fallback=})')
        val = self.get(sec, clé, fallback=None)
        logger.debug(f'{self!r} .getlist(...) {val=}')

        logger.debug(f'{self!r} .getlist(...) {val is not None=}')

        if val is not None:
            val = list(map(str.strip, val.strip().split('\n')))
        else:
            val = fallback

        logger.debug(f'{self!r} .getlist(...) {val=}')

        return val

    def geturl(self,
               sec: str,
               clé: str,
               fallback: str = '',
               **kargs):
        champ = self.get(sec, clé, fallback=None)

        if champ is None and fallback != '':
            champ = fallback
        elif champ is None:
            raise KeyError(f'{clé!r} not found in {sec!r}.')

        url = urlparse(champ)
        d = {'dialect': '',
             'driver': '',
             'nom': '',
             'mdp': '',
             'netloc': '',
             'port': '',
             'path': '',
             'params': '',
             'query': '',
             'fragment': ''}

        if '+' in url.scheme:
            d['dialect'], d['driver'] = url.scheme.split('+')
        else:
            d['dialect'] = url.scheme

        if '@' in url.netloc:
            userdetails, d['netloc'] = url.netloc.split('@')
        else:
            userdetails, d['netloc'] = '', url.netloc

        if ':' in d['netloc']:
            d['netloc'], d['port'] = d['netloc'].split(':')

        if ':' in userdetails:
            d['nom'], d['mdp'] = userdetails.split(':')
        else:
            d['nom'] = userdetails

        d['path'] = url.path
        d['params'] = url.params
        d['query'] = url.query
        d['fragment'] = url.fragment

        for c in d.keys() & kargs.keys():
            d[c] = kargs[c]

        for clé, préfixe in (('driver', '+'),
                             ('mdp', ':'),
                             ('port', ':'),
                             ('params', ';'),
                             ('query', '?'),
                             ('fragment', '#')):
            if d[clé]:
                d[clé] = préfixe + d[clé]

        logger.debug(f'{self!r} .geturl {d["netloc"]=!r}')
        if d['netloc'] in ('localhost', '127.0.0.1', ''):
            logger.debug(f'{self!r} .geturl {d["path"]=}')
            d['path'] = str(Path(d['path'].strip('/')).expanduser())
            logger.debug(f'{self!r} .geturl {d["path"]=}')

        if d['nom']:
            d['netloc'] = '@' + d['netloc']

        if not d['netloc'].endswith('/'):
            d['netloc'] = d['netloc'] + '/'
        if Path(d['path']).is_absolute():
            d['netloc'] = d['netloc'] + '//'
        else:
            d['netloc'] = d['netloc'] + '/'

        return '{dialect}{driver}://{nom}{mdp}{netloc}{port}{path}{params}{query}{fragment}'.format(**d)

    def getpath(self,
                sec: str,
                clé: str,
                fallback: str = '') -> Path:
        champ = self.get(sec, clé, fallback=None)

        if champ is None:
            return fallback

        return Path(champ).expanduser().absolute()

    def __str__(self) -> str:
        """
        Retourne le contenu du fichier de configuration.

        Returns
        -------
        str
            Contenu du fichier de configuration.

        """
        résultat = ''
        for n in self.sections():
            sec = self[n]
            résultat += f'[{n}]\n'
            for n, v in sec.items():
                résultat += f'\t{n}: {v}\n'
        return résultat


def main(fichier: str = None) -> FichierConfig:
    """Exemple très simple d'utilisation du fichier de configuration."""
    logger.info('Ouvrir un fichier de configuration...')
    import pathlib

    if fichier is None:
        fichier = pathlib.Path(
            __file__).parent.absolute() / '../base.cfg'

    config = FichierConfig(fichier)
    logger.info('Configuration ouverte...')
    logger.info(f'{config=}')

    logger.info('Assurer la bonne forme de l\'adresse de base de donnée:')
    logger.info(config.geturl('bd', 'adresse', dialect='sqlite'))

    return config


if __name__ == '__main__':
    main()
