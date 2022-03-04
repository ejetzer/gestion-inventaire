#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vérifications des heures de travail.

Created on Tue Oct 19 12:53:56 2021

@author: ejetzer
"""

import warnings
import configparser

from pathlib import Path

from pandas import DataFrame

from .mise_a_jour import FeuilleDeTemps
from .calendrier import Calendrier


class AvertissementAdministratif(UserWarning):
    """Avertissement administratif."""

    pass


class TravailLaFinDeSemaine(AvertissementAdministratif):
    """Si on travaille la fin de semaine."""

    pass


class AvertissementQuotidien(AvertissementAdministratif):
    """Si le nombre d'heures dans une journée est inadéquat."""

    pass


class JourTropCourt(AvertissementQuotidien):
    """Si on travaille trop peu d'heures."""

    pass


class JourTropLong(AvertissementQuotidien):
    """Si on travaille trop d'heures."""

    pass


class AvertissementHebdomadaire(AvertissementAdministratif):
    """Si le nombre d'heures dans une semaine est inadéquat."""

    pass


class SemaineTropCourte(AvertissementHebdomadaire):
    """Si on travaille trop peu dans une semaine."""

    pass


class SemaineTropLongue(AvertissementHebdomadaire):
    """Si on travaille trop dans une semaine."""

    pass


avertissements = [TravailLaFinDeSemaine,
                  JourTropCourt,
                  JourTropLong,
                  SemaineTropCourte,
                  SemaineTropLongue]


def pas_de_travail_la_fin_de_semaine(feuille: DataFrame):
    """
    Vérifier si je travaille la fin de semaine.

    Parameters
    ----------
    feuille : DataFrame
        DESCRIPTION.

    Returns
    -------
    heures_fds : TYPE
        DESCRIPTION.

    """
    heures_quotidiennes = feuille.loc[:, [
        'Date', 'Heures']].groupby('Date').sum()
    fds = heures_quotidiennes.index.map(lambda x: x.weekday() in [5, 6])
    heures_fds = heures_quotidiennes.loc[fds, :]
    heures_fds = heures_fds.assign(Avertissement='Travail la fin de semaine')
    return heures_fds


def au_moins_sept_heures_par_jour(feuille: DataFrame):
    """
    Vérifier si je travaille assez.

    Parameters
    ----------
    feuille : DataFrame
        DESCRIPTION.

    Returns
    -------
    heures_peu : TYPE
        DESCRIPTION.

    """
    heures_quotidiennes = feuille.loc[:, [
        'Date', 'Heures']].groupby('Date').sum()
    sem = heures_quotidiennes.index.map(lambda x: x.weekday() not in [5, 6])
    heures_sem = heures_quotidiennes.loc[sem, :]
    peu = heures_sem.Heures < 7
    heures_peu = heures_sem.loc[peu, :]
    heures_peu = heures_peu.assign(
        Avertissement='Peu d\'heures dans une journée')
    return heures_peu


def au_plus_dix_heures_par_jour(feuille: DataFrame):
    """
    Vérifier si je ne travaille pas trop.

    Parameters
    ----------
    feuille : DataFrame
        DESCRIPTION.

    Returns
    -------
    heures_trop : TYPE
        DESCRIPTION.

    """
    heures_quotidiennes = feuille.loc[:, [
        'Date', 'Heures']].groupby('Date').sum()
    sem = heures_quotidiennes.index.map(lambda x: x.weekday() not in [5, 6])
    heures_sem = heures_quotidiennes.loc[sem, :]
    trop = heures_sem.Heures > 10
    heures_trop = heures_sem.loc[trop, :]
    heures_trop = heures_trop.assign(
        Avertissement='Trop d\'heures dans une journée')
    return heures_trop


def au_moins_trente_heures_par_semaine(feuille: DataFrame):
    """
    Vérifier si je travaille assez.

    Parameters
    ----------
    feuille : DataFrame
        DESCRIPTION.

    Returns
    -------
    heures_peu : TYPE
        DESCRIPTION.

    """
    heures_hebdomadaires = feuille.loc[:, ['Date', 'Heures']].groupby(
        lambda x: feuille.at[x, 'Date'].isocalendar().week).sum()
    peu = heures_hebdomadaires.Heures < 30
    heures_peu = heures_hebdomadaires.loc[peu, :]
    heures_peu = heures_peu.assign(
        Avertissement='Peu d\'heures dans une semaine')
    return heures_peu


def au_plus_quarante_cinq_heures_par_semaine(feuille: DataFrame):
    """
    Vérifier si je ne travaille pas trop.

    Parameters
    ----------
    feuille : DataFrame
        DESCRIPTION.

    Returns
    -------
    heures_trop : TYPE
        DESCRIPTION.

    """
    heures_hebdomadaires = feuille.loc[:, ['Date', 'Heures']].groupby(
        lambda x: feuille.at[x, 'Date'].isocalendar().week).sum()
    trop = heures_hebdomadaires.Heures > 45
    heures_trop = heures_hebdomadaires.loc[trop, :]
    heures_trop = heures_trop.assign(
        Avertissement='Trop d\'heures dans une semaine')
    return heures_trop


vérifications = [pas_de_travail_la_fin_de_semaine,
                 au_moins_sept_heures_par_jour,
                 au_plus_dix_heures_par_jour,
                 au_moins_trente_heures_par_semaine,
                 au_plus_quarante_cinq_heures_par_semaine]


def main(cfg):
    """
    Vérifier les heures.

    Parameters
    ----------
    cfg : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    cal_cfg = cfg['Calendrier']
    racine = Path(cal_cfg['ics']).expanduser()
    calendrier = Calendrier(cal_cfg['compte'], cal_cfg['cal'], racine)

    with FeuilleDeTemps(calendrier, **cfg['Polytechnique']) as feuille:
        feuille.charger()

        for test, avertissement in zip(vérifications, avertissements):
            résultat = test(feuille.tableau)
            for i, ligne in résultat.iterrows():
                warnings.warn(f'{ligne}', avertissement)


if __name__ == '__main__':
    cfg = configparser.ConfigParser()
    cfg.optionxform = str
    cfg.read('Configuration.txt')

    main(cfg)
