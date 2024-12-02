#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 17:31:07 2024

@author: olivermaamary
"""
import pygame

#================================================
# Paramétres / constantes :
#================================================
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

#================================================
# Définition de la classe pour les personnages :
#================================================

class Unit:
    """Classe de base pour toutes les unités."""
    def __init__(self, x, y, color, name):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        self.health = 100
        self.defense = 10

    def draw(self, screen, cell_size):
        """Dessine l'unité sur l'écran."""
        pygame.draw.rect(
        screen,
        self.color,  # Couleur de l'unité
        (
            self.x * cell_size,  # Position x
            self.y * cell_size,  # Position y
            cell_size,  # Largeur
            cell_size   # Hauteur
        )
    )


#=====================================  
# Compétence de L'Explorateur :
#=====================================  
    
class Explorateur(Unit):
    def __init__(self, x, y):
        super().__init__(x, y, BLUE, "Explorateur")
        self.speed = 5
    
    #compétence 1 :
    def revele_zone(self, grid):
        """Révèle une zone 3x3 autour de l'Explorateur."""
        revealed = []
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                nx, ny = self.x + dx, self.y + dy
                if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
                    grid[nx][ny].hidden = False  # Révéler la case
                    revealed.append((nx, ny))
        return revealed
    
    #Compétence 2 : Détection de pièges :
    def detecte_piege(self, grid):
        """Retourne un message indiquant s'il y a des pièges autour."""
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                nx, ny = self.x + dx, self.y + dy
                if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and grid[nx][ny].type == "piège":
                    return "Piège détecté à proximité !"
        return "Aucun piège détecté."
    
    #Compétence 3: Coup rapide dégats:
    def coup_rapide(self, cible):
        """Inflige 15 dégâts à une cible si elle est valide."""
        if cible:
            cible.health -= 15
            return f"{cible.name} a subi 15 dégâts !"
        return "Pas de cible valide."
    
#=====================================
#   Compétence de l'Archeologue :
#=====================================   

class Archeologue(Unit):
    def __init__(self, x, y):
        super().__init__(x, y, (255, 0, 0), "Archéologue")
        self.speed = 2

    #Compétence 1 : Decrypter l'indice :
    def decrypter_indice(self, case):
        """Décrypte un indice sur une case."""
        if case.type == "indice":
            case.type = "normale"  # L'indice est résolu
            return "Indice décrypté !"
        return "Aucun indice à décrypter ici."
   
    #Compétence 2 : Analyse de l'environnement :
    def analyse_environnement(self, grid):
        """Analyse les cases spéciales autour (3x3) et retourne un message."""
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                nx, ny = self.x + dx, self.y + dy
                if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and grid[nx][ny].type in ["indice", "ressource"]:
                    return "Case spéciale détectée à proximité."
        return "Aucune case spéciale détectée."
    
    #Compétence 3 : Attaque ciblé :
    def attaque_ciblee(self, cible):
        """Inflige 20 dégâts, en ignorant une partie de la défense."""
        if cible:
            degats = max(0, 20 - (cible.defense // 2))  # Pour éviter des dégâts négatifs
            cible.health -= degats
            return f"{cible.name} a subi {degats} dégâts !"
        return "Pas de cible valide."
#=====================================
#   Compétence du Chasseur :
#=====================================   

class Chasseur(Unit):
    def __init__(self, x, y):
        super().__init__(x, y, (0, 255, 0), "Chasseur")
        self.speed = 3
    
    #Compétence 1 : Pose de piège :
    def poser_piege(self, grid, x, y):
        """Pose un piège sur une case spécifique."""
        if grid[x][y].type == "normale":
            grid[x][y].type = "piège"
            return "Piège posé avec succès !"
        return "Impossible de poser un piège ici."
    
    #Compétence 2 : Tir à distance :
    def tir_distance(self, cible):
        """Inflige 25 dégâts à une cible si elle est valide."""
        if cible:
            cible.health -= 25
            return f"{cible.name} a subi 25 dégâts à distance !"
        return "Pas de cible valide."
    
    #Compétence 3 : Brouillard de guerre :
    def brouillard_de_guerre(self, enemy_units, grid):
        """Crée un brouillard de guerre et force les unités ennemies à retourner à leur position de départ."""
        for enemy in enemy_units:
            enemy.x, enemy.y = 0, 0  
        return "Brouillard de guerre activé !"
    
    
    
    
    
    
    