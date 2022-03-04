# Outils & programmes du département de génie physique de Polytechnique [![Python application](https://github.com/ejetzer/polygphys/actions/workflows/python-app.yml/badge.svg)](https://github.com/ejetzer/polygphys/actions/workflows/python-app.yml) [![CodeQL](https://github.com/ejetzer/polygphys/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/ejetzer/polygphys/actions/workflows/codeql-analysis.yml) [![Upload Python Package](https://github.com/ejetzer/polygphys/actions/workflows/python-publish.yml/badge.svg)](https://github.com/ejetzer/polygphys/actions/workflows/python-publish.yml)

- Installation via PyPI: https://pypi.org/project/polygphys/
    ```
    pip install polygphys
    ```
- Documentation sur Read The Docs: https://polygphys.readthedocs.io/en/latest/
- Contributions via Github: https://github.com/ejetzer/polygphys 



## Prérequis & conseils

Ce programme est en développement actif, et ne devrait être utilisé que

- Si vous avez une bonne idée de la structure du programme;
- Si vous êtes capable de lire et déboguer du [Python]
- Si vous avez [Python] d'installé, avec les modules décrits dans `requirements.txt`
- Si vous pouvez utiliser [Git]

**Pour toutes questions, svp envoyez un courriel à [emile.jetzer@polymtl.ca] avec «_[gestion-inventaire]_» dans le sujet du courriel.

[Python]: https://www.python.org
[Git]: https://git-scm.com/
[emile.jetzer@polymtl.ca]: mailto:emile.jetzer@polymtl.ca?subject=[gestion-inventaire]

## Installation

L'installation de la version stable se fait via `pip`:

```
pip install polygphys
```

Le bon fonctionnement du sous-module `polygphys.outils.appareils` pourrait demander l'installation de logiciel supplémentaire, selon l'utilisation:

1. L'installation des drivers VISA officiels de National Instrument
2. L'installation de drivers supplémentaires USB pour pyUSB.
3. L'installation séparée de pylablib (selon le système d'exploitation)
4. L'installation de drivers Keysight ou Agilent pour cetains adapteurs GPIB sur Windows.

Voir la [page de référence de pyVISA] pour résoudre les problèmes causés par des drivers manquants.

[page de référence de pyVISA]: https://pyvisa.readthedocs.io/projects/pyvisa-py/en/latest/installation.html


## Développement

Le développement se fait sur les branches `alpha` et `beta` en général, parfois sur des branches spécifiques à certaines fonctionnalités. Pour s'en servir et les installer, il faut utiliser `git`:

```
git clone https://github.com/ejetzer/polygphys.git
cd polygphys
git checkout alpha
pip install -e .
```

## À faire

Dans le sous module `polygphys.outils.database`:

0. [ ] Rendre les programmes exécutables avec un argument en ligne de commande & comme application
1. [x] Définir plus adéquatement les bases de données et leurs relations
1. [ ] Filtrer par valeur dans des colonnes
2. [ ] Permettre l'ajout de colonnes de l'intérieur de l'application
3. [ ] Permettre d'ajouter des sections de configuration
4. [x] Permettre d'ajouter des champs de configuration
5. [ ] Placer la base de données dans son propre répertoire git externe, et automatiquement en faire des sauvegardes
6. [x] Rendre le logging plus compatible avec sqlalchemy.
7. [ ] Retirer les logs sql, utiliser ceux de sqlalchemy à la place.

Dans les sous modules `polygphys.laboratoires`, `polygphys.outils.appareils` et `polygphys.sst`:

8. [ ] Intégrer les applications externes
    - Certificats laser
    - PHS8302

En général:

1. [ ] Compléter la suite de tests