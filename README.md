# Les Mystérieuses Cités d'Or - Exploration et Stratégie sur Grille 
![Map_jeu](images/map_maya.png)

## Description

Les **Mystérieuses Cités d'Or** est un jeu stratégique en Python où des unités explorent une grille remplie d'énigmes, de trésors et de pièges. Chaque unité possède des compétences uniques influençant la stratégie du joueur pour atteindre l'objectif final: récuperer le trésor. Ce projet met en avant l'utilisation de la **programmation orientée objet (POO)**.

## Fonctionnalités
- **Exploration de la grille** : Explorer les ruines et évitez les pièges.
- **Unités spécialisées** :
   - **Explorateur** images/explorateur.png : Détecte les pièges et explore des zones cachées.
   - **Archéologue** images/archeologue.png : Résout des énigmes pour progresser.
   - **Chasseur** images/chasseur_2.Png : Pose des pièges et utilise le brouillard pour reculer ses ennemis.
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

---

## Technologies Utilisées

- **Python** : Langage de programmation principal.
- **POO (Programmation Orientée Objet)** : Structure du code basée sur les classes.
- **Graphviz** : Outil utilisé pour modéliser le diagramme de classes UML.

---

## Prérequis

Pour exécuter ce projet, assurez-vous d'avoir :

- **Python 3.8 ou supérieur** installé.
- Les bibliothèques nécessaires (installables via pip si besoin).

---

## Installation et Exécution

1. **Clonez ce dépôt** :
   ```bash
   git clone https://github.com/votre-utilisateur/nom-du-repo.git
