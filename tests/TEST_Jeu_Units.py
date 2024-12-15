import pygame

pygame.init()
#================================================
# Paramétres / constantes :
#================================================
BLACK = (0, 0, 0)

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





def get_accessible_positions(unit, GRID_COLUMNS, GRID_ROWS):
    x, y = unit.x, unit.y

    # Définir la portée de déplacement selon le type d'unité
    max_range = getattr(unit, "max_range", 1)  # Par défaut, 1 case de portée

    accessible_positions = []

    # Parcourir toutes les cases accessibles dans les limites définies
    for dx in range(-max_range, max_range + 1):
        for dy in range(-max_range, max_range + 1):
            nx, ny = x + dx, y + dy
            # Vérifiez les limites de la grille
            if 0 <= nx < GRID_COLUMNS and 0 <= ny < GRID_ROWS:
                # Vérifiez la distance de Manhattan
                if abs(dx) + abs(dy) <= max_range:
                    accessible_positions.append((nx, ny))

    return accessible_positions



class Competence:
    def __init__(self, nom, multiplicateur, portee, effet=None):
     
        self.nom = nom
        self.multiplicateur = multiplicateur
        self.portee = portee
        self.effet = effet

    def utiliser(self, utilisateur, cible, game): 
        
        accessible_positions = get_accessible_positions(utilisateur, GRID_COLUMNS, GRID_ROWS)
        
        
        #Si aucune cible n'est spécifiée, appliquer un effet global (par exemple pour "Révéler zone" ou "Brouillard de guerre")
        if cible is None:
           if self.effet:  # Vérifie si la compétence a un effet global
               self.effet(utilisateur, game)  # Appel à l'effet
           return

        # Vérifier que la cible est dans la portée
        if (cible.x, cible.y) not in accessible_positions:
            print(f"{cible.name} est hors de portée de {self.nom}.")
            return

        # Vérifier que la cible appartient à l'équipe adverse
        if cible.team == utilisateur.team:
            print(f"{cible.name} est un allié, attaque impossible.")
            return

        # Appliquer les dégâts
        degats = utilisateur.calculer_degats(cible, self.multiplicateur)
        cible.health -= degats

        # Afficher les effets visuels en fonction du type de compétence
        if self.nom == "Coup rapide":
            game.afficher_effet_coup_rapide(utilisateur, cible)
        elif self.nom == "Tir à distance":
            game.afficher_effet_tir_distance(utilisateur, cible)
        else:
            game.afficher_effet_attaque(cible, degats)

        # Appliquer un effet secondaire s'il y en a un
        if self.effet:
            self.effet(utilisateur, cible)

        # Vérifier si la cible est vaincue
        if cible.health <= 0:
            cible.mourir(game)
            print(f"{cible.name} a été vaincu !")

#================================================
# Définition de la classe pour les personnages :
#================================================

class Unit:
   
    def __init__(self, x, y, image_path, name,team):
        self.x = x
        self.y = y
        self.image = pygame.image.load(image_path)  # Charger l'image
        self.image = pygame.transform.scale(self.image, (85, 85))  # Redimensionner si nécessaire
        self.name = name
        self.health = 100
        self.defense = 10
        self.attack_power = 20
        self.team=team
        self.is_active=True #Par défaut, l'unité est jouable 
        self.has_key=False # Par défaut l'unité n'a pas de clé 
    
    
    
    
    def draw(self, screen, MARGIN_X, MARGIN_Y, CELL_SIZE):
        
        screen.blit(self.image, (
            self.x * CELL_SIZE + MARGIN_X,
            self.y * CELL_SIZE + MARGIN_Y
        ))
        
    def calculer_degats(self, cible, multiplicateur=1):
        attaque = self.attack_power * multiplicateur
        bonus_vitesse = self.speed * 2
        degats = max(0, (attaque + bonus_vitesse) - cible.defense)  # Minimum de 0 dégâts
        return degats  # Retourne les dégâts sans modifier les PV


    def attaquer(self, cible, multiplicateur=1):
        
        degats = self.calculer_degats(cible, multiplicateur)
        cible.health -= degats
        print(f"{self.name} inflige {degats} dégâts à {cible.name} !")
        if cible.health <= 0:
            cible.mourir(game)
            print(f"{cible.name} a été vaincu !")
    
    
    def get_cibles_accessibles(self, other_units, grid_columns, grid_rows, offset_x=0, offset_y=0):
        
        # Obtenez les positions accessibles en fonction de la portée de l'unité
        accessible_positions = get_accessible_positions(self, grid_columns, grid_rows)

        # Filtrer les cibles ennemies situées dans les positions accessibles
        cibles = [
            unit for unit in other_units
            if (unit.x, unit.y) in accessible_positions
            and unit.is_active  # La cible doit être active
            and unit.team != self.team  # La cible doit être une ennemie
        ]

        return cibles
    
    def mourir(self, game):
        self.is_active = False  # Marquer l'unité comme inactive
        game.add_message(f"{self.name} est mort et ne peut plus jouer.")
        game.explosion_animation(self.x, self.y)  # Animation de mort
        
        # Mise à jour : Retirer temporairement cette unité des affichages
        game.selected_position = None
        game.selected_unit_index = -1
        

#=====================================  
# Compétence de L'Explorateur :
#=====================================  
    
class Explorateur(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y,"images/explorateur.png" , "explorateur" ,team)
        self.attack_power = 10
        self.defense = 10
        self.speed = 5
        self.max_range = 2  # Portée de déplacement pour l'explorateur
        self.name="Explorateur"
        # Charger l'image et redimensionner
        self.image = pygame.image.load("images/explorateur.png")  # Charger l'image
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))  # redimenssionner

        # Ajouter les compétences
        self.competences = [
            Competence(
                nom="Coup rapide",
                multiplicateur=0.8,
                portee=2
            ),
            Competence(
                nom="Révéler zone",
                multiplicateur=0,  # Pas de dégâts
                portee=3,
                effet=self.reveler_zone
            ),
            Competence(
                nom="Détection de piège",
                multiplicateur=0,
                portee=3,
                effet=self.detecter_piege
            )
        ]

    def reveler_zone(self, utilisateur, game):
        
        for x, y in get_accessible_positions(utilisateur, GRID_COLUMNS, GRID_ROWS):
            game.grid[y][x].hidden = False  # Lever le brouillard de guerre
            print(f"Case ({x}, {y}) révélée.")
        game.afficher_effet_revelation(utilisateur)

    def detecter_piege(self, utilisateur, game):
        
        for x, y in get_accessible_positions(utilisateur, GRID_COLUMNS, GRID_ROWS):
            if game.grid[y][x].type == "piège":
                game.grid[y][x].hidden = False
                print(f"Piège détecté à la position ({x}, {y}).")
            
        game.afficher_effet_detection_piege(utilisateur, MARGIN_X, MARGIN_Y)
    

#=====================================
#   Compétence de l'Archeologue :
#=====================================   

class Archeologue(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, "images/archeologue.png","Archéologue", team)
        self.attack_power = 15
        self.defense = 15
        self.speed = 2
        self.name="Archeologue"
        
        self.image = pygame.image.load("images/archeologue.png")  # Charger l'image
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))  # redimenssionner
        self.enigme_non_resolue=False #énigme en attente de réponse       


        # Ajouter les compétences
        self.competences = [
            Competence(
                nom="Attaque ciblée",
                multiplicateur=1.5,
                portee=1
            ),
            Competence(
                nom="Décrypter indice",
                multiplicateur=0,
                portee=1,
                effet=self.decrypter_indice
            ),
            Competence(
                nom="Analyse de l'environnement",
                multiplicateur=0,
                portee=2,
                effet=self.analyse_environnement  # Lien avec la méthode à définir
            )
        ]

    def decrypter_indice(self, utilisateur, game):
        
        for x, y in get_accessible_positions(utilisateur, GRID_COLUMNS, GRID_ROWS):
            if game.grid[y][x].type == "indice":
                game.grid[y][x].type = "normale"
                print(f"{utilisateur.name} a décrypté l'indice à ({x}, {y}).")
        
        game.afficher_effet_decrypter_indice(utilisateur, MARGIN_X, MARGIN_Y)

    def analyse_environnement(self, utilisateur, game):
        
        for x, y in get_accessible_positions(utilisateur, GRID_COLUMNS, GRID_ROWS):
            if game.grid[y][x].type in ["ressource", "indice"]:
                game.grid[y][x].hidden = False
                print(f"{utilisateur.name} a détecté une case spéciale à ({x}, {y}).")
        game.afficher_effet_analyse(utilisateur)


#=====================================
#   Compétence du Chasseur :
#=====================================   

class Chasseur(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, "images/chasseur_2.png", "Chasseur", team)
        self.attack_power = 17
        self.defense = 15
        self.speed = 2
        self.name="Chasseur" 
        
        self.image = pygame.image.load("images/chasseur_2.png")  # Charger l'image
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE))  
        
        # Ajouter les compétences
        self.competences = [
            Competence(
                nom="Tir à distance",
                multiplicateur=1.2,
                portee=2
            ),
            Competence(
                nom="Pose de piège",
                multiplicateur=0,
                portee=1,
                effet=self.poser_piege
            ),
            Competence(
                nom="Brouillard de guerre",
                multiplicateur=0,
                portee=3,
                effet=self.brouillard_de_guerre
            )
        ]

    def poser_piege(self, utilisateur, game):
        # Vérifiez que la position sélectionnée est accessible
        selected_position = game.selected_position
        accessible_positions = get_accessible_positions(utilisateur, GRID_COLUMNS, GRID_ROWS)

        if selected_position in accessible_positions:
            x, y = selected_position
            if game.grid[y][x].type == "normale":  # Vérifiez que la case est normale
                # Modifier le type de la case
                game.grid[y][x].type = "piège"
                
                game.add_message(f"{utilisateur.name} pose un piège sur la case ({x}, {y}).")
                print(f"{utilisateur.name} pose un piège sur la case ({x}, {y}).")
                
                # Charger et ajuster l'image du piège avec CELL_SIZE
                game.tile_images["piège"] = pygame.image.load("images/case_piege2.png")
                game.tile_images["piège"] = pygame.transform.scale(
                    game.tile_images["piège"], (CELL_SIZE, CELL_SIZE)
                )

                # Afficher l'effet visuel
                game.afficher_effet_pose_piege((x, y))
            else:
                game.add_message("La case sélectionnée n'est pas normale, impossible de poser un piège.")
                print("La case sélectionnée n'est pas normale, impossible de poser un piège.")
        else:
            game.add_message("La position sélectionnée est hors de portée.")
            print("La position sélectionnée est hors de portée.")


    def brouillard_de_guerre(self, utilisateur, game):
    
        # Identifier l'équipe adverse
        equipe_adverse = game.enemy_units if utilisateur.team == "player" else game.player_units
        nouvelles_positions = []  # Liste pour stocker les nouvelles positions des ennemis
        for adversaire in equipe_adverse:
            # Calculer la direction principale pour reculer (gauche/droite ou haut/bas)
            dx = adversaire.x - utilisateur.x
            dy = adversaire.y - utilisateur.y

            # Par défaut, la direction de recul sera basée sur la position relative
            if abs(dx) >= abs(dy):  # Privilégier un recul horizontal
                recul_x = adversaire.x + (2 if dx > 0 else -2)
                recul_y = adversaire.y
            else:  # Privilégier un recul vertical
                recul_x = adversaire.x
                recul_y = adversaire.y + (2 if dy > 0 else -2)

            # Si le recul sort des limites, ajuster pour rester dans la grille
            recul_x = max(0, min(GRID_COLUMNS - 1, recul_x))
            recul_y = max(0, min(GRID_ROWS - 1, recul_y))

            # Appliquer le recul si la case cible est libre ou forcer le déplacement
            adversaire.x, adversaire.y = recul_x, recul_y
            game.add_message(f"{adversaire.name} a reculé à la position ({recul_x}, {recul_y}).")
            print(f"{adversaire.name} a reculé à la position ({recul_x}, {recul_y}).")

        # Ajouter un effet visuel pour le brouillard
        game.afficher_effet_brouillard(utilisateur)

        if nouvelles_positions:
            game.add_message(f"{utilisateur.name} a forcé les unités adverses à reculer : {nouvelles_positions}")
            print(f"{utilisateur.name} a forcé les unités adverses à reculer : {nouvelles_positions}")

        # Retourner les nouvelles positions des unités affectées
        return nouvelles_positions
    
