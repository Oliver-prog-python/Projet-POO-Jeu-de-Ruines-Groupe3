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
    
    def trigger_effect(self, unit, is_human=True):
        if self.type == "trésor":
            return f"{unit.name} a trouvé le trésor ! Victoire !"
        if self.type == "piège":
            if isinstance(unit, Chasseur):
                return f"{unit.name} détecte et désamorce un piège."
            else: # cas où ce n'est pas un chasseur
                unit.health -= 20
                return f"{unit.name} marche sur un piège et perd 20 PV."

        elif self.type == "ressource":
            unit.health += 10
            return f"{unit.name} récupère une ressource et gagne 10 PV."

        elif self.type == "indice":
            if isinstance(unit,Archeologue):
                if is_human:
                    # Défi pour le joueur humain controlant un archéologue
                    x, y = random.randint(1, 10), random.randint(1, 10)
                    correct_answer = x + y
                    print(f"Défi : Quel est le résultat de {x} + {y} ?")
                    try:
                        player_answer = int(input("Votre réponse : "))
                        if player_answer == correct_answer:
                            self.type = "normale"
                            return f"{unit.name} a résolu l'indice avec succès."
                        else:
                            unit.health -= 10
                            return f"{unit.name} a échoué à résoudre l'indice et perd 10 PV."
                    except ValueError:
                        unit.health -= 10
                        return f"{unit.name} n'a pas répondu correctement et perd 10 PV."
                else:
                # L'IA contrôlant un archéologue échoue automatiquement
                    unit.health-=10
                    return f"{unit.name} (IA) n'a pas déchiffré l'indice avec succès."
            else:
            # Unité non archéologue : perd toujours 10 PV
                unit.health -= 10
                return f"{unit.name} ne peut pas déchiffrer l'indice et perd 10 PV."
        elif self.type == "ruines":
            if isinstance(unit, Explorateur):
                return f"{unit.name} explore efficacement les ruines."
        else:
            return f"{unit.name} explore les ruines sans compétences particulières."
        return f"{unit.name} avance sur une case normale."
      
class Game:
    def __init__(self, screen):
        self.screen = screen
        self.grid_size = 10
        self.cell_size = GRID_WIDTH // self.grid_size
        self.grid = self.initialize_grid()

         # Charger les images des cases
        self.tile_images = {
            "normale": pygame.image.load("images/case_ruine2.png"),
            "piège": pygame.image.load("images/case_piege2.png"),
            "ressource": pygame.image.load("images/case_ressource2.png"),
            "indice": pygame.image.load("images/case_indice2.png"),
        }
         

        for key in self.tile_images:
            self.tile_images[key] = pygame.transform.scale(self.tile_images[key], (self.cell_size, self.cell_size))

        # Ajouter l'image du trésor
        self.tile_images["trésor"] = pygame.image.load("images/case_tresor2.png")
        self.tile_images["trésor"] = pygame.transform.scale(self.tile_images["trésor"], (self.cell_size, self.cell_size))
        
        # Placer le trésor
        self.place_tresor()

        # Initialiser les équipes
        self.player_units = self.create_random_team("player")
        self.enemy_units = self.create_random_team("enemy")

        self.selected_unit_index = 0
        self.last_action_message = "Aucune action effectuée."

    def initialize_grid(self):
        """
        Crée une grille avec des cases de différents types en fonction de proportions prédéfinies.
        """
        grid = [[Case() for _ in range(self.grid_size)] for _ in range(self.grid_size)]
    
    # Définir les proportions
        nombre_pieges = int(self.grid_size * self.grid_size * 0.2)  # 20% de pièges
        nombre_ressources = int(self.grid_size * self.grid_size * 0.2)  # 10% de ressources
        nombre_indices= int(self.grid_size * self.grid_size * 0.1)  # 10% d'indices

    # Placer des pièges
        for _ in range(nombre_pieges):
            x, y = random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1)
            grid[y][x].type = "piège"

    # Placer des ressources
        for _ in range(nombre_ressources):
            x, y = random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1)
            grid[y][x].type = "ressource"

    # Placer des indices
        for _ in range(nombre_indices):
            x, y = random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1)
            grid[y][x].type = "indice"

        return grid
    
    def place_tresor(self):
        """Place un trésor sur une case aléatoire de la grille."""
        while True:
            x, y = random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1)
            if self.grid[y][x].type == "normale":  # Assurez-vous que la case est normale
                self.grid[y][x].type = "trésor"
                print(f"Le trésor a été placé sur la case ({x}, {y})")
                break
    
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

        # Initialiser dx et dy pour éviter des erreurs
        dx, dy = 0, 0  # Par défaut, aucune direction
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
                    # Passer à l'unité suivante
                    self.selected_unit_index = (self.selected_unit_index + 1) % len(self.player_units)
                    selected_unit = self.player_units[self.selected_unit_index]
                    self.last_action_message = f"{selected_unit.name} est sélectionné."
                    break
                if dx != 0 or dy != 0:
                    # Mise à jour de la position
                    selected_unit.x = max(0, min(self.grid_size - 1, selected_unit.x + dx))
                    selected_unit.y = max(0, min(self.grid_size - 1, selected_unit.y + dy))
                    
                    # Appliquer l'effet de la case
                    case = self.grid[selected_unit.y][selected_unit.x]
                    self.last_action_message = case.trigger_effect(selected_unit, is_human=True)
                    print(self.last_action_message)
                    has_acted = True


    def handle_enemy_turn(self):
        for enemy in self.enemy_units:
            target = random.choice(self.player_units)
            dx = 1 if enemy.x < target.x else -1 if enemy.x > target.x else 0
            dy = 1 if enemy.y < target.y else -1 if enemy.y > target.y else 0

        # Mise à jour de la position
        enemy.x = max(0, min(self.grid_size - 1, enemy.x + dx))
        enemy.y = max(0, min(self.grid_size - 1, enemy.y + dy))

        # Appliquer l'effet de la case
        case = self.grid[enemy.y][enemy.x]
        self.last_action_message = case.trigger_effect(enemy, is_human=False)
        print(self.last_action_message)

    
    def draw_grid(self):
        """
        Dessine la grille avec toutes les cases affichées en fonction de leur type.
        """
        for y, row in enumerate(self.grid):
            for x, case in enumerate(row):
                # Utiliser l'image correspondant au type de la case
                image = self.tile_images.get(case.type, self.tile_images["normale"])
                self.screen.blit(image, (x * self.cell_size, y * self.cell_size))

                # Dessiner les bordures des cases
                pygame.draw.rect(
                    self.screen,
                    (0, 0, 0),
                    (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size),
                    1,
                )

    def draw_units(self):
        for unit in self.player_units + self.enemy_units:
            unit.draw(self.screen, self.cell_size)

    
    def draw_ui(self):
    # Dessiner la zone UI
        pygame.draw.rect(self.screen, (50, 50, 50), (GRID_WIDTH, 0, UI_WIDTH, HEIGHT))

    # Initialiser une police d'écriture
        font = pygame.font.Font(None, 36)

    # Afficher les commandes
        commands = [
            "Commandes :",
            "Flèches : Déplacer l'unité",
            "TAB : Changer d'unité",
            "E : Révéler une zone (Explorateur)",
            "D : Décrypter un indice (Archéologue)",
            "P : Poser un piège (Chasseur)"
    ]
        for i, cmd in enumerate(commands):
            line = font.render(cmd, True, (255, 255, 255))
            self.screen.blit(line, (GRID_WIDTH + 20, 20 + i * 30))

    # Afficher l'action du joueur
        player_action = font.render(f"Action Joueur : {self.last_action_message}", True, (0, 255, 0))
        self.screen.blit(player_action, (GRID_WIDTH + 20, 200))

    # Afficher l'action de l'IA (en rouge)
        ia_action = font.render(f"Action IA : {self.last_action_message}", True, (255, 0, 0))
        self.screen.blit(ia_action, (GRID_WIDTH + 20, 240))

    # Informations sur l'unité sélectionnée
        selected_unit = self.player_units[self.selected_unit_index]
        unit_info = [
            f"Unité : {selected_unit.name}",
            f"PV : {selected_unit.health}",
            f"Position : ({selected_unit.x}, {selected_unit.y})"
    ]
        for i, info in enumerate(unit_info):
            line = font.render(info, True, (200, 200, 200))
            self.screen.blit(line, (GRID_WIDTH + 20, 300 + i * 30))

    def flip_display(self):
        self.screen.fill((0, 0, 0))
        self.draw_grid()
        self.draw_units()
        self.draw_ui()
        pygame.display.flip()

                    
            
               
                    
                   
            
                
                

    
            
            
       
    
       
        
