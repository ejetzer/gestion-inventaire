#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 11:22:11 2022

@author: emilejetzer
"""

import tkinter as tk

from ..laser import Fenetre

def main():
    """
    Script principal: créer et faire rouler l'interface.

    Retourne
    -------
    None.

    """
    _ = tk.Tk()
    app = Fenetre(parent=_)
    app.mainloop()


if __name__ == '__main__':
    main()
