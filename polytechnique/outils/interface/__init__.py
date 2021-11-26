#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
"""
Programme ou module pour ...

Créé le Fri Nov 26 10:41:14 2021

@author: ejetzer
"""

import pathlib

import itertools as it
import tkinter as tk

from tkinter.simpledialog import askstring, askinteger, askfloat
from dataclasses import dataclass, field, InitVar
from typing import Callable, Any, Union

import pandas as pd

from ..database import BaseDeDonnées
from ..database.dtypes import get_type

@dataclass
class InterfaceHandler:
    entrée: Callable[[str, Callable, type], Any]
    texte: Callable[[str], Any]
    bouton: Callable[[str, Callable], Any]
    demander: Callable[[str, type], Callable]
