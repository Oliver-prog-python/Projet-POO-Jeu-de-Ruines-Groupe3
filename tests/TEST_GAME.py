import pygame
import random
from TEST_Jeu_Units2 import Explorateur, Archeologue, Chasseur

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

         self.action_done = False  # Reset l'action pour le joueur
         selected_unit = self.player_units[self.selected_unit_index]

         while not self.action_done:
             self.flip_display()
             for event in pygame.event.get():
                 if event.type == pygame.QUIT:
                     pygame.quit()
                     exit()

                 if event.type == pygame.KEYDOWN:
                     dx, dy = 0, 0
                     if event.key == pygame.K_c:  
                         self.show_commands = not self.show_commands
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
                     elif event.key == pygame.K_RETURN:  # Touche pour confirmer la fin du tour
                         self.last_action_message = f"{selected_unit.name} a terminé son tour."
                         self.action_done = True
                         break

                     # Si un déplacement est effectué
                     if dx != 0 or dy != 0:
                         selected_unit.x = max(0, min(self.grid_size - 1, selected_unit.x + dx))
                         selected_unit.y = max(0, min(self.grid_size - 1, selected_unit.y + dy))
                         case = self.grid[selected_unit.y][selected_unit.x]
                         self.last_action_message = case.trigger_effect(selected_unit)
                         self.action_done = True  # Fin de l'action après un déplacement


    # Definition qui permet de gérer le tour de l'IA
    def handle_enemy_turn(self):
    
        self.last_action_message = "C'est le tour de l'IA."
        self.flip_display()  # Met à jour l'affichage pour indiquer que c'est le tour de l'IA
        pygame.time.delay(1000)  # Pause pour indiquer visuellement le tour de l'IA

        # Choisir une unité de l'IA pour effectuer une action
        enemy_unit = random.choice(self.enemy_units)  # Choisir une unité aléatoire
        target_unit = random.choice(self.player_units)  # Choisir une cible aléatoire du joueur

        # Déplacer l'unité ennemie vers la cible
        dx = 1 if enemy_unit.x < target_unit.x else -1 if enemy_unit.x > target_unit.x else 0
        dy = 1 if enemy_unit.y < target_unit.y else -1 if enemy_unit.y > target_unit.y else 0

        # Effectuer le déplacement
        enemy_unit.x = max(0, min(self.grid_size - 1, enemy_unit.x + dx))
        enemy_unit.y = max(0, min(self.grid_size - 1, enemy_unit.y + dy))

        # Vérifier les effets de la case sur laquelle l'ennemi arrive
        case = self.grid[enemy_unit.y][enemy_unit.x]
        self.last_action_message = case.trigger_effect(enemy_unit)

        self.flip_display()  # Rafraîchir l'affichage avec la dernière action de l'IA
        pygame.time.delay(1000)  # Pause pour montrer l'action de l'IA

    
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
        title_action = font_title.render("Dernière action :", True, (255, 255, 255))
        self.screen.blit(title_action, (GRID_WIDTH + 20, y_offset))

        y_offset += 50  # Espacement après le titre
        action_message = font_medium.render(f"Action : {self.last_action_message}", True, (255, 255, 255))
        self.screen.blit(action_message, (GRID_WIDTH + 20, y_offset))

    def flip_display(self):
        self.screen.fill((0, 0, 0))
        self.draw_grid()
        self.draw_units()
        self.draw_ui()
        pygame.display.flip()
