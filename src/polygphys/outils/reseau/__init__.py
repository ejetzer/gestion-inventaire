# -*- coding: utf-8 -*-
"""
Gestion de connexions réseau.

Facilite les connexions à des disques réseau ou à des VPNs.
"""

import time

from subprocess import run
from pathlib import Path


class ExceptionDisqueReseau(Exception):
    pass


class LePointDeMontageExiste(ExceptionDisqueReseau):
    pass


class LeVolumeNEstPasMonte(ExceptionDisqueReseau):
    pass


class LePointDeMontageNExistePas(ExceptionDisqueReseau):
    pass


class ErreurDeMontage(ExceptionDisqueReseau):
    pass


class DisqueRéseau:

    @staticmethod
    def mount_cmd(nom: str, mdp: str, url: str, mode: str, chemin: Path):
        return ['mount', '-t', mode, f'//{nom}:{mdp}@{url}', str(chemin)]

    @staticmethod
    def unmount_cmd(chemin: Path):
        return ['umount', str(chemin)]

    def __init__(self,
                 adresse: str,
                 chemin: Path,
                 nom: str,
                 mdp: str,
                 mode: str = 'smbfs',
                 timeout: int = 10):
        self.adresse = adresse
        self.chemin = chemin if isinstance(chemin, Path) else Path(chemin)
        self.nom = nom
        self.mdp = mdp
        self.mode = mode
        self.timeout = timeout

    def mount(self):
        if not self.exists():
            self.chemin.mkdir()
            res = run(self.mount_cmd(self.nom,
                                     self.mdp,
                                     self.url,
                                     self.mode,
                                     self.chemin))
            for i in range(self.timeout*1000):
                if self.is_mount():
                    break
                else:
                    time.sleep(0.001)
            if not self.is_mount():
                self.chemin.rmdir()
                raise ErreurDeMontage(f'Valeur retournée de {res}')
        else:
            raise LePointDeMontageExiste(f'{self.chemin!r} existe déjà.')

    def umount(self):
        if self.exists():
            if self.is_mount():
                return run(self.umount_cmd(self.chemin))
            else:
                raise LeVolumeNEstPasMonte(
                    f'{self.url!r} n\'est pas monté au point {self.chemin!r}.')
        else:
            raise LePointDeMontageNExistePas(
                f'Le point de montage {self.chemin!r} n\'existe pas.')

    def __enter__(self):
        self.mount()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.umount()

    def is_mount(self):
        return self.chemin.is_mount()

    def exists(self):
        return self.chemin.exists()

    def __bool__(self):
        return self.exists() and self.is_mount()

    def __truediv__(self, other):
        return self.chemin / other

    def __rtruediv__(self, other):
        return NotImplemented


class VPN:

    def __init__(self, url: str, nom: str, mdp: str):
        pass

    def connect(self):
        pass

    def disconnect(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()
