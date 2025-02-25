# Simulateur SGBD SQLite

Un simulateur de base de données SQLite avec interface graphique PyQt5.

## Pour Commencer

### Cloner le dépôt
```plaintext
Pour créer une clé SSH et cloner le dépôt :

1. Générer une nouvelle clé SSH :

ssh-keygen -t ed25519 -C "votre@email.com"

2. Démarrer l'agent SSH :
windows :
-cmd
start ssh-agent
ssh-add %USERPROFILE%\.ssh\id_ed25519

-powershell
Start-Service ssh-agent
ssh-add $env:USERPROFILE\.ssh\id_ed25519


linux
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

3. Copier la clé publique :
windows:
-cmd
type %USERPROFILE%\.ssh\id_ed25519.pub
-powershell
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub

linux:
cat ~/.ssh/id_ed25519.pub

4. Ajouter la clé dans GitHub :
   - Aller dans Settings > SSH and GPG keys
   - Cliquer sur "New SSH key"
   - Coller la clé publique
   - Sauvegarder
```
5. Cloner le dépôt :

git clone git@github.com:1Cryptify/SGBDsimulator.git
cd SGBDsimulator

### Installation des dépendances

pip install -r requirements.txt

## Structure du Projet

```plaintext
sgbd_simulator/
│
├── src/
│   ├── __init__.py              # Fichier d'initialisation du package src
│   ├── main.py                  # Point d'entrée de l'application
│   │
│   ├── gui/
│   │   ├── __init__.py          # Fichier d'initialisation du package gui
│   │   ├── main_window.py       # Fenêtre principale de l'application
│   │   └── widgets/             # Répertoire pour les composants d'interface personnalisés
│   │
│   ├── modules/
│   │   ├── database_connector.py    # Module de connexion à la base de données
│   │   ├── schema_manager.py        # Gestion des schémas (tables)
│   │   ├── crud_operator.py         # Opérations CRUD sur les données
│   │   ├── data_viewer.py           # Visualisation des données
│   │   ├── query_executor.py        # Exécution des requêtes SQL
│   │   └── ui_coordinator.py        # Coordination de l'interface utilisateur
│   │
│   └── utils/
│       ├── constants.py         # Constantes globales du projet
│
├── tests/                       # Répertoire pour les tests unitaires
├── requirements.txt             # Fichier listant les dépendances du projet
└── README.md                   # Documentation principale du projet
```
## Répartition des Tâches par Équipe

### Équipe Core

#### EBAKISSE: Optimisation de la Connexion BD

- Implémentation de database_connector.py
- Gestion du pool de connexions
- Administration des sessions BD
- Sécurisation des accès à la base

Pour push vos modifications:
```python
git add src/modules/database_connector.py
git commit -m "Description des modifications"
git push origin main
```
#### FOMEKOUO: Coordination Interface Utilisateur

- Développement de ui_coordinator.py
- Conception de la mise en page principale
- Gestion des interactions entre widgets
- Design de l'expérience utilisateur

Pour push vos modifications:
```python
git add src/modules/ui_coordinator.py
git commit -m "Description des modifications"
git push origin main
```
### Équipe Fonctionnalités

#### EFONTSE: Gestion des Schémas

- Implémentation de schema_manager.py
- Création et modification des tables
- Administration de la structure BD
- Validation des schémas

Pour push vos modifications:
```python
git add src/modules/schema_manager.py
git commit -m "Description des modifications"
git push origin main
```
#### NJEMI: Opérations CRUD

- Développement de crud_operator.py
- Fonctionnalités de manipulation des données
- Gestion des enregistrements
- Validation des données

Pour push vos modifications:
```python
git add src/modules/crud_operator.py
git commit -m "Description des modifications"
git push origin main
```
#### MEZATIO: Visualisation des Données

- Création de data_viewer.py
- Affichage des résultats
- Design des layouts de présentation
- Export des données

Pour push vos modifications:
```python
git add src/modules/data_viewer.py
git commit -m "Description des modifications"
git push origin main
```
#### TENKWA: Exécution des Requêtes

- Construction de query_executor.py
- Traitement des requêtes SQL
- Gestion des résultats et erreurs
- Optimisation des requêtes

Pour push vos modifications:
```python
git add src/modules/query_executor.py
git commit -m "Description des modifications"
git push origin main## Prérequis Techniques
```
### Environnement de Développement
- Python 3.x
- IDE recommandé: VS Code ou PyCharm
- Git pour le contrôle de version

### Dépendances Principales
- PyQt5: Interface graphique
- SQLite3: Moteur de base de données
- pytest: Tests unitaires

## Lancement de l'Application

python3 src/main.py

## Conventions de Développement

### Style de Code
- PEP 8 pour le formatage Python
- Docstrings pour la documentation
- Nommage en français pour les variables/fonctions

### Gestion des Versions
- Une branche par fonctionnalité
- Pull requests pour les fusions
- Tests obligatoires avant merge

## Documentation

### Pour les Développeurs
- Commenter le code en français
- Maintenir la documentation à jour
- Documenter les APIs des modules

### Pour les Utilisateurs
- Guide d'utilisation à venir
- Captures d'écran des fonctionnalités
- Exemples d'utilisation

## Tests

### Exécution des Tests

pytest tests/

### Couverture de Code
- Minimum 80% de couverture
- Tests unitaires par module
- Tests d'intégration

## Licence

© 2024 Équipe SGBDsimulator. Tous droits réservés.