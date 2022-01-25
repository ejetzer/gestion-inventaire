#!python
# -*- coding: utf-8 -*-
"""
Programme ou module pour ...

Créé le Thu Jan 13 09:45:19 2022

@author: ejetzer
"""

from collections import namedtuple
from decimal import Decimal

import numpy as np

from matplotlib import pyplot as plt

from ..appareils import Appareil, Expérience


class HP4274A(Appareil):

    def bias(self, potential: float) -> str:
        signe, chiffres, exposant = Decimal(potential).as_tuple()
        mantisse = ''.join(chiffres[:3])
        signe = {0: '+', 1: '-'}[signe]
        return self.query(f'BI {signe}{mantisse} E {exposant:+02d} V')

    def set(display_a_function: int = None,
            display_b_function: int = None,
            circuit_mode: int = None,
            deviation_measurement: int = None,
            frequency_step: int = None,
            high_resolution: int = None,
            data_ready: int = None,
            key_status_output: bool = None,
            level_monitor: str = None,
            multiplier: int = None,
            LCRZ_range: int = None,
            self_test: bool = None,
            trigger: int = None,
            zero_open: bool = None):
        pass

    def get(self, param: str = None) -> namedtuple:
        pass


class PHS8302_CV(Expérience):

    def run(self):
        impedance_metre = HP4274A('GPIB::16::INSTR')

        vs = np.linspace(-6, 6, 100)

        for f_mode in range(11, 21):
            f_mode = f'F{f_mode}'
            impedance_metre.query(f_mode)

            cs = [impedance_metre.bias(v) for v in vs]

            plt.plot(vs, cs, label=f_mode)

            with open(f_mode + '.txt', 'w') as F:
                print('\t'.join(vs), file=F)
                print('\t'.join(cs), file=F)

        plt.legend()
        plt.show()


if __name__ == '__main__':
    pass
