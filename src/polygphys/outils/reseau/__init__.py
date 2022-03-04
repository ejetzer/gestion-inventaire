# -*- coding: utf-8 -*-
"""
Gestion de connexions réseau.

Facilite les connexions à des disques réseau ou à des VPNs.
"""

import time

from subprocess import run
from pathlib import Path


class ExceptionDisqueReseau(Exception):
    """Exception générique avec les disques réseau."""

    pass


class LePointDeMontageExiste(ExceptionDisqueReseau):
    """Le point de montage existe déjà."""

    pass


class LeVolumeNEstPasMonte(ExceptionDisqueReseau):
    """Le volume n,est pas monté."""

    pass


class LePointDeMontageNExistePas(ExceptionDisqueReseau):
    """Le point de montage n'existe pas."""

    pass


class ErreurDeMontage(ExceptionDisqueReseau):
    """Le montage n'a pas réussi."""

    pass


class DisqueRéseau:
    """Disque réseau."""

    @staticmethod
    def mount_cmd(nom: str, mdp: str, url: str, mode: str, chemin: Path):
        """Commande de montage de disque."""
        return ['mount', '-t', mode, f'//{nom}:{mdp}@{url}', str(chemin)]

    @staticmethod
    def unmount_cmd(chemin: Path):
        """Commande de démontage de disque."""
        return ['umount', str(chemin)]

    def __init__(self,
                 adresse: str,
                 chemin: Path,
                 nom: str,
                 mdp: str,
                 mode: str = 'smbfs',
                 timeout: int = 10):
        """
        Disque réseau.

        Parameters
        ----------
        adresse : str
            DESCRIPTION.
        chemin : Path
            DESCRIPTION.
        nom : str
            DESCRIPTION.
        mdp : str
            DESCRIPTION.
        mode : str, optional
            DESCRIPTION. The default is 'smbfs'.
        timeout : int, optional
            DESCRIPTION. The default is 10.

        Returns
        -------
        None.

        """
        self.adresse = adresse
        self.chemin = chemin if isinstance(chemin, Path) else Path(chemin)
        self.nom = nom
        self.mdp = mdp
        self.mode = mode
        self.timeout = timeout

    def mount(self):
        """
        Monter le disque.

        Raises
        ------
        ErreurDeMontage
            DESCRIPTION.
        LePointDeMontageExiste
            DESCRIPTION.

        Returns
        -------
        None.

        """
        if not self.exists():
            self.chemin.mkdir()
            res = run(self.mount_cmd(self.nom,
                                     self.mdp,
                                     self.url,
                                     self.mode,
                                     self.chemin))
            for i in range(self.timeout * 1000):
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
        """
        Démonter le disque.

        Raises
        ------
        LeVolumeNEstPasMonte
            DESCRIPTION.
        LePointDeMontageNExistePas
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
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
        """
        Monter sécuritairement.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        self.mount()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Démonter en fin d'utilisation.

        Parameters
        ----------
        exc_type : TYPE
            DESCRIPTION.
        exc_value : TYPE
            DESCRIPTION.
        traceback : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.umount()

    def is_mount(self):
        """
        Vérifie le montage.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        return self.chemin.is_mount()

    def exists(self):
        """
        Vérifie l'existence.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        return self.chemin.exists()

    def __bool__(self):
        """
        Vérifie l'existence et le montage.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        return self.exists() and self.is_mount()

    def __truediv__(self, other):
        """
        Naviguer dans le disque.

        Parameters
        ----------
        other : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        return self.chemin / other

    def __rtruediv__(self, other):
        """Rien."""
        return NotImplemented
