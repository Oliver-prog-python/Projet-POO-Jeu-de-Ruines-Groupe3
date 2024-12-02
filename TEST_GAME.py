import pygame
import random
from TEST_Jeu_Units import Explorateur, Archeologue, Chasseur

# Dimensions de la grille
CELL_SIZE = 60
GRID_SIZE = 10
WIDTH = CELL_SIZE * GRID_SIZE
HEIGHT = CELL_SIZE * GRID_SIZE


class Case:
    """
    Classe pour représenter une case sur la grille.
    """
    def __init__(self, type_case="normale"):
        self.type = type_case
        self.hidden = False  # Les cases commencent masquées

    def trigger_effect(self, unit):
        """Déclenche l'effet de la case en fonction de son type."""
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
    """
    Classe principale pour gérer le jeu.
    """
    def __init__(self, screen, grid_size, cell_size):
        """
        Initialise le jeu.
        """
        self.screen = screen
        self.grid_size = grid_size  # Utilisé pour les dimensions de la grille
        self.cell_size = cell_size  # Taille de chaque cellule en pixels
        self.grid = self.initialize_grid()

        # Créer des équipes aléatoires pour le joueur humain et l'IA
        self.player_units = self.create_random_team("player")
        self.enemy_units = self.create_random_team("enemy")

        # Autres attributs
        self.selected_unit_index = 0  # Indice de l'unité sélectionnée dans l'équipe humaine
        self.last_action_message = "Aucune action effectuée."  # Dernière action à afficher

    def initialize_grid(self):
        """Crée une grille avec des cases de différents types."""
        grid = [[Case() for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        grid[2][2].type = "piège"
        grid[5][5].type = "indice"
        grid[7][7].type = "ressource"
        grid[1][8 % self.grid_size].type = "ruines"  # S'assurer que l'index reste valide
        return grid

    def create_random_team(self, team):
        """
        Crée une équipe de 3 unités sélectionnées aléatoirement.

        :param team: str - Équipe ('player' ou 'enemy').
        :return: list - Liste des unités de l'équipe.
        """
        unit_classes = [Explorateur, Archeologue, Chasseur]
        return [random.choice(unit_classes)(random.randint(0, self.grid_size - 1),
                                            random.randint(0, self.grid_size - 1),
                                            team) for _ in range(3)]

    def handle_player_turn(self):
        """Gère le tour du joueur humain."""
        selected_unit = self.player_units[self.selected_unit_index]
        has_acted = False

        while not has_acted:
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
                        # Passer à l'unité suivante
                        self.selected_unit_index = (self.selected_unit_index + 1) % len(self.player_units)
                        selected_unit = self.player_units[self.selected_unit_index]
                        self.last_action_message = f"{selected_unit.name} est sélectionné."
                        break

                    # Déplacement
                    if dx != 0 or dy != 0:
                        selected_unit.x = max(0, min(self.grid_size - 1, selected_unit.x + dx))
                        selected_unit.y = max(0, min(self.grid_size - 1, selected_unit.y + dy))
                        case = self.grid[selected_unit.y][selected_unit.x]
                        self.last_action_message = case.trigger_effect(selected_unit)
                        has_acted = True

    def handle_enemy_turn(self):
        """Gère le tour de l'IA."""
        for enemy in self.enemy_units:
            target = random.choice(self.player_units)
            dx = 1 if enemy.x < target.x else -1 if enemy.x > target.x else 0
            dy = 1 if enemy.y < target.y else -1 if enemy.y > target.y else 0
            enemy.x = max(0, min(self.grid_size - 1, enemy.x + dx))
            enemy.y = max(0, min(self.grid_size - 1, enemy.y + dy))

            case = self.grid[enemy.y][enemy.x]
            self.last_action_message = case.trigger_effect(enemy)

            # Attaque si à portée
            if abs(enemy.x - target.x) <= 1 and abs(enemy.y - target.y) <= 1:
                enemy.ranged_attack(target)

    def draw_grid(self):
        """Dessine la grille."""
        for y, row in enumerate(self.grid):
            for x, case in enumerate(row):
                color = (200, 200, 200) if not case.hidden else (50, 50, 50)
                pygame.draw.rect(self.screen, color, (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size))
                pygame.draw.rect(self.screen, (0, 0, 0), (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size), 1)

    def draw_units(self):
        """Dessine les unités."""
        for unit in self.player_units + self.enemy_units:
            unit.draw(self.screen, self.cell_size)

    def flip_display(self):
        print("Flip Display Start")
        self.screen.fill((0, 0, 0))
        print("Screen filled")
        self.draw_grid()
        print("Grid drawn")
        self.draw_units()
        print("Units drawn")
        pygame.display.flip()
        print("Display flipped")