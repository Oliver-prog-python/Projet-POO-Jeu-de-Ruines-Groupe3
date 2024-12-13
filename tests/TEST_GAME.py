import pygame
import random
from TEST_Jeu_Units import Explorateur, Archeologue, Chasseur

pygame.init()


# Dimensions de l'écran
SCREEN_WIDTH = 1300  # Largeur fixe
SCREEN_HEIGHT = 750  # Hauteur fixe

# Taille des cases
CELL_SIZE = 60  # Taille de chaque case

# Calcul dynamique des dimensions de la grille
GRID_COLUMNS = SCREEN_WIDTH // CELL_SIZE  # Nombre de colonnes
GRID_ROWS = SCREEN_HEIGHT // CELL_SIZE    # Nombre de lignes

# Calcul des marges pour centrer la grille
MARGIN_X = (SCREEN_WIDTH - (GRID_COLUMNS * CELL_SIZE)) // 2
MARGIN_Y = (SCREEN_HEIGHT - (GRID_ROWS * CELL_SIZE)) // 2



#=================================================================================================================================================#
#              Definition peremetant de faire une retourne de liste des positions accessibles en fonction de la portée de l'unité                 #
#=================================================================================================================================================# 

def get_accessible_positions(unit, GRID_COLUMNS, GRID_ROWS, game=None):
    x, y = unit.x, unit.y

    max_range = getattr(unit, "max_range", 1)
    accessible_positions = []

    for dx in range(-max_range, max_range + 1):
        for dy in range(-max_range, max_range + 1):
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_COLUMNS and 0 <= ny < GRID_ROWS and abs(dx) + abs(dy) <= max_range:
                if game:
                    case = game.grid[ny][nx]
                    # Bloquer les portes pour les unités sans clé
                    if case.type == "porte" and not unit.has_key:
                        continue
                    # Bloquer le trésor si la porte correcte n'est pas encore ouverte
                    if case.type == "trésor":
                        porte_x, porte_y = game.porte_correcte
                        if game.grid[porte_y][porte_x].type == "porte":
                            continue
                accessible_positions.append((nx, ny))

    return accessible_positions


#==============================================#
#              Class des Cases                 #
#==============================================# 

class Case:
    def __init__(self, type_case="normale"):
        self.type = type_case
        self.hidden = False  # Les cases commencent révélées

    def effet_case(self, unit, game, is_human=True):
        if self.type == "trésor":
            game.treasure_animation(unit.x, unit.y)  # Lancer l'animation
            game.add_message(f"{unit.name} a trouvé le trésor ! Victoire !")
            return f"{unit.name} a trouvé le trésor ! Victoire !"

        if self.type == "piège":
            if isinstance(unit, Chasseur):
                game.add_message(f"{unit.name} détecte et désamorce un piège.")
                return f"{unit.name} détecte et désamorce un piège."
            else:
                game.explosion_animation(unit.x, unit.y)
                unit.health -= 20
                unit.health = max(0, unit.health)
                game.add_message(f"{unit.name} marche sur un piège et perd 20 PV.")
                if unit.health == 0:
                    unit.mourir(game)
                    return f"{unit.name} est éliminé après avoir marché sur un piège."
                return f"{unit.name} marche sur un piège et perd 20 PV."

        elif self.type == "ressource":
            unit.health = min(100, unit.health + 10)
            game.add_message(f"{unit.name} récupère une ressource et gagne 10 PV.")
            return f"{unit.name} récupère une ressource et gagne 10 PV."

        elif self.type == "indice":
            if isinstance(unit, Archeologue):
                if not game.current_riddle:
                    choix_enigme = game.genere_enigme()
                    game.current_riddle = {
                        "question": choix_enigme["question"],
                        "answer": str(choix_enigme["réponse"]).strip(),
                        "unit": unit,
                        "case": self,
                    }
                return f"{unit.name} doit résoudre une énigme."
            else:
                unit.health -= 10
                unit.health = max(0, unit.health)
                if unit.health == 0:
                    unit.mourir(game)
                    return f"{unit.name} est éliminé sur une case indice."
                return f"{unit.name} ne peut pas résoudre l'indice et perd 10 PV."
        
        elif self.type == "clé":
            if unit.has_key:
                game.add_message(f"{unit.name} possède déjà une clé.")
                return f"{unit.name} possède déjà une clé."
            else:
                unit.has_key = True  # L'unité récupère la clé
                self.type = "normale"  # La case redevient normale
                game.add_message(f"{unit.name} a récupéré une clé magique !")
                return f"{unit.name} a récupéré une clé magique !"
        
        elif self.type == "porte":
            if unit.has_key:
                # Vérifiez si c'est la porte correcte
                for y, row in enumerate(game.grid):
                    for x, case in enumerate(row):
                        if case is self:
                            if (x, y) == game.porte_correcte:  # Si c'est la porte correcte
                                self.type = "normale"  # Ouvrir la porte
                                unit.has_key = False  # Consommer la clé
                                game.add_message(f"{unit.name} a ouvert la porte correcte !")
                                
                                # Débloquer l'accès au trésor en le marquant comme "normale"
                                if game.tresor_position == (x, y + 1):  # Ajuster selon la position
                                    game.grid[y + 1][x].type = "trésor"
                                
                                return f"{unit.name} a ouvert la porte correcte !"
                            else:  # Si ce n'est pas la porte correcte
                                # Empêcher le déplacement
                                unit.x, unit.y = unit.x, unit.y  # Reste sur sa position actuelle
                                unit.health -= 10  # Inflige 10 points de dégâts
                                unit.health = max(0, unit.health)  # Santé ne peut pas être négative
                                if unit.health == 0:  # Vérification si l'unité meurt
                                    unit.mourir(game)
                                game.add_message(f"{unit.name} essaie d'ouvrir une porte incorrecte et perd 10 PV.")
                        
                                # Afficher l'animation de verrouillage
                                game.draw_door_locked_effect(unit.x, unit.y)
                                return f"{unit.name} essaie d'ouvrir une porte incorrecte et perd 10 PV."
            else:
                # Pas de clé, empêcher tout mouvement
                game.add_message(f"{unit.name} a besoin d'une clé pour ouvrir cette porte.")
                return f"{unit.name} a besoin d'une clé pour ouvrir cette porte."
        
        
        elif self.type == "ruines":
            if isinstance(unit, Explorateur):
                game.add_message(f"{unit.name} explore efficacement les ruines.")
                return f"{unit.name} explore efficacement les ruines."

        else:
            game.add_message(f"{unit.name} avance sur une case normale.")
            return f"{unit.name} avance sur une case normale."


class Game:
    def __init__(self, screen):
        
        self.screen = screen
        self.running = True
        
        # Initialiser la grille avant d'appeler les autres méthodes
        self.grid = self.initialize_grid()
        
        self.place_tresor()
        self.place_portes()
        self.place_clef()
        self.choix_enigme = None
        
        
        # Ajouter cette ligne pour suivre la position sélectionnée
        self.selected_position = None  # Position sélectionnée (initialement None)
        
        self.console_messages = []  # Liste des messages pour le popup console
        self.font = pygame.font.Font(None, 24)  # Police pour le texte de la console
        self.show_console_popup = True  # Le popup console est visible par défaut
        self.show_commands = False  # pour masquer le popup par defaut 
        
        # Popup pour afficher le tour de l'équipe a jouer :
        self.turn_popup_message = None  # Message à afficher pour le changement de tour
        self.turn_popup_start_time = None  # Temps où le popup a commencé à être affiché
        
        # Initialiser les équipes
        self.player_units = self.create_random_team("player")
        self.enemy_units = self.create_random_team("enemy")
        self.initialize_teams()
        
        self.selected_unit_index = 0
        self.last_action_message = "Aucune action effectuée."
        self.action_done = False  # Cette ligne permet de verifier si une action à ete realiser par le jouer / IA
        
        # Initialisation pour les énigmes
        self.current_riddle = None  # L'énigme en cours (aucune par défaut)
        self.player_input = ""      # Stockage de l'entrée utilisateur
        
        # Pour afficher l'icon de la clé a coter du healthbar lorsque recuperer 
        self.key_icon = pygame.image.load("images/case_clef.png")  # Chargez l'icône de la clé
        self.key_icon = pygame.transform.scale(self.key_icon, (20, 20))  # Redimensionnez à 20x20 pixels
 
        # Charger et redimensionner les images des cases
        self.tile_images = {
            "normale": pygame.image.load("images/case_ruine2.png"),
            "piège": pygame.image.load("images/case_piege2.png"),
            "ressource": pygame.image.load("images/case_ressource2.png"),
            "indice": pygame.image.load("images/case_indice2.png"),
            "trésor": pygame.image.load("images/case_tresor2.png"),
            "porte": pygame.image.load("images/case_porte.png"),
            "clé": pygame.image.load("images/case_clef.png"),
        }

        # Redimensionner toutes les images pour correspondre à CELL_SIZE
        for key in self.tile_images:
            self.tile_images[key] = pygame.transform.scale(self.tile_images[key], (CELL_SIZE, CELL_SIZE))
        
        
        

        self.debut_player=1 #commencer avec le joueur 1
        self.selected_unit_index = 0
        self.last_action_message = "Aucune action effectuée."
        
    def add_message(self, message):
        """Ajoute un message unique à la console."""
        self.console_messages = [message]  # Remplace le contenu de la liste par un seul message
    
    
    #==========================================================================================================#
    #              Definition genre enigme qui permet de generer 3 types differents d'enigmes                  #
    #==========================================================================================================# 
    
    def genere_enigme(self):  # Génère une énigme
        enigmes = [
            # Carré magique
            {
                "question": "Carré magique :\n2 7 6\n9 _ 1\n4 3 8\nQuel est le chiffre manquant ?",
                "réponse": 5
            },
            # Séquence numérique
            {
                "question": "Suite : 1, 1, 2, 3, 5, ?\nQuel est le prochain nombre ?",
                "réponse": 8
            },
            # Séquence alphabétique
            {
                "question": "Suite : A, C, E, G, ?\nQuelle est la prochaine lettre ?",
                "réponse": "I"
            }
        ]
        self.choix_enigme = random.choice(enigmes)
        return self.choix_enigme
    
    def handle_events(self):
        """Gère les événements pour le jeu."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:  # Toggle pour afficher/masquer la console
                    self.show_console = not self.show_console
                elif event.key == pygame.K_SPACE:  # Exemple d'ajout de message
                    self.add_message("Appui sur ESPACE - Énigme déclenchée!")
                elif event.key == pygame.K_RETURN:  # Exemple de réponse
                    self.add_message("Réponse validée!")
    
    
    #=====================================================================================================================================#
    #               Définition qui crée une grille en utilisant différents types de case en fonction des proportions prédéfinies          #
    #=====================================================================================================================================#
    
    def initialize_grid(self):
        # Créer une grille vide basée sur GRID_COLUMNS et GRID_ROWS
        grid = [[Case() for _ in range(GRID_COLUMNS)] for _ in range(GRID_ROWS)]
        
        # Définir les proportions
        total_cells = GRID_COLUMNS * GRID_ROWS
        nombre_pieges = int(total_cells * 0.1)  # 10% de pièges
        nombre_ressources = int(total_cells * 0.2)  # 20% de ressources
        nombre_indices = int(total_cells * 0.1)  # 10% d'indices

        # Fonction pour placer les types
        def place_type(type_name, count):
            for _ in range(count):
                while True:
                    x = random.randint(0, GRID_COLUMNS - 1)
                    y = random.randint(0, GRID_ROWS - 1)
                    if grid[y][x].type == "normale":  # Assurez-vous que la case est normale
                        grid[y][x].type = type_name
                        break

        # Placer les différents types de cases
        place_type("piège", nombre_pieges)
        place_type("ressource", nombre_ressources)
        place_type("indice", nombre_indices)

        return grid
    
    #==========================================================================================================#
    #               Définition qui permet de placer le trésor sur une case aléatoire de la grille              #
    #==========================================================================================================#
    
    def place_tresor(self):
        """Place le trésor dans une zone centrale de la grille."""
        # Définir une marge centrale proportionnelle à la grille
        center_margin_x = GRID_COLUMNS // 4  # 25% de la largeur
        center_margin_y = GRID_ROWS // 4  # 25% de la hauteur
        
        # Définir les bornes de la zone centrale
        center_start_x = center_margin_x
        center_end_x = GRID_COLUMNS - center_margin_x
        center_start_y = center_margin_y
        center_end_y = GRID_ROWS - center_margin_y

        while True:
            # Générer des coordonnées aléatoires dans la zone centrale
            x = random.randint(center_start_x, center_end_x - 1)
            y = random.randint(center_start_y, center_end_y - 1)

            # Vérifier que la case est normale
            if self.grid[y][x].type == "normale":
                self.grid[y][x].type = "trésor"  # Placer le trésor
                self.tresor_position = (x, y)  # Enregistrer la position du trésor
                print(f"Le trésor a été placé sur la case ({x}, {y})")
                break
    
    
    #==========================================================================================================#
    #               Définition qui permet de placer les portes autours du trésors                              #
    #==========================================================================================================#
    
    def place_portes(self):
        if not hasattr(self, 'tresor_position'):
            print("Erreur : Le trésor doit être placé avant les portes.")
            return

        tx, ty = self.tresor_position  # Position du trésor
        portes_places = []
        
        # Directions possibles autour du trésor
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            px, py = tx + dx, ty + dy
            # Vérifier que les coordonnées sont dans les limites de la grille
            if 0 <= px < GRID_COLUMNS and 0 <= py < GRID_ROWS:
                # Placer une porte si la case est normale
                if self.grid[py][px].type == "normale" or self.grid[py][px].type == "piège" or self.grid[py][px].type == "ressource" or self.grid[py][px].type == "indice"  :
                    self.grid[py][px].type = "porte"
                    portes_places.append((px, py))
                    print(f"Porte placée sur la case ({px}, {py})")

        # Définir une des portes comme correcte
        if portes_places:
            self.porte_correcte = random.choice(portes_places)
            print(f"La porte correcte est sur la case {self.porte_correcte}")
        else:
            print("Erreur : Aucune porte n'a été placée.")

        # Vérification du nombre de portes placées
        if len(portes_places) < 4:
            print(f"Erreur : Seulement {len(portes_places)} portes ont été placées autour du trésor.")
    
    #==========================================================================================================#
    #                        Définition qui permet de placer une clé aléatoire éloignée                        #
    #==========================================================================================================#
    
    def place_clef(self):
    
        while True:
            # Générer des coordonnées aléatoires dans les limites de la grille
            x = random.randint(0, GRID_COLUMNS - 1)
            y = random.randint(0, GRID_ROWS - 1)

            # S'assurer que la clé n'est pas trop proche du trésor
            tx, ty = self.tresor_position
            if abs(x - tx) + abs(y - ty) > (GRID_COLUMNS + GRID_ROWS) // 4:  # Distance suffisante
                if self.grid[y][x].type == "normale":  # Vérifier que la case est normale
                    self.grid[y][x].type = "clé"  # Placer la clé
                    self.clef_position = (x, y)  # Enregistrer la position de la clé
                    print(f"Clé placée sur la case ({x}, {y})")
                    break
    
    
    
    #==========================================================================================================#
    #               Définition pour génerer une animation quand le trésore est trouvé et recuperé              #
    #==========================================================================================================#
    
    def treasure_animation(self, x, y):

        # Charger la police pour le texte
        font = pygame.font.Font("images/police.ttf", 72)  # Police pixel art avec taille 72
        
        # Calcul des positions avec les offsets
        center_x = x * CELL_SIZE + MARGIN_X + CELL_SIZE // 2
        center_y = y * CELL_SIZE + MARGIN_Y + CELL_SIZE // 2
        
        for i in range(30):  # Répéter l'effet
            self.flip_display()  # Réinitialiser l'affichage pour éviter d'écraser la grille
            
            # Calculer le rayon des cercles pour l'effet
            radius = i * 10  # Le rayon augmente à chaque itération
            alpha = max(255 - (i * 12), 0)  # Réduire l'opacité
            
            # Créer une surface temporaire avec transparence
            temp_surface = pygame.Surface((CELL_SIZE * 2, CELL_SIZE * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                temp_surface,
                (255, 223, 0, alpha),  # Couleur dorée avec transparence
                (CELL_SIZE, CELL_SIZE),  # Centre du cercle
                radius // 2
            )
            # Blit la surface temporaire sur l'écran principal
            self.screen.blit(temp_surface, (center_x - CELL_SIZE, center_y - CELL_SIZE))

            # Afficher un message rouge au centre de l'écran
            message = "Victoire !"
            text = font.render(message, True, (255, 0, 0))  # Rouge
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            self.screen.blit(text, text_rect)
            
            # Mettre à jour l'écran et ajouter un délai
            pygame.display.flip()
            pygame.time.delay(100)  # 100 ms entre chaque étape de l'animation
    
    
    #===================================================================================================#
    #               Définition qui genere aleatoirement  les 2 équipes (joueur1 et joueur 2)            #
    #===================================================================================================#
    
    def create_random_team(self, team):
        unit_classes = [Explorateur, Archeologue, Chasseur]
        units = []
        for _ in range(3):
            x = random.randint(0, GRID_COLUMNS - 1)
            y = random.randint(0, GRID_ROWS - 1)
            units.append(random.choice(unit_classes)(x, y, team))
        return units
    
    
    #============================================================================================================================#
    #               Définition qui initialise les équipes en placant les unités aux coins opposés de la grille                   #
    #============================================================================================================================#
    


    def initialize_teams(self):

        # Positions pour l'équipe 1 (en haut à gauche)
        team_1_positions = [(0, 0), (1, 0), (0, 1)]
        # Positions pour l'équipe 2 (en bas à droite)
        team_2_positions = [
            (GRID_COLUMNS - 1, GRID_ROWS - 1),
            (GRID_COLUMNS - 2, GRID_ROWS - 1),
            (GRID_COLUMNS - 1, GRID_ROWS - 2),
        ]

        # Placer les unités de l'équipe 1
        for i, unit in enumerate(self.player_units):
            if i < len(team_1_positions):  # Vérifier que l'index est valide
                grid_x, grid_y = team_1_positions[i]
                unit.x = grid_x
                unit.y = grid_y

        # Placer les unités de l'équipe 2
        for i, unit in enumerate(self.enemy_units):
            if i < len(team_2_positions):  # Vérifier que l'index est valide
                grid_x, grid_y = team_2_positions[i]
                unit.x = grid_x
                unit.y = grid_y

        # Affiche les coordonnées des unités pour débogage
        print("Positions des unités de l'équipe 1 (player):")
        for unit in self.player_units:
            print(f"{unit.name} - x: {unit.x}, y: {unit.y}")

        print("Positions des unités de l'équipe 2 (enemy):")
        for unit in self.enemy_units:
            print(f"{unit.name} - x: {unit.x}, y: {unit.y}")
                
    #========================================================================================================================#
    #               Définition qui permet au joueur d'interagire avec les unités en utilisants differants touches            #
    #========================================================================================================================#
    
    def handle_player_turn(self):
        # Vérifier les unités actives de l'équipe en cours
        actuelle_units = [u for u in self.player_units if u.is_active] if self.debut_player == 1 else [u for u in self.enemy_units if u.is_active]
        ennemis = self.enemy_units if self.debut_player == 1 else self.player_units
        
        
        if not actuelle_units:  # Si aucune unité active dans l'équipe
            self.fin_de_jeu()  # Vérifier les conditions de fin de jeu
            return  # Arrêter le tour
        
        # Réinitialiser l'indice sélectionné si l'unité actuelle est invalide
        if self.selected_unit_index >= len(actuelle_units) or not actuelle_units[self.selected_unit_index].is_active:
            self.selected_unit_index = 0
        
        unite_selectionne = actuelle_units[self.selected_unit_index]
        
        # S'assurer que l'unité sélectionnée est active, sinon passer à la suivante
        while not unite_selectionne.is_active:
            self.selected_unit_index = (self.selected_unit_index + 1) % len(actuelle_units)
            unite_selectionne = actuelle_units[self.selected_unit_index]
                                           
        
        # Forcer le recalcul des zones d'accessibilité
        self.selected_position = (unite_selectionne.x, unite_selectionne.y)
        self.flip_display()  # Redessiner l'affichage avec la bonne zone d'accessibilité
            
        has_acted = False
        
        # Afficher le popup pour signaler le changement de tour
        if not self.turn_popup_start_time:  # Afficher seulement si ce n'est pas déjà affiché
            self.turn_popup_message = f"Tour du Joueur {self.debut_player}"
            self.turn_popup_start_time = pygame.time.get_ticks()

        while not has_acted:
            self.flip_display()  # Mettre à jour l'affichage (inclut le popup)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False  # Quitter le jeu proprement

                if self.current_riddle:  # Si une énigme est active
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:  # Valider la réponse
                            try:
                                # Comparer la réponse en transformant tout en chaînes pour éviter les erreurs de type
                                if str(self.player_input).strip().lower() == str(self.current_riddle["answer"]).strip().lower():
                                    self.add_message(f"Bonne réponse ! {self.current_riddle['unit'].name} a résolu l'énigme.")
                                    self.current_riddle["case"].type = "normale"  # L'indice devient une case normale
                                else:
                                    self.add_message(f"Mauvaise réponse. {self.current_riddle['unit'].name} perd 10 PV.")
                                    self.current_riddle["unit"].health -= 10
                                    if self.current_riddle["unit"].health <= 0:
                                        self.add_message(f"{self.current_riddle['unit'].name} est éliminé suite à une mauvaise réponse.")
                            except ValueError:
                                self.add_message("Erreur : veuillez entrer une réponse valide.")

                            # Réinitialisation après la réponse
                            self.current_riddle = None
                            self.player_input = ""
                            has_acted = True  # Fin du tour après réponse
                        elif event.key == pygame.K_BACKSPACE:  # Supprimer un caractère
                            self.player_input = self.player_input[:-1]
                        else:
                            # Ajouter le caractère à la réponse
                            self.player_input += event.unicode
                else:  # Pas d'énigme active, gérer les déplacements et autres actions
                    if event.type == pygame.KEYDOWN:
                        dx, dy = 0, 0
                        if event.key == pygame.K_m:  # Activer/désactiver la console popup
                            self.show_console_popup = not self.show_console_popup
                        elif event.key == pygame.K_c:
                            self.show_commands = not self.show_commands
                            break  # Interruption pour éviter une boucle infinie
                        elif event.key == pygame.K_LEFT:
                            dx = -1
                        elif event.key == pygame.K_RIGHT:
                            dx = 1
                        elif event.key == pygame.K_UP:
                            dy = -1
                        elif event.key == pygame.K_DOWN:
                            dy = 1
                        elif event.key == pygame.K_TAB:
                            self.selected_unit_index = (self.selected_unit_index + 1) % len(actuelle_units)
                            unite_selectionne = actuelle_units[self.selected_unit_index]
                            accessible_positions = get_accessible_positions(unite_selectionne, GRID_COLUMNS, GRID_ROWS, game = self)
                            self.selected_position = (unite_selectionne.x, unite_selectionne.y)
                            self.last_action_message = f"{unite_selectionne.name} est sélectionné."
                            # Forcer le recalcul des zones d'accessibilité pour la nouvelle unité
                            self.flip_display()
                            break

                        if dx != 0 or dy != 0:
                            # Calculer les nouvelles coordonnées proposées
                            new_x = max(0, min(GRID_COLUMNS - 1, self.selected_position[0] + dx))
                            new_y = max(0, min(GRID_ROWS - 1, self.selected_position[1] + dy))
                            
                            # Vérifiez si la position proposée est accessible
                            accessible_positions = get_accessible_positions(unite_selectionne, GRID_COLUMNS, GRID_ROWS)
                            if (new_x, new_y) in accessible_positions:
                                self.selected_position = (new_x, new_y)
                            else:
                                print("Position non accessible.")
                        if event.key == pygame.K_SPACE:
                            accessible_positions = get_accessible_positions(unite_selectionne, GRID_COLUMNS, GRID_ROWS, game = self)
                            if self.selected_position in accessible_positions:
                                # Récupérer la case à la position sélectionnée
                                case = self.grid[self.selected_position[1]][self.selected_position[0]]
        
                                # Vérifiez si la case est une porte
                                if case.type == "porte" and not unite_selectionne.has_key:
                                    # Empêcher le passage si l'unité n'a pas de clé
                                    self.add_message(f"{unite_selectionne.name} ne peut pas passer par la porte sans clé.")
                                    continue
                                elif case.type == "porte" and (self.selected_position != self.porte_correcte):
                                    # Bloquer le passage si ce n'est pas la bonne porte
                                    self.add_message(f"{unite_selectionne.name} ne peut pas passer, porte incorrecte.")
                                    # Reste sur place, ajoutez ici une animation ou effet si nécessaire
                                    self.draw_door_locked_effect(unite_selectionne.x, unite_selectionne.y)
                                    unite_selectionne.health -= 10  # Infliger des dégâts si porte incorrecte
                                    unite_selectionne.health = max(0, unite_selectionne.health)
                                    if unite_selectionne.health == 0:
                                        self.add_message(f"{unite_selectionne.name} a été éliminé.")
                                    continue

                                # Si tout est OK, effectuer le déplacement et appliquer l'effet de la case
                                unite_selectionne.x, unite_selectionne.y = self.selected_position
                                self.last_action_message = case.effet_case(unite_selectionne, self)
                                has_acted = True  # Signale qu'une action a été effectuée
                            else:
                                print("Déplacement non valide.")
                       
                        # Gestion des compétences
                        if event.key == pygame.K_r and isinstance(unite_selectionne, Explorateur):  # Coup rapide
                            cibles = unite_selectionne.get_cibles_accessibles(ennemis, GRID_COLUMNS, GRID_ROWS)
                            if not cibles:
                                print("Aucune cible disponible pour Coup rapide.")
                                break  # Éviter une boucle infinie
                            cible = cibles[0]  # Prenez la première cible disponible
                            competence = unite_selectionne.competences[0]  # Coup rapide
                            competence.utiliser(unite_selectionne, cible, self)
                            has_acted = True

                        elif event.key == pygame.K_t and isinstance(unite_selectionne, Archeologue):  # Attaque ciblée
                            cibles = unite_selectionne.get_cibles_accessibles(ennemis, GRID_COLUMNS, GRID_ROWS)
                            if cibles:
                                cible = cibles[0]
                                competence = unite_selectionne.competences[0]
                                competence.utiliser(unite_selectionne, cible, self)
                                has_acted = True
                        elif event.key == pygame.K_a and isinstance(unite_selectionne, Archeologue):  # Analyse de l'environnement
                            competence = unite_selectionne.competences[2]
                            competence.utiliser(unite_selectionne, None, self)
                            has_acted = True

                        elif event.key == pygame.K_y and isinstance(unite_selectionne, Chasseur):  # Tir à distance
                            cibles = unite_selectionne.get_cibles_accessibles(ennemis, GRID_COLUMNS, GRID_ROWS)
                            if cibles:
                                cible = cibles[0]
                                competence = unite_selectionne.competences[0]
                                competence.utiliser(unite_selectionne, cible, self)
                                has_acted = True
                        elif event.key == pygame.K_e and isinstance(unite_selectionne, Explorateur):  # Révéler zone
                            competence = unite_selectionne.competences[1]  # Hypothèse : Révélation est la deuxième compétence
                            competence.utiliser(unite_selectionne, None, self)
                            self.afficher_effet_revelation(unite_selectionne)  # Ajout d'un effet visuel pour la révélation
                            has_acted = True
                        elif event.key == pygame.K_p and isinstance(unite_selectionne, Chasseur):  # Pose de piège
                            competence = unite_selectionne.competences[1]
                            competence.utiliser(unite_selectionne, None, self)
                            has_acted = True

                        elif event.key == pygame.K_b and isinstance(unite_selectionne, Chasseur):  # Brouillard de guerre
                            competence = unite_selectionne.competences[2]
                            competence.utiliser(unite_selectionne, None, self)
                            has_acted = True

                    # Vérifier si le jeu est terminé après l'action
                            if self.fin_de_jeu():
                                return  # Arrêter le tour si le jeu est terminé

            # Alterner le joueur actif après une action réussie ou une énigme résolue
            if has_acted and not self.current_riddle:
                self.selected_position = None
                self.selected_unit_index = 0
                self.debut_player = 2 if self.debut_player == 1 else 1
                self.turn_popup_start_time = None  # Réinitialiser le popup pour le prochain tour
    
    #========================================================================================================================#
    #               Définition peremettant de declarer les conditions pour l'arret (gagner) pour arreter le jeu              #
    #========================================================================================================================#
   
    def fin_de_jeu(self):
        # Vérifier si une équipe a trouvé le trésor
        for unit in self.player_units + self.enemy_units:
            if self.grid[unit.y][unit.x].type == "trésor":
                winner = "Player" if unit in self.player_units else "Enemy"
                print(f"Victoire : {winner} a trouvé le trésor !")
                return True  # Fin de jeu confirmée

        if all(not unit.is_active for unit in self.player_units):
            print("Victoire : l'ennemi a gagné car toutes les unités du joueur sont mortes.")
            return True
        if all(not unit.is_active for unit in self.enemy_units):
            print("Victoire : le joueur a gagné car toutes les unités ennemies sont mortes.")
            return True

        # Sinon, le jeu continue
        return False
    
    #==================================================================================================#
    #               Définition permettant de dessiner la grile sur l'écran avec des marges             #
    #==================================================================================================#
    
    def draw_grid(self):

        for y, row in enumerate(self.grid):
            for x, case in enumerate(row):
                # Calculer la position avec les marges
                pos_x = x * CELL_SIZE + MARGIN_X
                pos_y = y * CELL_SIZE + MARGIN_Y
            
                # Dessiner l'image de la case
                image = self.tile_images.get(case.type, self.tile_images["normale"])
                self.screen.blit(image, (pos_x, pos_y))
            
                # Dessiner une bordure bleue autour de chaque case
                pygame.draw.rect(
                    self.screen,
                    (0, 0, 0),  # Couleur bleue
                    (pos_x, pos_y, CELL_SIZE, CELL_SIZE), 1  # Position et taille de la bordure                                    
                )
   
    #========================================================================================================================#
    #               Définition qui permet la création de la barre de vie ( 100 hp ) pour chaque unité                        #
    #========================================================================================================================# 
    
    def draw_health_bar(self, unit, color):

        # Position avec les marges
        barre_x = unit.x * CELL_SIZE + MARGIN_X
        barre_y = unit.y * CELL_SIZE + MARGIN_Y - 5  # 5 pixels au-dessus de l'unité
        
        # Largeur et hauteur de la barre de vie
        largeur_barre = CELL_SIZE
        hauteur_barre = 5
        
        # Ratio de la santé
        health_ratio = unit.health / 100
        
        # Dessiner la barre de fond (gris)
        pygame.draw.rect(self.screen, (50, 50, 50), (barre_x, barre_y, largeur_barre, hauteur_barre))
        
        # Dessiner la barre de vie (colorée)
        pygame.draw.rect(self.screen, color, (barre_x, barre_y, largeur_barre * health_ratio, hauteur_barre))
        
        # Dessiner l'icône de clé si l'unité en possède une
        if unit.has_key:
            # Positionner l'icône à gauche de la barre de vie
            key_icon_x = barre_x - 25  # Place l'icône à gauche avec un espace
            key_icon_y = barre_y - 5 # Alignée verticalement avec la barre de vie

            # Appliquer un effet visuel (exemple : cercle autour de l'icône)
            pygame.draw.circle(self.screen, (255, 255, 0), (key_icon_x + 10, key_icon_y + 10), 12)  # Cercle jaune
            
            # Dessiner l'icône (redimensionnée pour meilleure visibilité)
            key_icon = pygame.transform.scale(self.key_icon, (20, 20))  # Augmenter légèrement la taille
            self.screen.blit(key_icon, (key_icon_x, key_icon_y))
            
    #========================================================================================================================#
    #               Définition qui permet de dessiner les unités et leur barre de vie sur la grille du jeu                   #
    #========================================================================================================================# 
    
    def draw_units(self):

        for unit in self.player_units + self.enemy_units:
            if unit.is_active:
                unit.draw(self.screen, MARGIN_X, MARGIN_Y, CELL_SIZE)
                self.draw_health_bar(unit, (0, 255, 0))
        
        for unit in self.enemy_units:
            if unit.is_active:
                # Dessiner uniquement les unités qui ont encore des PV
                unit.draw(self.screen, MARGIN_X, MARGIN_Y, CELL_SIZE)
                self.draw_health_bar(unit, (255, 0, 0))  # Barre de vie rouge
            
   
   #===========================================================================================#
   #               Définition dessiner l'animation d'explosion                                 #
   #===========================================================================================#  
   
    def explosion_animation(self, x, y):
        # Couleurs de l'explosion (Rouge -> Orange -> Jaune -> Disparaît)
        explosion_colors = [(255, 0, 0), (255, 69, 0), (255, 140, 0), (255, 255, 0)]

        # Centre de l'explosion
        center_x = x * CELL_SIZE + MARGIN_X + CELL_SIZE // 2
        center_y = y * CELL_SIZE + MARGIN_Y + CELL_SIZE // 2

        # Créer plusieurs étapes d'explosion
        for step in range(1, 16):  # 15 étapes pour une animation fluide
            self.flip_display()  # Rafraîchir l'écran

            for i, color in enumerate(explosion_colors):
            # Dessiner les cercles successifs
                pygame.draw.circle(
                    self.screen,
                    color,
                    (center_x, center_y),
                    step * (i + 2),  # Le rayon augmente selon la couleur
                    width = max (1 , 5 - i)  # Les cercles extérieurs sont plus fins
            ) 

        # Mettre à jour l'écran
        pygame.display.flip()
        pygame.time.delay(50)  # Pause entre chaque étape 
   
   
   #================================================================================================#
   #               Définition pour dessiner l'animation d'explosion                                 #
   #================================================================================================#
   
    def draw_accessible_areas_with_selection(self, unit, selected_position):
    
        accessible_positions = get_accessible_positions(unit, GRID_COLUMNS, GRID_ROWS, game=self)

        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)

        accessible_color = (173, 216, 230, 100)  # Bleu clair transparent
        blocked_color = (255, 0, 0, 150)  # Rouge transparent pour les zones bloquées
        selected_color = (0, 255, 0, 150)


        for y, row in enumerate(self.grid):
            for x, case in enumerate(row):
                rect = (
                    x * CELL_SIZE + MARGIN_X,
                    y * CELL_SIZE + MARGIN_Y,
                    CELL_SIZE,
                    CELL_SIZE,
                )
                if (x, y) in accessible_positions:
                    if case.type == "porte" and not unit.has_key:
                        pygame.draw.rect(overlay, blocked_color, rect)
                    else:
                        pygame.draw.rect(overlay, accessible_color, rect)

                if selected_position == (x, y):
                    pygame.draw.rect(overlay, selected_color, rect)

        self.screen.blit(overlay, (0, 0))
   
   
   #================================================================================================#
   #               Définition pour dessiner les effets d'attaque                                    #
   #================================================================================================#
   
    def afficher_effet_attaque(self, cible, degats):
        font = pygame.font.Font(None, 36)
        # Calculer la position du texte avec les offsets
        text_x = cible.x * CELL_SIZE + MARGIN_X + CELL_SIZE // 2
        text_y = cible.y * CELL_SIZE + MARGIN_Y + CELL_SIZE // 2
        degats_text = font.render(f"-{degats}", True, (255, 0, 0))
        text_rect = degats_text.get_rect(center=(text_x, text_y))

        flash_duration = 500
        start_time = pygame.time.get_ticks()
        
        while pygame.time.get_ticks() - start_time < flash_duration:
            self.flip_display()
            # Dessiner un rectangle rouge autour de la cible
            pygame.draw.rect(
                self.screen,
                (255, 0, 0),
                (
                    cible.x * CELL_SIZE + MARGIN_X,
                    cible.y * CELL_SIZE + MARGIN_Y,
                    CELL_SIZE,
                    CELL_SIZE
                ),
                5
            )
            # Afficher le texte des dégâts
            self.screen.blit(degats_text, text_rect)
            pygame.display.flip()
            
   #================================================================================================#
   #               Définition pour dessiner les effets d'attaque a tir distance                     #
   #================================================================================================#
    
    def afficher_effet_tir_distance(self, attaquant, cible):
        
        start_x = attaquant.x * CELL_SIZE + MARGIN_X + CELL_SIZE // 2
        start_y = attaquant.y * CELL_SIZE + MARGIN_Y + CELL_SIZE // 2
        end_x = cible.x * CELL_SIZE + MARGIN_X + CELL_SIZE // 2
        end_y = cible.y * CELL_SIZE + MARGIN_Y + CELL_SIZE // 2
        
        projectile_color = (255, 165, 0)  # Orange pour représenter le tir
        projectile_radius = 5
        steps = 20

        # Animation du tir
        for step in range(steps + 1):
            t = step / steps
            current_x = int(start_x + t * (end_x - start_x))
            current_y = int(start_y + t * (end_y - start_y))
            self.flip_display()  # Mettre à jour l'affichage derrière le projectile
            pygame.draw.circle(self.screen, projectile_color, (current_x, current_y), projectile_radius)
            pygame.display.flip()
            pygame.time.delay(50)

        # Effet visuel sur la cible
        flash_duration = 300
        start_time = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_time < flash_duration:
            pygame.draw.rect(
                self.screen,
                (255, 0, 0),
                (cible.x * CELL_SIZE + MARGIN_X, cible.y * CELL_SIZE + MARGIN_Y, CELL_SIZE, CELL_SIZE),
                5
            )
            pygame.display.flip()
    
   #================================================================================================#
   #               Définition pour dessiner les effets d'attaque coup rapide                        #
   #================================================================================================#
   
    def afficher_effet_coup_rapide(self, attaquant, cible):
        
        start_x = attaquant.x * CELL_SIZE + MARGIN_X + CELL_SIZE // 2
        start_y = attaquant.y * CELL_SIZE + MARGIN_Y + CELL_SIZE // 2
        cible_x = cible.x * CELL_SIZE + MARGIN_X + CELL_SIZE // 2
        cible_y = cible.y * CELL_SIZE + MARGIN_Y + CELL_SIZE // 2

        effect_color = (0, 255, 0)  # Vert pour représenter la rapidité
        flash_duration = 500  # Durée de l'effet en millisecondes

        start_time = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_time < flash_duration:
            self.flip_display()
            pygame.draw.line(
                self.screen,
                effect_color,
                (start_x, start_y),
                (cible_x, cible_y),
                5  # Épaisseur de la ligne
            )
            pygame.display.flip()
            pygame.time.delay(50)
   
   
   #=========================================================================================================#
   #               Définition pour afficher les effets de la competence de revelation                        #
   #=========================================================================================================#
   
    def afficher_effet_revelation(self, utilisateur):
        
        # Couleurs pour l'effet
        reveal_color = (173, 216, 230, 100)  # Bleu clair transparent pour la zone accessible
        piege_color = (255, 0, 0, 150)  # Rouge transparent pour les pièges détectés
        flash_duration = 500  # Durée du flash en millisecondes

        # Obtenir les positions accessibles
        accessible_positions = get_accessible_positions(utilisateur, GRID_COLUMNS, GRID_ROWS)

        # Créer une surface transparente pour superposition
        overlay = pygame.Surface((GRID_COLUMNS * CELL_SIZE, GRID_ROWS * CELL_SIZE), pygame.SRCALPHA)

        # Dessiner les zones accessibles
        for pos in accessible_positions:
            x, y = pos
            if self.grid[y][x].type == "piège":
                pygame.draw.rect(
                    overlay,
                    piege_color,  # Rouge pour les pièges
                    (x * CELL_SIZE + MARGIN_X, y * CELL_SIZE + MARGIN_Y, CELL_SIZE, CELL_SIZE),
                )
            else:
                pygame.draw.rect(
                    overlay,
                    reveal_color,  # Bleu clair pour les autres cases accessibles
                    (x * CELL_SIZE + MARGIN_X, y * CELL_SIZE + MARGIN_Y, CELL_SIZE, CELL_SIZE),
                )

        # Appliquer la surface de superposition
        self.screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(300)  # Pause pour que l'effet reste visible brièvement

        # Ajouter un flash temporaire pour les cases détectées
        start_time = pygame.time.get_ticks()
        
        while pygame.time.get_ticks() - start_time < flash_duration:
            for pos in accessible_positions:
                x, y = pos
                if self.grid[y][x].type == "piège":
                    pygame.draw.rect(
                        self.screen,
                        (255, 255, 0),  # Jaune pour un flash temporaire sur les pièges
                        (x * CELL_SIZE + MARGIN_X, y * CELL_SIZE + MARGIN_Y, CELL_SIZE, CELL_SIZE),
                        3,  # Épaisseur du contour
                    )
            pygame.display.flip()
            pygame.time.delay(50)  # Petite pause pour rendre l'effet fluide
            
    #=====================================================================================================#
    #               Définition pour afficher l'effet de la compétence de pose piege                       #
    #=====================================================================================================#
   
    def afficher_effet_pose_piege(self, position):
        
        x, y = position
        flash_duration = 500  # Durée de l'effet en millisecondes
        start_time = pygame.time.get_ticks()

        while pygame.time.get_ticks() - start_time < flash_duration:
            pygame.draw.rect(
                self.screen,
                (255, 140, 0),  # Orange pour indiquer un piège
                (
                    x * CELL_SIZE + MARGIN_X,  # Inclure l'offset horizontal
                    y * CELL_SIZE + MARGIN_Y,  # Inclure l'offset vertical
                    CELL_SIZE,  # Largeur de la case
                    CELL_SIZE   # Hauteur de la case
                ),
                3  # Épaisseur du contour
            )
            pygame.display.flip()
            pygame.time.delay(50)
            
    #=====================================================================================================#
    #               Définition pour afficher l'effet de la compétence de Brouillard                       #
    #=====================================================================================================#
    
    def afficher_effet_brouillard(self, utilisateur):
        
        # Créer une surface transparente pour l'effet de brouillard
        overlay = pygame.Surface(
            (GRID_COLUMNS * CELL_SIZE, GRID_ROWS * CELL_SIZE), pygame.SRCALPHA
        )
        fog_color = (50, 50, 50, 150)  # Gris semi-transparent pour le brouillard

        # Appliquer le brouillard uniquement sur la zone accessible
        accessible_positions = get_accessible_positions(utilisateur, GRID_COLUMNS, GRID_ROWS)

        for x, y in accessible_positions:
            pygame.draw.rect(
                overlay,
                fog_color,
                (
                    x * CELL_SIZE + MARGIN_X,  # Inclure l'offset horizontal
                    y * CELL_SIZE + MARGIN_Y,  # Inclure l'offset vertical
                    CELL_SIZE,  # Largeur de la case
                    CELL_SIZE   # Hauteur de la case
                )
            )

        # Afficher l'overlay sur l'écran
        self.screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(500)  # Pause pour que l'effet reste visible brièvement
        
    
    #================================================================================================================#
    #               Définition pour afficher l'effet de la compétence Analyse de l'environnement                     #
    #================================================================================================================#
    
    def afficher_effet_analyse(self, utilisateur):
        
        # Obtenir les positions accessibles
        accessible_positions = get_accessible_positions(utilisateur, GRID_COLUMNS, GRID_ROWS)
        
        # Couleurs lumineuses pour les cases spéciales
        colors = {
            "indice": (0, 255, 255),  # Cyan lumineux pour les indices
            "ressource": (0, 255, 0),  # Vert clair lumineux pour les ressources
            "autre": (100, 100, 100)  # Gris pour les autres cases accessibles
        }

        # Nombre d'étapes pour l'animation
        flash_steps = 10
        max_radius = CELL_SIZE // 2  # Taille maximum pour le flash

        # Pour chaque étape de l'animation
        for step in range(flash_steps):
            self.flip_display()  # Redessiner l'écran sans effacer l'effet
            for x, y in accessible_positions:
                case_type = self.grid[y][x].type
                color = colors.get(case_type, colors["autre"])
                
                # Calculer le rayon du cercle (agrandissement progressif)
                radius = int((step + 1) / flash_steps * max_radius)
                center = (x * CELL_SIZE + MARGIN_X + CELL_SIZE // 2, y * CELL_SIZE + MARGIN_Y + CELL_SIZE // 2)

                if case_type in colors:  # Mettre en évidence les cases spéciales
                    pygame.draw.circle(
                        self.screen,
                        color,
                        center,
                        radius
                    )

            pygame.display.flip()  # Mettre à jour l'écran
            pygame.time.delay(50)  # Pause entre les étapes

        # Dernière étape : afficher les zones révélées en permanence
        overlay = pygame.Surface((GRID_COLUMNS * CELL_SIZE, GRID_ROWS * CELL_SIZE), pygame.SRCALPHA)
        for x, y in accessible_positions:
            case_type = self.grid[y][x].type
            color = (*colors.get(case_type, colors["autre"]), 100)  # Ajouter transparence
            pygame.draw.rect(
                overlay,
                color,
                (x * CELL_SIZE + MARGIN_X, y * CELL_SIZE + MARGIN_Y, CELL_SIZE, CELL_SIZE)
            )

        self.screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(500)  # Pause finale pour que l'effet reste visible

    #===============================================================================================================#
    #               Définition pour afficher l'effet pour indiquer que la porte est verrouillé                      #
    #===============================================================================================================#
    
    def draw_door_locked_effect(self, x, y):
      
        # Calculer les coordonnées avec les offsets
        rect_x = x * CELL_SIZE + MARGIN_X
        rect_y = y * CELL_SIZE + MARGIN_Y
        rect_size = CELL_SIZE  # Taille de la cellule

        # Dessiner un rectangle rouge pour indiquer l'erreur
        pygame.draw.rect(
            self.screen,
            (255, 0, 0),  # Rouge vif
            (rect_x, rect_y, rect_size, rect_size),
            5  # Épaisseur de la bordure
        )
        
        # Mettre à jour l'écran pour afficher l'effet
        pygame.display.flip()
        pygame.time.delay(500)  # Afficher l'effet pendant 500 ms
            
   #========================================================================================================================#
   #               Définition pour pouvoir l'afficher (dessiner) sur l'ecran lors du fonctionnement du jeu                  #
   #========================================================================================================================# 
   
    def draw_popup(self, lines, x, y, width, height):

        pygame.draw.rect(self.screen, (30, 30, 30), (x, y, width, height))  # Fond sombre
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, width, height), 3)  # Bordure blanche

        font_title = pygame.font.Font(None, 40)  # Titre
        font_text = pygame.font.Font(None, 28)  # Texte standard
        line_height = 35
        y_offset = y + 20  # Position de départ verticale

        for i, line in enumerate(lines):
            if i == 0:  # Premier élément est un titre
                text = font_title.render(line, True, (255, 255, 0))  # Couleur jaune
            else:
                text = font_text.render(line, True, (200, 200, 200))  # Couleur grise
            self.screen.blit(text, (x + 20, y_offset))
            y_offset += line_height
    
    #========================================================================================================================#
    #               Définition pour afficher un popup pour permettre au joueurs de savoir c'est le tour de qui               #
    #========================================================================================================================#
    
    def draw_turn_popup(self):

        if self.turn_popup_message and self.turn_popup_start_time:
            elapsed_time = pygame.time.get_ticks() - self.turn_popup_start_time
            if elapsed_time < 2000:  # Afficher pendant 2 secondes
                popup_width = self.screen.get_width() // 2
                popup_height = 30
                popup_x = (self.screen.get_width() - popup_width) // 2
                popup_y = 10  # Position en haut de l'écran

                # Fond semi-transparent
                s = pygame.Surface((popup_width, popup_height))
                s.set_alpha(200)  # Transparence
                s.fill((0, 0, 0))  # Fond noir
                self.screen.blit(s, (popup_x, popup_y))

                # Texte
                text_surface = self.font.render(self.turn_popup_message, True, (255, 255, 255))
                text_x = popup_x + (popup_width - text_surface.get_width()) // 2
                text_y = popup_y + (popup_height - text_surface.get_height()) // 2
                self.screen.blit(text_surface, (text_x, text_y))
            else:
                # Supprimer le popup après 2 secondes
                self.turn_popup_message = None
                self.turn_popup_start_time = None
                
    #=====================================================================================================================================#
    #               Définition pour afficher les touches que peut l'utilisateur utiliser pour faire des actions tout au long du jeu       #
    #=====================================================================================================================================#
                
    def draw_popup_commands(self):

        try:
            # Charger l'image
            panneau_image = pygame.image.load("images/Commandes.png")
        except FileNotFoundError:
            print("Erreur : L'image Commandes.png est introuvable.")
            return
        
        # Dimensions de l'écran
        screen_width, screen_height = self.screen.get_width(), self.screen.get_height()
        
        # Ajuster les dimensions du popup
        new_width = 913
        new_height = 700
        panneau_image = pygame.transform.scale(panneau_image, (new_width, new_height))
        
        # Ajouter une bordure
        border_color = (64, 64, 64)  # Gris foncé
        border_thickness = 10  # Épaisseur de la bordure
        border_rect = pygame.Rect(
            (screen_width - new_width - 2 * border_thickness) // 2,
            (screen_height - new_height - 2 * border_thickness) // 2,
            new_width + 2 * border_thickness,
            new_height + 2 * border_thickness,
        )
        pygame.draw.rect(self.screen, border_color, border_rect)
        
        # Centrer et afficher le popup
        panneau_rect = panneau_image.get_rect(center=(screen_width // 2, screen_height // 2))
        self.screen.blit(panneau_image, panneau_rect)
    
    #===================================================================================================================================================#
    #               Définition qui permet d'afficher les messages du console dans un popup pour permettre a l'utilisateur de le voir durant le jeu      #
    #===================================================================================================================================================#
    
    def draw_console_popup(self):
        
        if not self.show_console_popup:
            return  # Ne rien faire si la console est masquée

        # Dimensions du popup console
        console_width = self.screen.get_width() // 2
        console_height = 150
        console_x = (self.screen.get_width() - console_width) // 2
        console_y = self.screen.get_height() - console_height - 10

        # Fond semi-transparent
        s = pygame.Surface((console_width, console_height))
        s.set_alpha(180)
        s.fill((0, 0, 0))
        self.screen.blit(s, (console_x, console_y))

        y_offset = console_y + 10

        if self.current_riddle:
            # Afficher uniquement l'énigme et la réponse utilisateur
            lines = self.current_riddle["question"].split("\n")
            for line in lines:
                text_surface = self.font.render(line, True, (255, 255, 255))
                self.screen.blit(text_surface, (console_x + 10, y_offset))
                y_offset += 20

            input_surface = self.font.render(f"Votre réponse : {self.player_input}", True, (200, 200, 200))
            self.screen.blit(input_surface, (console_x + 10, y_offset + 10))
        else:
            # Afficher les messages standards de la console
            for line in self.console_messages:
                text_surface = self.font.render(line, True, (255, 255, 255))
                self.screen.blit(text_surface, (console_x + 10, y_offset))
                y_offset += 20
        
    def update(self):

        pass  # Logique de mise à jour du jeu ici
    
    #==========================================================================#
    #               Définition pour afficher et rafraichire l'affichage        #
    #==========================================================================#
    
    def flip_display(self):

        self.screen.fill((0, 0, 0))  # Nettoyer l'écran
        self.draw_grid()            # Dessiner la grille
        
        # Dessiner les zones accessibles pour l'unité active
        active_units = self.player_units if self.debut_player == 1 else self.enemy_units
        self.draw_accessible_areas_with_selection(
            active_units[self.selected_unit_index],
            self.selected_position
        )
        
        self.draw_units()           # Dessiner les unités (avec bordures)
        self.draw_console_popup()
        self.draw_turn_popup()      # Dessiner le popup du changement de tour

        if self.show_commands:
            self.draw_popup_commands()
        
            
        pygame.display.flip()       # Mettre à jour l'affichage
