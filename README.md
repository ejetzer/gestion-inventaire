# Gestion d'inventaire

Programme de gestion d'inventaire minimal, avec une base de données.

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

## Fichiers

1. `afficher_dataframe.py` est une module Python contenant la classe `Tableau`, qui permet d'afficher des `pandas.DataFrame` dans `tkinter`.
2. `définir_db.py` permet de définir la structure d'une base de données, telle que décrit dans `référence.config`.
3. `onglets.py` permet d'afficher et éditer le fichier de configuration et les bases de données qui y sont décrites. **Il s'agit du fichier à exécuter.**
4. `*.db` sont les fichiers de base de données SQL. SVP ne pas y toucher.
5. `*.config` sont des fichiers de configuration.

## Configuration

Le fichier de configuration comporte différentes sections:

1. `base de données` contient les informations sur la base de données et les tables de données à utiliser.
2. `common` contient une liste des champs communs à toutes les bases de données.
3. Les autres sections décrivent différentes tables de données.

### Base de données

1. `adresse` indique la position du fichier de base de données, et le protocole SQLAlchemy à utiliser. En ce moment n'utilisez que `sqlite`, qui stocke la base de données dans un fichier localement.
2. `tables` doit être une valeur littérale de liste de chaînes en Python, contenant les tables de la base de données à considérer.

### Common

Les champs `index`, `quantité` et `description` sont communs à toutes les tables de données.

1. `index` est un nombre unique à chaque élément à l'intérieur d'une même table. On doit le considérer comme immuable, et on peut utiliser le nom de table et l'index pour désigner un élément particulier avec précision et sans ambiguité.
2. `quantité` désigne la qantité d'un item qu'on a en inventaire
3. `description` décrit l'item. Il n'y a pas de limite de longueur, n'hésitez pas à inclure des détails.

### Boîtes

La table des boîtes est la seule en service actif en ce moment, pour tester le système.

# À faire

- [ ] Permettre l'ajout de colonnes de l'intérieur de l'application
- [ ] Permettre d'effacer des rangées
- [ ] Permettre d'ajouter des sections de configuration
- [ ] Permettre d'ajouter des champs de configuration
- [ ] Placer la base de données dans son propre répertoire git externe, et automatiquement en faire des sauvegardes
- [ ] Faciliter l'importation de documents Excel & d'autres bases de données
