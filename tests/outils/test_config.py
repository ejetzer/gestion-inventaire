#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 17:06:19 2022

@author: emilejetzer
"""

import pytest


def test_import():
    import polygphys.outils.config
    polygphys.outils.config


def test_FichierConfig():
    from polygphys.outils.config import FichierConfig
    from pathlib import Path

    chemin = Path('test_FichierConfig.cfg')
    fichier_config = FichierConfig(chemin)

    try:
        assert 'FichierConfig' in fichier_config.sections()
        assert fichier_config.get('FichierConfig', 'auto') == 'True'
        assert 'FichierConfig' in fichier_config.get('FichierConfig', 'class')
    finally:
        chemin.unlink()


def test_FichierConfig_edition():
    from polygphys.outils.config import FichierConfig
    from pathlib import Path

    chemin = Path('test_FichierConfig.cfg')
    fichier_config = FichierConfig(chemin)

    try:
        fichier_config.add_section('test')
        fichier_config['test']['soustest'] = '245'
        assert fichier_config['test']['soustest'] == 'allo'
        assert fichier_config.getint('test', 'soustest') == 245
    finally:
        chemin.unlink()


def test_FichierConfig_getlist():
    from polygphys.outils.config import FichierConfig
    from pathlib import Path

    chemin = Path('test_FichierConfig.cfg')
    fichier_config = FichierConfig(chemin)

    try:
        fichier_config.add_section('pytest')
        assert 'pytest' in fichier_config.sections()

        fichier_config.set('pytest', 'liste', '\n\t'.join(['1', '2', '3']))
        assert fichier_config.getlist('pytest', 'liste') == ['1', '2', '3']
    finally:
        chemin.unlink()


def test_FichierConfig_getpath():
    from polygphys.outils.config import FichierConfig
    from pathlib import Path

    chemin = Path('test_FichierConfig.cfg')
    fichier_config = FichierConfig(chemin)

    try:
        fichier_config.add_section('pytest')
        assert 'pytest' in fichier_config.sections()

        fichier_config.set('pytest', 'chemin', __file__)
        assert __file__ == str(Path(__file__))
        assert fichier_config.getpath('pytest', 'chemin') == Path(__file__)
    finally:
        chemin.unlink()


def test_FichierConfig_geturl():
    from polygphys.outils.config import FichierConfig
    from pathlib import Path
    from urllib.parse import urlparse

    chemin = Path('test_FichierConfig.cfg')
    fichier_config = FichierConfig(chemin)

    try:
        fichier_config.add_section('pytest')
        assert 'pytest' in fichier_config.sections()

        fichier_config.set('pytest', 'url', 'http://test.com/')
        assert fichier_config.geturl(
            'pytest', 'url') == urlparse('http://test.com/')
    finally:
        chemin.unlink()
