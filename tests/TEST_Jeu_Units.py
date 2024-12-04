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

#================================================
# Définition de la classe pour les personnages :
#================================================

class Unit:
    """Classe de base pour toutes les unités."""
    def __init__(self, x, y, image_path, name,team):
        self.x = x
        self.y = y
        self.image = pygame.image.load(image_path)  # Charger l'image
        self.image = pygame.transform.scale(self.image, (85, 85))  # Redimensionner si nécessaire
        self.name = name
        self.health = 100
        self.defense = 10
        self.team=team

    def draw(self, screen, cell_size):
        """Dessine l'unité sur l'écran."""
        screen.blit(self.image, (self.x * cell_size, self.y * cell_size))
      


#=====================================  
# Compétence de L'Explorateur :
#=====================================  
    
class Explorateur(Unit):
    def __init__(self, x, y,team):
        super().__init__(x, y,"images/aventurier.png" , team,"Explorateur")
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
    def __init__(self, x, y,team):
        super().__init__(x, y, "images/archeologue.png",team, "Archéologue")
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
    def __init__(self, x, y,team):
        super().__init__(x, y, "images/chasseur.png", team,"Chasseur")
        self.speed = 3

    def poser_piege(self, grid, x, y):
        """Pose un piège sur une case spécifique."""
        if grid[x][y].type == "normale":
            grid[x][y].type = "piège"
            return "Piège posé avec succès !"
        return "Impossible de poser un piège ici."
    
    
    
    
    
    
    
    
    
