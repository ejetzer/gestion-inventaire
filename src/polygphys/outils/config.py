#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Enveloppe pour les fichiers de configuration.

Permet de garder en mémoire le chemin du fichier.

Created on Mon Nov 22 14:22:36 2021

@author: ejetzer
"""

import logging
import sys

from pathlib import Path
from configparser import ConfigParser
from urllib.parse import urlparse


class FichierConfig(ConfigParser):
    """Garde ConfigParser synchronisé avec un fichier."""

    def __init__(self,
                 chemin: Path,
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
        logging.debug('chemin = %r\tinline_comment_prefixes = %r\tkargs = %r',
                      chemin,
                      inline_comment_prefixes,
                      kargs)
        self.chemin = chemin

        if not self.chemin.exists():
            self.chemin.touch()
            with self.chemin.open('w') as f:
                f.write(self.default())

        super().__init__(inline_comment_prefixes=inline_comment_prefixes,
                         **kargs)
        self.read()

    def default(self):
        """
        Retourne la configuration par défaut.

        Returns
        -------
        None.

        """
        return f'''[FichierConfig]
    auto: True
    class: {type(self)}
'''

    def read(self):
        """
        Lis le fichier de configuration associé à l'objet.

        Returns
        -------
        None.

        """
        logging.debug('chemin = %r', self.chemin)
        super().read(self.chemin, encoding='utf-8')

    def write(self):
        """
        Écris au fichier les changements à l'objet Python.

        Returns
        -------
        None.

        """
        logging.debug('chemin = %r', self.chemin)
        chemins = (self.chemin,) if isinstance(
            self.chemin, (Path, str)) else self.chemin
        logging.debug('chemins = %r', chemins)

        for chemin in chemins:
            with open(chemin, 'w', encoding='utf-8') as f:
                logging.debug('f = %r', f)
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
        logging.debug('section = %r\toption = %r\tvalue = %r',
                      section,
                      option,
                      value)
        super().set(section, option, value)
        self.write()
        self.read()

    def getlist(self,
                sec: str,
                clé: str,
                fallback: list = tuple()) -> list[str]:
        """
        Transformer une énumération en une liste Python.

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
        logging.debug('sec = %r\tclé = %r\tfallback = %r',
                      sec,
                      clé,
                      fallback)
        val = self.get(sec, clé, fallback=None)
        logging.debug('val = %r', val)

        logging.debug('val is not None = %r', val is not None)

        if val is not None:
            val = list(map(str.strip, val.strip().split('\n')))
        else:
            val = fallback

        logging.debug('val = %r', val)

        return val

    def geturl(self,
               sec: str,
               clé: str,
               fallback: str = '',
               **kargs) -> str:
        """
        Retire une url du fichier de configuration.

        Parameters
        ----------
        sec : str
            Section.
        clé : str
            Clé.
        fallback : str, optional
            Valeur par défaut. The default is ''.
        **kargs : TYPE
            Valeurs à forcer.

        Raises
        ------
        KeyError
            Si clé ou sec n'existent pas.

        Returns
        -------
        str
            Adresse (pour base de données).

        """
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

        logging.debug('d["netloc"] = %r', d['netloc'])
        if d['netloc'] in ('localhost', '127.0.0.1', ''):
            logging.debug('d["path"] = %r', d['path'])
            d['path'] = d['path'].lstrip('\\')
            logging.debug('d["path"] = %r', d['path'])

        if d['nom']:
            d['netloc'] = '@' + d['netloc']

        return '{dialect}{driver}://{nom}{mdp}{netloc}{port}/\
{path}{params}{query}{fragment}'.format(**d)

    def getpath(self,
                sec: str,
                clé: str,
                fallback: str = '') -> Path:
        """
        Obtiens un chemin dans le fichier de configuration.

        Parameters
        ----------
        sec : str
            Section.
        clé : str
            Clé.
        fallback : str, optional
            Valeur par défaut. The default is ''.

        Returns
        -------
        Path
            Chemin.

        """
        champ = self.get(sec, clé, fallback=None)

        if champ is None:
            return fallback

        return Path(champ).expanduser().resolve()

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


def main(dossier: str = None) -> FichierConfig:
    """Exemple très simple d'utilisation du fichier de configuration."""
    logging.basicConfig(level=logging.DEBUG)
    logging.info('Ouvrir un fichier de configuration...')

    if dossier is None:
        if len(sys.argv) > 1:
            dossier = Path(sys.argv[1]).resolve()
        else:
            fichier = Path(__file__).expanduser().resolve()
            dossier = fichier.parent.parent

    fichier = dossier / next(dossier.glob('*.cfg'))
    logging.debug('fichier = %r', fichier)
    logging.debug('fichier.exists() = %r', fichier.exists())

    config = FichierConfig(fichier)
    logging.info('Configuration ouverte...')
    logging.info('config = %r', config)

    logging.info('Assurer la bonne forme de l\'adresse de base de donnée:')
    logging.info(config.geturl('bd', 'adresse', dialect='sqlite'))

    return config


if __name__ == '__main__':
    main()
