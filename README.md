# Les Mystérieuses Cités d'Or - Exploration et Stratégie sur Grille 
![Map_jeu](images/map_maya.png)

## Description

Les **Mystérieuses Cités d'Or** est un jeu stratégique en Python où des unités explorent une grille remplie d'énigmes, de trésors, de pièges et plein d'autres.  Chaque unité possède des compétences uniques influençant la stratégie du joueur pour atteindre l'objectif final: **récuperer le trésor**. Ce projet met en avant l'utilisation de la **programmation orientée objet (POO)**.

## Fonctionnalités
- **Exploration de la grille** : Explorer les ruines et évitez les pièges et l'équipe ennemie.
- **Unités spécialisées** :
   - **Explorateur** ![Explorateur](images/explorateur.png) <img src="images/explorateur.png" alt="Explorateur" width="50"> : Détecte les pièges et explore des zones cachées.
   - **Archéologue** ![Archeologue](images/archeologue.png)  : Résout des énigmes pour progresser.
   - **Chasseur** ![Chasseur](images/chasseur_2.png) : Pose des pièges et utilise le brouillard pour reculer ses ennemis.
- **Système de compétences** : Chaque unité utilise des actions spécifiques pour interagir avec la grille, voici quelques unes :
   - `reveler_zone()` : Révélation des cases voisines.
   - `poser_piege()` : Placement de pièges sur la grille.
   - `decrypter_indice()` : Decrypter des énigmes.
- **Effets des cases** :
   - **Pièges** : Infligent des dégâts aux unités.
   - **Trésors** : Objectif final pour gagner la partie.
   - **Indices** : Déclenchent des énigmes à résoudre.
   - **Ressources**: Récuperer des points de vie.
   - **Clé magique** : Récuperer la clé magique afin d'ouvrir une des portes qui mène au trésor.
   - **Portes**: Protègent le trésor, une seule s'ouvre.

-**Comprendre les fonctionnalitées**:
Afin de comprendre les fonctionnalités du jeu, la touche "C" permet de dérouler le menu. 

---

## Technologies Utilisées

- **Python** : Langage de programmation principal.
- **Pygame**: bibliothèque nécessaire à la création du jeu. 
- **Graphviz** : Outil utilisé pour modéliser le diagramme de classes UML.

---

## Prérequis

Pour exécuter ce projet, assurez-vous d'avoir :

- **Python 3.8 ou supérieur** installé.
- Les bibliothèques nécessaires (installables via pip si besoin) tel que pygame. 

---

## Installation et Exécution

1. **Clonez ce dépôt** :
   ```bash
   git clone https://github.com/votre-utilisateur/nom-du-repo.git
