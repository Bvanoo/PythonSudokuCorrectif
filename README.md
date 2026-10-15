# PythonSudokuCorrectif

Correctif d'un exercice de formation : un **Sudoku jouable dans le terminal**, écrit en Python avec la bibliothèque `curses`.

Le code est construit pas à pas et commenté pour expliquer le *pourquoi* de chaque choix, afin de servir de support avec des stagiaires.

## Objectifs pédagogiques

- Représenter une grille avec une liste de listes (`board[ligne][colonne]`)
- Implémenter les règles du Sudoku (ligne, colonne, bloc 3x3)
- Découvrir le **backtracking** (essai, erreur, retour en arrière) et la récursion
- Séparer la logique du jeu de l'affichage
- Gérer une **boucle de jeu** interactive : afficher, lire une touche, modifier l'état

## Prérequis

- Python 3.6 ou supérieur
- Un terminal d'au moins **65 colonnes x 22 lignes**
- Sous Windows uniquement, `curses` n'est pas fourni :

```bash
pip install windows-curses
```

## Lancer le jeu

```bash
python main.py
```

## Commandes

| Touche                  | Action                                      |
| ----------------------- | ------------------------------------------- |
| Flèches                 | Déplacer le curseur                         |
| `1` à `9`               | Placer un chiffre                           |
| `Suppr` / `Retour` / `0`| Effacer la case                             |
| `v`                     | Vérifier la case sous le curseur            |
| `c`                     | Afficher la correction complète             |
| `q`                     | Quitter                                     |

Les cases d'origine apparaissent en **gras** et ne sont pas modifiables.

## Structure du code

Le fichier `main.py` suit cinq étapes :

| Étape | Contenu                                                              |
| ----- | -------------------------------------------------------------------- |
| 1     | `create_empty_board`, `is_valid` : la grille et les règles           |
| 2     | `fill_grid_backtracking`, `generate_puzzle` : génération du puzzle   |
| 3     | `check_victory` : détection de la victoire                           |
| 4     | `draw_grid` : affichage dans le terminal                             |
| 5     | `main` : boucle de jeu et actions du joueur                          |

## Fonctionnement de la génération

1. On remplit une grille **complète et valide** par backtracking, en mélangeant les chiffres pour varier les parties.
2. On en garde une copie : c'est la **solution**.
3. On vide 40 cases au hasard pour obtenir le puzzle.

Avoir la solution sous la main permet de vérifier le joueur et de proposer la correction.

## Limites connues

Pistes d'amélioration à proposer en exercice :

- Le puzzle n'est **pas garanti à solution unique** : une grille valide mais différente de la solution stockée ne déclenche pas la victoire.
- Pas de niveaux de difficulté (le nombre de cases vides est fixé à 40 dans `generate_puzzle`).
- Pas de détection des conflits en direct (doublon sur une ligne, une colonne ou un bloc).
- Pas de chronomètre ni de sauvegarde de partie.
