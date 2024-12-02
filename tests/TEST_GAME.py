import pygame
import random
from TEST_Jeu_Units import Explorateur, Archeologue, Chasseur

# Dimensions
WIDTH, HEIGHT = 1300, 800
GRID_WIDTH = 800
UI_WIDTH = WIDTH - GRID_WIDTH
CELL_SIZE = GRID_WIDTH // 10


class Case:
    def __init__(self, type_case="normale"):
        self.type = type_case
        self.hidden = False  # Les cases commencent révélées

    def trigger_effect(self, unit):
        if self.type == "piège":
            if isinstance(unit, Chasseur):
                return f"{unit.name} détecte et désamorce un piège."
            else:
                unit.health -= 20
                return f"{unit.name} marche sur un piège et perd 20 PV."
        elif self.type == "ressource":
            unit.health += 10
            return f"{unit.name} récupère une ressource et gagne 10 PV."
        elif self.type == "indice":
            if isinstance(unit, Archeologue):
                self.type = "normale"
                return f"{unit.name} déchiffre un indice pour avancer."
            return f"{unit.name} ne peut pas déchiffrer cet indice."
        elif self.type == "ruines":
            return f"{unit.name} explore les ruines."
        return f"{unit.name} avance sur une case normale."


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.grid_size = 10
        self.cell_size = GRID_WIDTH // self.grid_size
        self.grid = self.initialize_grid()

        # Initialiser les équipes
        self.player_units = self.create_random_team("player")
        self.enemy_units = self.create_random_team("enemy")

        self.selected_unit_index = 0
        self.last_action_message = "Aucune action effectuée."

    def initialize_grid(self):
        grid = [[Case() for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        grid[2][2].type = "piège"
        grid[5][5].type = "indice"
        grid[7][7].type = "ressource"
        grid[1][8 % self.grid_size].type = "ruines"
        return grid

    def create_random_team(self, team):
        unit_classes = [Explorateur, Archeologue, Chasseur]
        return [
            random.choice(unit_classes)(
                random.randint(0, self.grid_size - 1),
                random.randint(0, self.grid_size - 1),
                team
            )
            for _ in range(3)
        ]

    def handle_player_turn(self):
        selected_unit = self.player_units[self.selected_unit_index]
        has_acted = False
        while not has_acted:
            self.flip_display()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    dx, dy = 0, 0
                    if event.key == pygame.K_LEFT:
                        dx = -1
                    elif event.key == pygame.K_RIGHT:
                        dx = 1
                    elif event.key == pygame.K_UP:
                        dy = -1
                    elif event.key == pygame.K_DOWN:
                        dy = 1
                    elif event.key == pygame.K_TAB:
                        self.selected_unit_index = (self.selected_unit_index + 1) % len(self.player_units)
                        selected_unit = self.player_units[self.selected_unit_index]
                        self.last_action_message = f"{selected_unit.name} est sélectionné."
                        break
                    if dx != 0 or dy != 0:
                        selected_unit.x = max(0, min(self.grid_size - 1, selected_unit.x + dx))
                        selected_unit.y = max(0, min(self.grid_size - 1, selected_unit.y + dy))
                        case = self.grid[selected_unit.y][selected_unit.x]
                        self.last_action_message = case.trigger_effect(selected_unit)
                        print(self.last_action_message)
                        has_acted = True

    def handle_enemy_turn(self):
        for enemy in self.enemy_units:
            target = random.choice(self.player_units)
            dx = 1 if enemy.x < target.x else -1 if enemy.x > target.x else 0
            dy = 1 if enemy.y < target.y else -1 if enemy.y > target.y else 0
            enemy.x = max(0, min(self.grid_size - 1, enemy.x + dx))
            enemy.y = max(0, min(self.grid_size - 1, enemy.y + dy))
            case = self.grid[enemy.y][enemy.x]
            self.last_action_message = case.trigger_effect(enemy)

    def draw_grid(self):
        for y, row in enumerate(self.grid):
            for x, case in enumerate(row):
                color = (200, 200, 200) if not case.hidden else (50, 50, 50)
                pygame.draw.rect(
                    self.screen,
                    color,
                    (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                )
                pygame.draw.rect(
                    self.screen,
                    (0, 0, 0),
                    (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size),
                    1
                )

    def draw_units(self):
        for unit in self.player_units + self.enemy_units:
            unit.draw(self.screen, self.cell_size)

    def draw_ui(self):
        pygame.draw.rect(self.screen, (50, 50, 50), (GRID_WIDTH, 0, UI_WIDTH, HEIGHT))

         # Fontes pour le texte
        font_small = pygame.font.Font(None, 24)
        font_medium = pygame.font.Font(None, 28)
        font_large = pygame.font.Font(None, 36)
        font_title = pygame.font.Font(None, 40)
         
        y_offset = 20  # Position de départ verticale pour les commandes
    
        #Section 1 : Touche de commandes :
        title_commands = font_title.render("Touches de commandes :", True, (255, 255, 255))
        self.screen.blit(title_commands, (GRID_WIDTH + 20, y_offset))
        y_offset += 50
    
        controls = [
            #Touches pour le deplacement et choix de l'unité :
            "Flèches : Déplacer l'unité",
            "TAB : Changer d'unité",
        
            # Touches pour les compétences Explorateur :
            
            "E : Révéler une zone (Explorateur)",
            "Q : Détection de pièges (Explorateur)",
            "R : Coup rapide (Explorateur)",
        
            # Touches pour les compétences Archeologue :
            
            "D : Décrypter un indice (Archéologue)",
            "A : Analyse de l'environnement (Archéologue)",
            "T : Attaque ciblée (Archéologue)",
        
            #Touches pour les compétences Chasseur :
            
            "P : Poser un piège (Chasseur)",
            "Y : Tir à distance (Chasseur)",
            "B : Brouillard de guerre (Chasseur)"
            ]
        for command in controls:
            line = font_small.render(command, True, (200, 200, 200))
            self.screen.blit(line, (GRID_WIDTH + 20, y_offset))
            y_offset += 25  # Espacement entre les commandes

        # Pour separer la section control et la section informations (Mieux visuellement)
        y_offset += 20
        pygame.draw.line(self.screen, (255, 255, 255), (GRID_WIDTH + 10, y_offset), (WIDTH - 10, y_offset), 2)
        y_offset += 20
    
        #Section 2 : Infos sur l'unité :
        title_unit_info = font_title.render("Informations sur l'unité :", True, (255, 255, 255))
        self.screen.blit(title_unit_info, (GRID_WIDTH + 20, y_offset))
        y_offset += 50 
        
        # Informations sur l'unité sélectionnée
        selected_unit = self.player_units[self.selected_unit_index]
        unit_info = [
            f"Unité : {selected_unit.name}",
            f"PV : {selected_unit.health}",
            f"Défense : {selected_unit.defense}",
            f"Position : ({selected_unit.x}, {selected_unit.y})"
            ]
        for info in unit_info:
            line = font_medium.render(info, True, (255, 255, 0))
            self.screen.blit(line, (GRID_WIDTH + 20, y_offset))
            y_offset += 35  # Espacement entre les infos

        # Pour separer la section Informations et Action realiser par une unité
        y_offset += 20
        pygame.draw.line(self.screen, (255, 255, 255), (GRID_WIDTH + 10, y_offset), (WIDTH - 10, y_offset), 2)
        y_offset += 20
    
        # Section 3 :  Action fait par l'unité :
        title_action = font_title.render("Dernière action :", True, (255, 255, 255))
        self.screen.blit(title_action, (GRID_WIDTH + 20, y_offset))
        
        y_offset += 50  # Espacement après le titre
        # Section 3 : Dernière action
        action_message = font_medium.render(f"Action : {self.last_action_message}", True, (255, 255, 255))
        self.screen.blit(action_message, (GRID_WIDTH + 20, y_offset))

    def flip_display(self):
        self.screen.fill((0, 0, 0))
        self.draw_grid()
        self.draw_units()
        self.draw_ui()
        pygame.display.flip()