# Les Mystérieuses Cités d'Or - Exploration et Stratégie sur Grille 
![Map_jeu]([main/images/map_maya.png](https://raw.githubusercontent.com/Oliver-prog-python/Projet-POO-Jeu-de-Ruines/main/main/images/map_maya.png))

## Description

Les **Mystérieuses Cités d'Or** est un jeu stratégique en Python où des unités explorent une grille remplie d'énigmes, de trésors, de pièges et plein d'autres.  Chaque unité possède des compétences uniques influençant la stratégie du joueur pour atteindre l'objectif final: **récuperer le trésor**. Ce projet met en avant l'utilisation de la **programmation orientée objet (POO)**.

## Fonctionnalités
- **Exploration de la grille** : Explorer les ruines et évitez les pièges et l'équipe ennemie.
- **Unités spécialisées** :
   - **Explorateur**  <img src="main/images/explorateur.png" alt="Explorateur" width="50"> : Détecte les pièges et explore des zones cachées.
   - **Archéologue** <img src="main/images/archeologue.png" alt="Archeologue" width="50">: Résout des énigmes pour progresser.
   - **Chasseur** <img src="images/chasseur_2.png" alt="Chasseur" width="50">: Pose des pièges et utilise le brouillard pour reculer ses ennemis.
- **Système de compétences** : Chaque unité utilise des actions spécifiques pour interagir avec la grille, voici quelques unes :
   - `reveler_zone()` : Révélation des cases voisines.
   - `poser_piege()` : Placement de pièges sur la grille.
   - `decrypter_indice()` : Decrypter des énigmes.
- **Effets des cases** :
   - **Pièges** : Infligent des dégâts aux unités. <img src="main/images/case_piege2.png" alt="Piege" width="50">
   - **Trésor** : Objectif final pour gagner la partie.  <img src="main/images/case_tresor2.png" alt="Trésor" width="50">
   - **Indices** : Déclenchent des énigmes à résoudre.   <img src="main/images/case_indice2.png" alt="Indices " width="50">
   - **Ressources**: Récuperer des points de vie.  <img src="main/images/case_ressource2.png" alt="Ressources" width="50">
   - **Clé magique** : Récuperer la clé magique afin d'ouvrir une des portes qui mène au trésor.  <img src="main/images/case_clef.png" alt="clé magique" width="50">
   - **Portes**: Protègent le trésor, une seule s'ouvre.  <img src="main/images/case_porte.png" alt="Porte" width="50">
   - **Ruines** : Sans effet. <img src="main/images/case_ruine2.png" alt="Ruine" width="50">

## Comprendre les fonctionnalitées
Afin de comprendre les fonctionnalités du jeu, la touche "C" permet de dérouler le menu. NB: certaines compétences relèvent des cases (ex: seul archéologue peut tenter de résoudre énigme et ne pas perdre de points si il s'y trouve, les autres unités perdent sytématiquement des PV ou encore quand l'explorateur active la touche "E" il marque en rouge sur la map les pièges aux alentours).  

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
   git clone https://github.com/<votre-nom-d'utilisateur>/<Projet-POO-Jeu-de-Ruines>.git

