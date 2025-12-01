# 📌 Projet L3 Algorithmique Avancée --- **Dijkstra MinContraste**

## 📖 Introduction

Ce projet, réalisé dans le cadre du module **Algorithmique Avancée
(L3)**, correspond au **Scénario 2 : Graphes et Image**.\
L'objectif est de modéliser une image numérique sous forme de **graphe
valué** afin de trouver le **chemin de MinContraste**, c'est-à-dire le
chemin dont le coût cumulé (variations d'intensité) est minimal entre
deux pixels sélectionnés par l'utilisateur.

Le calcul du chemin est effectué grâce à l'implémentation de
l'**algorithme de Dijkstra**.

------------------------------------------------------------------------

## 🧠 Modélisation du Problème

### 🔷 Modélisation du Graphe

L'image est transformée en un **graphe non orienté** ( G = (V, E) ), où
:

-   **Sommets (V)** : chaque pixel est un sommet.\
-   **Arêtes (E)** : relient les pixels voisins selon la
    **4-connexité**.\
-   **Poids (W)** : différence absolue d'intensité entre deux pixels
    voisins.

### 🔷 Rôle de Dijkstra et du MinContraste

L'algorithme de **Dijkstra** est utilisé pour déterminer le **chemin à
plus faible contraste cumulé**, ce qui correspond au chemin le plus
"lisse" du point de vue des variations d'intensité.

------------------------------------------------------------------------

## 🛠️ Installation & Prérequis

### 1. Prérequis

Le projet est développé en **Python** et dépend des bibliothèques
suivantes :

-   **PyQt6** (interface graphique)\
-   **OpenCV (opencv-python)** (traitement d'image)\
-   **NumPy** (gestion des matrices)

Installation :

``` bash
pip install PyQt6 opencv-python numpy
```

------------------------------------------------------------------------

## 📁 Structure du Projet

    CodeMiniProjet/
    ├── main.py
    ├── PathSolverApp.py
    ├── GraphModeler.py
    ├── [Votre_Image_Test.jpg]
    └── README.md

------------------------------------------------------------------------

## ▶️ Exécution de l'Application

``` bash
python main.py
```

------------------------------------------------------------------------

## 🖥️ Mode d'Emploi

1.  **Charger une image** : via *Fichier \> Ouvrir...*\
2.  **Sélectionner le départ** : premier clic (vert)\
3.  **Sélectionner l'arrivée** : second clic (bleu)\
4.  **Afficher le résultat** : Dijkstra trace en rouge le chemin le plus
    court\
5.  **Réinitialiser** : troisième clic

------------------------------------------------------------------------

## 🚀 Complexité Algorithmique

L'algorithme de Dijkstra (avec file de priorité) :\
**O(E + V log V)**

Pour une image de taille ( L imes H ) :

-   ( V = L imes H )
-   ( E pprox 4V )

Complexité finale :\
**O(L × H × log(L × H))**

