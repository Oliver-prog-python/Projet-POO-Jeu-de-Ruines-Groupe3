import pygame
import random
from TEST_Jeu_Units import Explorateur, Archeologue, Chasseur

# Dimensions
WIDTH, HEIGHT = 1300, 800
GRID_WIDTH = 800
UI_WIDTH = WIDTH - GRID_WIDTH
CELL_SIZE = GRID_WIDTH // 10

def get_accessible_positions(unit, grid_size):
    """Retourne une liste des positions accessibles en fonction de la portée de l'unité."""
    x, y = unit.x, unit.y

    # Définir la portée de déplacement selon le type d'unité
    max_range = 1 if isinstance(unit, (Archeologue, Chasseur)) else 2  # Portée par défaut

    accessible_positions = []

    # Parcourir toutes les cases accessibles dans les limites définies
    for dx in range(-max_range, max_range + 1):
        for dy in range(-max_range, max_range + 1):
            nx, ny = x + dx, y + dy
            # Vérifier que la case est dans les limites de la grille et respecte la distance de Manhattan
            if 0 <= nx < grid_size and 0 <= ny < grid_size and abs(dx) + abs(dy) <= max_range:
                accessible_positions.append((nx, ny))

    return accessible_positions

class Case:
    def __init__(self, type_case="normale"):
        self.type = type_case
        self.hidden = False  # Les cases commencent révélées

    def effet_case(self, unit, game):
        if self.type == "trésor":
            game.treasure_animation(unit.x, unit.y)  # Lancer l'animation
            return f"{unit.name} a trouvé le trésor ! Victoire !"

        if self.type == "piège":
            if isinstance(unit, Chasseur):  # si l'unité est un chasseur 
                return f"{unit.name} détecte et désamorce un piège."
            else:  # autres unités
                game.explosion_animation(unit.x, unit.y)
                unit.health -= 15
                unit.health = max(0, unit.health)  # Empêcher les PV négatifs
                game.check_et_supp_unit(unit)  # Vérifier si l'unité doit être supprimée
                return f"{unit.name} marche sur un piège et perd 15 PV."

        elif self.type == "ressource":
            unit.health = min(100, unit.health + 10)  # PV max à 100
            return f"{unit.name} récupère une ressource et gagne 10 PV."

        elif self.type == "indice":
            if isinstance(unit, Archeologue):
                # Défi pour le joueur contrôlant un archéologue
                choix_enigme = game.genere_enigme()
                print(f"Énigme : {choix_enigme['question']}")
                try:
                    player_reponse = input("Votre réponse : ")
                    if str(player_reponse).strip() == str(choix_enigme["réponse"]):
                        self.type = "normale"  # L'indice est résolu
                        unit.enigme_non_resolue = False  # Libère l'archéologue
                        return f"{unit.name} a résolu l'énigme avec succès !"
                    else:
                        unit.health -= 5
                        unit.health = max(0, unit.health)  # Empêcher les PV négatifs
                        unit.enigme_non_resolue = True  # Bloque l'archéologue
                        if unit.health == 0:
                            game.check_et_supp_unit(unit)  # Supprimer si PV = 0
                            return f"{unit.name} a échoué et est éliminé de la carte."
                        return f"{unit.name} a échoué à résoudre l'indice et perd 5 PV."

                except ValueError:
                    unit.health -= 5
                    unit.health = max(0, unit.health)
                    unit.enigme_non_resolue = True
                    if unit.health == 0:
                        game.check_et_supp_unit(unit)
                        return f"{unit.name} n'a pas répondu correctement et est éliminé."
                    return f"{unit.name} n'a pas répondu correctement et perd 5 PV."
            else:  # autres unités
                unit.health -= 10
                unit.health = max(0, unit.health)
                if unit.health == 0:
                    game.check_et_supp_unit(unit)
                    return f"{unit.name} est éliminé sur une case indice."
                return f"{unit.name} ne peut pas résoudre l'indice et perd 10 PV."
            
        elif self.type == "clé":
            if unit.has_key:
                return f"{unit.name} possède déjà une clé."
            else:
                unit.has_key = True  # L'unité récupère la clé
                self.type = "normale"  # La case redevient normale
                return f"{unit.name} a récupéré une clé magique !"
        elif self.type == "porte":    
            if unit.has_key:
            # Trouver les coordonnées de la case dans la grille
                for y, row in enumerate(game.grid):
                    for x, case in enumerate(row):
                        if case is self:  # Identifier la case actuelle
                            if (x, y) == game.porte_correcte:  # Vérifier si c'est la porte correcte
                                unit.has_key = False  # Consommer la clé pour ouvrir la porte
                                self.type = "normale"  # La porte est maintenant ouverte
                                return f"{unit.name} utilise une clé pour ouvrir la porte correcte !"
                            else:
                                unit.x=x
                                unit.y=y
                                game.draw_door_locked_effect(x, y)
                                #bloquer l'unité sur cette case
                                return f"{unit.name} essaie d'ouvrir une porte, mais ce n'est pas la bonne."
                else:
                    # Bloquer l'unité sur cette case si elle n'a pas de clé
                    for y, row in enumerate(game.grid):
                        for x, case in enumerate(row):
                            if case is self:
                                unit.x=x
                                unit.y=y
                                game.draw_door_locked_effect(x, y)
                                return f"{unit.name} a besoin d'une clé pour ouvrir cette porte."
        elif self.type == "ruines":
            if isinstance(unit, Explorateur):
                return f"{unit.name} explore efficacement les ruines."
            else:
                return f"{unit.name} explore les ruines sans compétences particulières."
        return f"{unit.name} explore les ruines."


    
    
class Game:
    def __init__(self, screen):
        self.screen = screen
        self.grid_size = 10
        self.cell_size = GRID_WIDTH // self.grid_size
        self.grid=self.initialize_grid()
        self.place_tresor()
        self.place_portes()
        self.place_clef()
        self.player_units = self.creation_random_team("player")
        self.enemy_units = self.creation_random_team("enemy")
        self.initialize_teams()
        self.choix_enigme = None

        # Ajouter cette ligne pour suivre la position sélectionnée
        self.selected_position = None  # Position sélectionnée (initialement None)
         
    

         # Charger les images des cases
        self.tile_images = {
            "normale": pygame.image.load("images/case_ruine2.png"),
            "piège": pygame.image.load("images/case_piege2.png"),
            "ressource": pygame.image.load("images/case_ressource2.png"),
            "indice": pygame.image.load("images/case_indice2.png"),
            "porte": pygame.image.load("images/case_porte.png"),
            "clé": pygame.image.load("images/case_clef.png"),
            
        }
         

        for key in self.tile_images:
            self.tile_images[key] = pygame.transform.scale(self.tile_images[key], (self.cell_size, self.cell_size))

        # Ajouter l'image du trésor
        self.tile_images["trésor"] = pygame.image.load("images/case_tresor2.png")
        self.tile_images["trésor"] = pygame.transform.scale(self.tile_images["trésor"], (self.cell_size, self.cell_size))
        
        self.debut_player=1 #commencer avec le joueur 1
        self.selected_unit_index = 0
        self.last_action_message = "Aucune action effectuée."


    def initialize_grid(self):
        """
        Crée une grille avec des cases de différents types en fonction de proportions prédéfinies.
        """
        grid = [[Case("normale") for _ in range(self.grid_size)] for _ in range(self.grid_size)]
    
    # Définir les proportions
        nombre_pieges = int(self.grid_size * self.grid_size * 0.1)  # 10% de pièges
        nombre_ressources = int(self.grid_size * self.grid_size * 0.2)  # 20% de ressources
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
    
    def place_tresor(self): # place trésor dans la zone centrale de la grille
        centre_marge = self.grid_size // 4  # Définir une marge pour centraliser le trésor
        center_start = centre_marge
        center_end = self.grid_size - centre_marge

        while True:
            x = random.randint(center_start,center_end - 1) 
            y = random.randint(center_start,center_end-1) 
            
            if self.grid[y][x].type == "normale":  # VERIFIE QUE la case est normale
                self.grid[y][x].type = "trésor"
                self.tresor_position = (x, y)  # Enregistrer la position du trésor
                print(f"Le trésor a été placé sur la case ({x}, {y})")
                break
    
    def place_portes(self):
        if not hasattr(self, 'tresor_position'):
            print("Erreur : Le trésor doit être placé avant les portes.")
            return

        tx, ty = self.tresor_position
        portes_places=[]
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            px, py = tx + dx, ty + dy
            if 0 <= px < self.grid_size and 0 <= py < self.grid_size:
                self.grid[py][px].type = "porte"
                portes_places.append((px,py))
                print(f"Porte placée sur la case ({px}, {py})")
        # Définir une des portes comme correcte
        if portes_places:
            self.porte_correcte = random.choice(portes_places)
            print(f"La porte correcte est sur la case {self.porte_correcte}")

        else: 
            print("Erreur:Aucune porte na été placée")
        # Vérifier qu'il y a bien 4 portes placées
        if len(portes_places) < 4:
            print(f"Erreur : Seulement {portes_places} portes ont été placées autour du trésor.")

    def place_clef(self):
        while True:
            x = random.randint(0, self.grid_size - 1)
            y = random.randint(0, self.grid_size - 1)
        # S'assure que la clé n'est pas trop proche du trésor
            tx, ty = self.tresor_position
            if abs(x - tx) + abs(y - ty) > self.grid_size // 2:  # Distance suffisante
                self.grid[y][x].type = "clé"
                self.clef_position = (x, y)
                break

    
    def initialize_teams(self):
    # Triangle pour l'équipe 1 (en haut à gauche)
        team_1_positions = [(0, 0), (0, 1), (1, 0)]

    # Triangle pour l'équipe 2 (en bas à droite)
        team_2_positions = [(self.grid_size - 1, self.grid_size - 1),
                        (self.grid_size - 1, self.grid_size - 2),
                        (self.grid_size - 2, self.grid_size - 1)]

    # Placer les unités de l'équipe 1
        for i, unit in enumerate(self.player_units):
            if i < len(team_1_positions):  # S'assurer qu'on ne dépasse pas la taille du triangle
                x, y = team_1_positions[i]
                unit.x, unit.y = x, y

    # Placer les unités de l'équipe 2
        for i, unit in enumerate(self.enemy_units):
            if i < len(team_2_positions):  # S'assurer qu'on ne dépasse pas la taille du triangle
                x, y = team_2_positions[i]
                unit.x, unit.y = x, y

    
    def treasure_animation(self, x, y):
        # Charger la police pour le texte
        font = pygame.font.Font("images/police.ttf", 72)  # Police pixel art avec taille 72


        for i in range(30):  # Répéter l'effet 
            self.flip_display()  # Réinitialiser l'affichage pour éviter d'écraser la grille

            # Calculer le rayon des cercles pour l'effet
            radius = i * 10  # Le rayon augmente à chaque itération
            alpha = max(255 - (i * 12),0) # Réduire l'opacité

           # Créer une surface temporaire avec transparence
            temp_surface = pygame.Surface((self.cell_size * 2, self.cell_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                temp_surface,
                (255, 223, 0, alpha),  # Couleur dorée avec transparence
                (self.cell_size, self.cell_size),  # Centre du cercle
                radius // 2
            )
           # Blit la surface temporaire sur l'écran principal
            self.screen.blit(temp_surface, (x * self.cell_size - self.cell_size // 2, y * self.cell_size - self.cell_size // 2))


         # Afficher un message rouge au centre de l'écran
            message = "Victoire !"
            text = font.render(message, True, (255, 0, 0))  # Rouge
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            self.screen.blit(text, text_rect)

        # Mettre à jour l'écran et ajouter un délai
            pygame.display.flip()
            pygame.time.delay(100)  # 100 ms entre chaque étape de l'animation

    
    def creation_random_team(self, team):
        unit_classes = [Explorateur, Archeologue, Chasseur]
        return [
            random.choice(unit_classes)(
                int(random.randint(0, self.grid_size - 1)),
                int(random.randint(0, self.grid_size - 1)),
                team
            )
            for _ in range(3)
        ]
    
    

    def genere_enigme(self): #génère une énigme 
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

    def handle_player_turn(self):
    """
        Gère le tour du joueur actif, permettant à chaque équipe (player et enemy) de sélectionner une unité et de jouer.
        """
        actuelle_units = self.player_units if self.debut_player == 1 else self.enemy_units
        ennemis = self.enemy_units if self.debut_player == 1 else self.player_units

        unite_selectionne = actuelle_units[self.selected_unit_index]
        if self.selected_position is None:
            self.selected_position = (unite_selectionne.x, unite_selectionne.y)

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
                        self.selected_unit_index = (self.selected_unit_index + 1) % len(actuelle_units)
                        unite_selectionne = actuelle_units[self.selected_unit_index]
                        self.selected_position = (unite_selectionne.x, unite_selectionne.y)
                        self.last_action_message = f"{unite_selectionne.name} est sélectionné."
                        break

                    if dx != 0 or dy != 0:
                        new_x = max(0, min(self.grid_size - 1, self.selected_position[0] + dx))
                        new_y = max(0, min(self.grid_size - 1, self.selected_position[1] + dy))
                        accessible_positions = get_accessible_positions(unite_selectionne, self.grid_size)
                        if (new_x, new_y) in accessible_positions:
                            self.selected_position = (new_x, new_y)

                    if event.key == pygame.K_SPACE:
                        accessible_positions = get_accessible_positions(unite_selectionne, self.grid_size)
                        if self.selected_position in accessible_positions:
                            unite_selectionne.x, unite_selectionne.y = self.selected_position
                            case = self.grid[unite_selectionne.y][unite_selectionne.x]
                            self.last_action_message = case.effet_case(unite_selectionne)
                            print(self.last_action_message)
                            has_acted = True
                        else:
                            print("Déplacement non valide.")

                    # Appeler une compétence
                    if event.key == pygame.K_r and isinstance(unite_selectionne, Explorateur):  # Coup rapide
                        cibles = unite_selectionne.get_cibles_accessibles(ennemis, self.grid_size)
                        if cibles:
                            cible = cibles[0]
                            competence = unite_selectionne.competences[0]
                            competence.utiliser(unite_selectionne, cible, self)
                            has_acted = True

                    elif event.key == pygame.K_t and isinstance(unite_selectionne, Archeologue):  # Attaque ciblée
                        cibles = unite_selectionne.get_cibles_accessibles(ennemis, self.grid_size)
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
                        cibles = unite_selectionne.get_cibles_accessibles(ennemis, self.grid_size)
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

                    # Vérifier si l'unité doit être supprimée
                        self.check_et_supp_unit(unite_selectionne)  

                    # Vérifier si le jeu est terminé après l'action
                        if self.fin_de_jeu():
                            return  # Arrêter le tour si le jeu est terminé
                    
                    
                    has_acted = True
    # Alterner le joueur actif
        if has_acted:
            self.selected_position = None
            self.selected_unit_index = 0
            self.debut_player = 2 if self.debut_player == 1 else 1
            print(f"Tour de l'équipe {'Player' if self.debut_player == 1 else 'Enemy'}.")


    def fin_de_jeu(self):
    # Vérifier si une équipe a trouvé le trésor
        for unit in self.player_units + self.enemy_units:
            if self.grid[unit.y][unit.x].type == "trésor":
                winner = "Player" if unit in self.player_units else "Enemy"
                print(f"Victoire : {winner} a trouvé le trésor !")
                return True  # Fin de jeu confirmée

    # Vérifier si une équipe a perdu toutes ses unités
        if all(unit.health <= 0 for unit in self.player_units):
            print("Victoire : l'ennemi a gagné car toutes les unités du joueur sont KO !")
            return True
        if all(unit.health <= 0 for unit in self.enemy_units):
            print("Victoire : le joueur a gagné car toutes les unités ennemies sont KO !")
            return True

    # Sinon, le jeu continue
        return False
    
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

    def draw_health_bar(self, unit, color):
        """
        Dessine une barre de vie au-dessus de l'unité.
        :param unit: L'unité pour laquelle dessiner la barre de vie.
        :param color: La couleur de la barre de vie (verte ou rouge).
        """
        # Calculer les dimensions de la barre de vie
        largeur_barre = self.cell_size
        hauteur_barre = 5
        health_ratio = unit.health / 100  # Supposons que 100 est le maximum de PV

        # Position de la barre (juste au-dessus de l'unité)
        barre_x = unit.x * self.cell_size
        barre_y = unit.y * self.cell_size - hauteur_barre - 2  # 2 pixels d'écart

        # Dessiner l'arrière-plan de la barre (grise)
        pygame.draw.rect(self.screen, (50, 50, 50), (barre_x, barre_y, largeur_barre, hauteur_barre))

        # Dessiner la barre de vie (colorée)
        pygame.draw.rect(self.screen, color, (barre_x, barre_y, largeur_barre * health_ratio, hauteur_barre))


    def draw_units(self):
        """
        Dessine toutes les unités et leurs barres de vie.
         """
        for unit in self.player_units:
            self.screen.blit(unit.image, (unit.x * self.cell_size, unit.y * self.cell_size))
            self.draw_health_bar(unit, (0, 255, 0))  # Barre de vie verte
            

        for unit in self.enemy_units:
            # Dessiner uniquement les unités qui ont encore des PV
            self.screen.blit(unit.image, (unit.x * self.cell_size, unit.y * self.cell_size))
            self.draw_health_bar(unit, (255, 0, 0))  # Barre de vie rouge
            
    def check_et_supp_unit(self, unit):

        if unit.health <= 0:
            unit_list = self.player_units if unit.team == "player" else self.enemy_units
            if unit in unit_list:
            # Supprimer l'unité de la liste
                unit_list.remove(unit)
                #self.draw_elimination_effect(unit)  # Afficher l'effet d'élimination
            print(f"{unit.name} a été éliminé et a disparu de la carte.")
        self.flip_display()  # Rafraîchir l'écran immédiatement


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

        # Section des énigmes
        if self.choix_enigme:
            enigme_text = self.choix_enigme["question"].split("\n")
            y_offset += 50  # Ajuster la position verticale pour les énigmes
            for line in enigme_text:
                line_rendered = font_medium.render(line, True, (255, 255, 255))
                self.screen.blit(line_rendered, (GRID_WIDTH + 20, y_offset))
                y_offset += 30  # Espacement entre les lignes
    def draw_accessible_areas_with_selection(self, unit, selected_position):
        """
        Dessine la zone accessible en transparence par-dessus la grille,
        tout en mettant en évidence la position temporaire.
        """
        # Créer une surface transparente pour la superposition
        overlay = pygame.Surface((self.grid_size * self.cell_size, self.grid_size * self.cell_size), pygame.SRCALPHA)

        # Définir les couleurs avec transparence
        accessible_color = (173, 216, 230, 100)  # Bleu clair transparent
        selected_color = (0, 255, 0, 150)  # Vert plus opaque pour la position temporaire

        # Déterminer la portée de déplacement de l'unité
        x, y = unit.x, unit.y
        max_range = 1 if isinstance(unit, (Archeologue, Chasseur)) else 2

        for dx in range(-max_range, max_range + 1):
            for dy in range(-max_range, max_range + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size and abs(dx) + abs(dy) <= max_range:
                    # Dessiner la zone accessible en bleu clair transparent
                    rect = (nx * self.cell_size, ny * self.cell_size, self.cell_size, self.cell_size)
                    pygame.draw.rect(overlay, accessible_color, rect)

                    # Si c'est la position temporaire, dessiner en vert transparent par-dessus
                    if selected_position == (nx, ny):
                        pygame.draw.rect(overlay, selected_color, rect)

        # Dessiner l'overlay sur l'écran
        self.screen.blit(overlay, (0, 0))
    def afficher_effet_attaque(self, cible, degats):
        """
        Affiche un effet visuel pour une attaque classique.
        """
        font = pygame.font.Font(None, 36)
        degats_text = font.render(f"-{degats}", True, (255, 0, 0))
        text_rect = degats_text.get_rect(center=(cible.x * self.cell_size + self.cell_size // 2,
                                                cible.y * self.cell_size + self.cell_size // 2))

        flash_duration = 500
        start_time = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_time < flash_duration:
            self.flip_display()
            pygame.draw.rect(
                self.screen,
                (255, 0, 0),
                (cible.x * self.cell_size, cible.y * self.cell_size, self.cell_size, self.cell_size),
                5
            )
            self.screen.blit(degats_text, text_rect)
            pygame.display.flip()

    def afficher_effet_tir_distance(self, attaquant, cible):
        """
        Affiche un effet visuel simulant un tir à distance.
        """
        start_x = attaquant.x * self.cell_size + self.cell_size // 2
        start_y = attaquant.y * self.cell_size + self.cell_size // 2
        end_x = cible.x * self.cell_size + self.cell_size // 2
        end_y = cible.y * self.cell_size + self.cell_size // 2

        projectile_color = (255, 165, 0)  # Orange pour représenter le tir
        projectile_radius = 5
        steps = 20

        for step in range(steps + 1):
            t = step / steps
            current_x = int(start_x + t * (end_x - start_x))
            current_y = int(start_y + t * (end_y - start_y))

            self.flip_display()
            pygame.draw.circle(self.screen, projectile_color, (current_x, current_y), projectile_radius)
            pygame.display.flip()
            pygame.time.delay(50)

        flash_duration = 300
        start_time = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_time < flash_duration:
            pygame.draw.rect(
                self.screen,
                (255, 0, 0),
                (cible.x * self.cell_size, cible.y * self.cell_size, self.cell_size, self.cell_size),
                5
            )
            pygame.display.flip()

    def afficher_effet_coup_rapide(self, attaquant, cible):
        """
        Affiche un effet visuel simulant un coup rapide.
        """
        start_x = attaquant.x * self.cell_size + self.cell_size // 2
        start_y = attaquant.y * self.cell_size + self.cell_size // 2
        cible_x = cible.x * self.cell_size + self.cell_size // 2
        cible_y = cible.y * self.cell_size + self.cell_size // 2

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
    def afficher_effet_revelation(self, utilisateur):
        """
        Affiche un effet visuel pour révéler les cases dans la zone accessible de l'Explorateur,
        en mettant en évidence les cases contenant des pièges.
        """
        # Couleurs pour l'effet
        reveal_color = (173, 216, 230, 100)  # Bleu clair transparent pour la zone accessible
        piege_color = (255, 0, 0, 150)  # Rouge transparent pour les pièges détectés
        flash_duration = 500  # Durée du flash en millisecondes

        # Obtenir les positions accessibles
        accessible_positions = get_accessible_positions(utilisateur, self.grid_size)

        # Créer une surface transparente pour superposition
        overlay = pygame.Surface((self.grid_size * self.cell_size, self.grid_size * self.cell_size), pygame.SRCALPHA)

        # Dessiner les zones accessibles
        for pos in accessible_positions:
            x, y = pos
            if self.grid[y][x].type == "piège":
                pygame.draw.rect(
                    overlay,
                    piege_color,  # Rouge pour les pièges
                    (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                )
            else:
                pygame.draw.rect(
                    overlay,
                    reveal_color,  # Bleu clair pour les autres cases accessibles
                    (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
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
                        (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size),
                        3  # Épaisseur du contour
                    )
            pygame.display.flip()
            pygame.time.delay(50)  # Petite pause pour rendre l'effet fluide
 
    def afficher_effet_pose_piege(self, position):
        """
        Affiche un effet visuel pour la pose d'un piège sur une case.
        """
        x, y = position
        flash_duration = 500  # Durée de l'effet en millisecondes
        start_time = pygame.time.get_ticks()

        while pygame.time.get_ticks() - start_time < flash_duration:
            pygame.draw.rect(
                self.screen,
                (255, 140, 0),  # Orange pour indiquer un piège
                (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size),
                3  # Épaisseur du contour
            )
            pygame.display.flip()
            pygame.time.delay(50)

    
    def afficher_effet_brouillard(self, utilisateur):
        """
        Affiche un effet visuel pour le brouillard de guerre autour de l'utilisateur.
        """
        overlay = pygame.Surface((self.grid_size * self.cell_size, self.grid_size * self.cell_size), pygame.SRCALPHA)
        fog_color = (50, 50, 50, 150)  # Gris semi-transparent pour le brouillard

        # Appliquer le brouillard uniquement sur la zone accessible
        accessible_positions = get_accessible_positions(utilisateur, self.grid_size)

        for x, y in accessible_positions:
            pygame.draw.rect(
                overlay,
                fog_color,
                (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
            )

        self.screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(500)  # Pause pour que l'effet reste visible brièvement
    def afficher_effet_analyse(self, utilisateur):
        """
        Affiche un effet visuel captivant pour l'analyse de l'environnement dans la zone accessible,
        avec un flash d'agrandissement pour les cases spéciales (indices et ressources).
        """
        # Obtenir les positions accessibles
        accessible_positions = get_accessible_positions(utilisateur, self.grid_size)
        
        # Couleurs lumineuses pour les cases spéciales
        colors = {
            "indice": (0, 255, 255),  # Cyan lumineux pour les indices
            "ressource": (0, 255, 0),  # Vert clair lumineux pour les ressources
            "autre": (100, 100, 100)  # Gris pour les autres cases accessibles
        }

        # Nombre d'étapes pour l'animation
        flash_steps = 10
        max_radius = self.cell_size // 2  # Taille maximum pour le flash

        # Pour chaque étape de l'animation
        for step in range(flash_steps):
            self.flip_display()  # Redessiner l'écran sans effacer l'effet
            for x, y in accessible_positions:
                case_type = self.grid[y][x].type
                color = colors.get(case_type, colors["autre"])
                
                # Calculer le rayon du cercle (agrandissement progressif)
                radius = int((step + 1) / flash_steps * max_radius)
                center = (x * self.cell_size + self.cell_size // 2, y * self.cell_size + self.cell_size // 2)

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
        overlay = pygame.Surface((self.grid_size * self.cell_size, self.grid_size * self.cell_size), pygame.SRCALPHA)
        for x, y in accessible_positions:
            case_type = self.grid[y][x].type
            color = (*colors.get(case_type, colors["autre"]), 100)  # Ajouter transparence
            pygame.draw.rect(
                overlay,
                color,
                (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
            )

        self.screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(500)  # Pause finale pour que l'effet reste visible



    
    def afficher_effet_decrypter_indice(self, utilisateur):
        """
        Affiche un effet visuel pour le décryptage d'un indice.
        """
        # Définir les couleurs et durées pour l'effet visuel
        highlight_color = (0, 255, 0)  # Vert pour indiquer le succès du décryptage
        flash_duration = 500  # Durée en millisecondes

        # Obtenir la position de l'utilisateur
        x, y = utilisateur.x, utilisateur.y

        start_time = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_time < flash_duration:
            pygame.draw.rect(
                self.screen,
                highlight_color,
                (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size),
                3  # Épaisseur de la bordure
            )
            pygame.display.flip()
            pygame.time.delay(50)  # Petite pause pour rendre l'effet visible



    def draw_door_locked_effect(self, x, y):
        rect_x = x * self.cell_size
        rect_y = y * self.cell_size
        rect_size = self.cell_size

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


    
    def explosion_animation(self, x, y):
    # Couleurs de l'explosion (Rouge -> Orange -> Jaune -> Disparaît)
        explosion_colors = [(255, 0, 0), (255, 69, 0), (255, 140, 0), (255, 255, 0)]

    # Centre de l'explosion
        center_x = x * self.cell_size + self.cell_size // 2
        center_y = y * self.cell_size + self.cell_size // 2

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
                    width=5 - i  # Les cercles extérieurs sont plus fins
            )

        # Mettre à jour l'écran
        pygame.display.flip()
        pygame.time.delay(50)  # Pause entre chaque étape

    def flip_display(self):
        self.screen.fill((0, 0, 0))
        self.draw_grid()
        
        # Dessiner les zones accessibles pour l'unité active
        active_units = self.player_units if self.debut_player == 1 else self.enemy_units
        self.draw_accessible_areas_with_selection(
            active_units[self.selected_unit_index],
            self.selected_position
        )
        self.draw_units()
        self.draw_ui()
        pygame.display.flip()
