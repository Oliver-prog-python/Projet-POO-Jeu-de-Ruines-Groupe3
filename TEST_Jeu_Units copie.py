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
    

#=====================================
#   Compétence de l'Archeologue :
#=====================================   

class Archeologue(Unit):
    def __init__(self, x, y):
        super().__init__(x, y, (255, 0, 0), "Archéologue")
        self.speed = 2

    def decrypter_indice(self, case):
        """Décrypte un indice sur une case."""
        if case.type == "indice":
            case.type = "normale"  # L'indice est résolu
            return "Indice décrypté !"
        return "Aucun indice à décrypter ici."


#=====================================
#   Compétence du Chasseur :
#=====================================   

class Chasseur(Unit):
    def __init__(self, x, y):
        super().__init__(x, y, (0, 255, 0), "Chasseur")
        self.speed = 3

    def poser_piege(self, grid, x, y):
        """Pose un piège sur une case spécifique."""
        if grid[x][y].type == "normale":
            grid[x][y].type = "piège"
            return "Piège posé avec succès !"
        return "Impossible de poser un piège ici."
    
    
    
    
    
    
    
    