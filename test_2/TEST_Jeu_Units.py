
import pygame
#================================================
# Paramétres / constantes :
#================================================
BLACK = (0, 0, 0)

def get_accessible_positions(unit, grid_size):
    """Retourne une liste des positions accessibles en fonction du type d'unité."""
    x, y = unit.x, unit.y

    # Définir la portée de déplacement selon le type d'unité
    if hasattr(unit, "max_range"):
        max_range = unit.max_range
    else:
        max_range = 1  # Par défaut, 1 case

    accessible_positions = []

    # Parcourir toutes les cases accessibles dans les limites définies
    for dx in range(-max_range, max_range + 1):
        for dy in range(-max_range, max_range + 1):
            nx, ny = x + dx, y + dy
            # Vérifier que la case est dans les limites de la grille et respecte la distance de Manhattan
            if 0 <= nx < grid_size and 0 <= ny < grid_size and abs(dx) + abs(dy) <= max_range:
                accessible_positions.append((nx, ny))

    return accessible_positions

class Competence:
    def __init__(self, nom, multiplicateur, portee, effet=None):
        """
        Initialise une compétence.

        :param nom: Nom de la compétence.
        :param multiplicateur: Multiplicateur de dégâts.
        :param portee: Portée maximale de la compétence.
        :param effet: Fonction optionnelle appliquant un effet secondaire.
        """
        self.nom = nom
        self.multiplicateur = multiplicateur
        self.portee = portee
        self.effet = effet

    def utiliser(self, utilisateur, cible, game): 
        """
        Applique la compétence sur une cible, uniquement si elle est dans la zone accessible
        et appartient à l'équipe adverse. Si aucune cible n'est donnée, applique l'effet globalement.
        """
        accessible_positions = get_accessible_positions(utilisateur, game.grid_size)

        # Si aucune cible n'est spécifiée, appliquer un effet global (par exemple pour "Révéler zone" ou "Brouillard de guerre")
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
            print(f"{cible.name} a été vaincu !")

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
        self.attack_power = 20
        self.team=team
        self.is_active=True #Par défaut, l'unité est jouable 
        self.has_key=False # Par défaut l'unité n'a pas de clé 
        
    def draw(self, screen, cell_size):
        """Dessine l'unité sur l'écran."""
        screen.blit(self.image, (self.x * cell_size, self.y * cell_size))
        
    def calculer_degats(self, cible, multiplicateur=1):
        attaque = self.attack_power * multiplicateur
        bonus_vitesse = self.speed * 2
        degats = max(0, (attaque + bonus_vitesse) - cible.defense)  # Minimum de 0 dégâts
        return degats  # Retourne les dégâts sans modifier les PV


    def attaquer(self, cible, multiplicateur=1):
        """
        Attaque une cible et inflige des dégâts en fonction des statistiques.
        """
        degats = self.calculer_degats(cible, multiplicateur)
        cible.health -= degats
        print(f"{self.name} inflige {degats} dégâts à {cible.name} !")
        if cible.health <= 0:
            print(f"{cible.name} a été vaincu !")
    
    def get_cibles_accessibles(self, other_units, grid_size):
        """
        Retourne une liste des unités ennemies dans la zone accessible.
        """
        accessible_positions = get_accessible_positions(self, grid_size)

        # Filtrer uniquement les unités ennemies basées sur les positions accessibles
        cibles = [
            unit for unit in other_units
            if (unit.x, unit.y) in accessible_positions and unit.team != self.team
        ]
        return cibles

#================================================
# Définition de la classe pour les personnages :
#================================================
class Explorateur(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y,"images/explorateur.png" , team,"Explorateur")
        self.attack_power = 10
        self.defense = 10
        self.speed = 5
        self.name="Explorateur"
        # Charger l'image et redimensionner
        self.image = pygame.image.load("images/explorateur.png")  # Charger l'image
        self.image = pygame.transform.scale(self.image, (85, 70))  # redimenssionner

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
        """
        Révèle les cases dans la zone accessible autour de l'explorateur.
        """
        accessible_positions = get_accessible_positions(utilisateur, game.grid_size)

        for x, y in accessible_positions:
            game.grid[y][x].hidden = False  # Lever le brouillard de guerre sur ces cases
            print(f"Case ({x}, {y}) révélée.")

        # Optionnel : Ajouter un effet visuel pour la révélation
        game.afficher_effet_revelation(utilisateur)

    def detecter_piege(self, utilisateur, game):
        """
        Détecte et révèle les pièges dans la zone accessible de l'explorateur.
        """
        accessible_positions = get_accessible_positions(utilisateur, game.grid_size)

        for x, y in accessible_positions:
            if game.grid[y][x].type == "piège":
                game.grid[y][x].hidden = False  # Révéler le piège
                print(f"Piège détecté à la position ({x}, {y}).")

        # Optionnel : Ajouter un effet visuel pour la détection
        game.afficher_effet_detection_piege(utilisateur)

class Archeologue(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, "images/archeologue.png",team, "Archéologue")
        self.attack_power = 15
        self.defense = 15
        self.speed = 2
        self.name="Archeologue"
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
        """
        Décrypte les indices présents dans la zone accessible.
        """
        accessible_positions = get_accessible_positions(utilisateur, game.grid_size)

        for x, y in accessible_positions:
            if game.grid[y][x].type == "indice":
                game.grid[y][x].type = "normale"  # Convertir l'indice en case normale
                print(f"{utilisateur.name} a décrypté l'indice à ({x}, {y}).")

        # Afficher l'effet visuel de décryptage
        game.afficher_effet_decrypter_indice(utilisateur)

    def analyse_environnement(self, utilisateur, game):
        """
        Révèle les cases spéciales (ressources ou indices) uniquement dans la zone accessible.
        """
        # Obtenir les positions accessibles
        accessible_positions = get_accessible_positions(utilisateur, game.grid_size)

        # Révéler les cases spéciales dans la zone accessible
        for x, y in accessible_positions:
            if game.grid[y][x].type in ["ressource", "indice"]:
                game.grid[y][x].hidden = False  # Révéler la case
                print(f"{utilisateur.name} a détecté une case spéciale à ({x}, {y}).")

        # Afficher un effet visuel pour l'analyse
        game.afficher_effet_analyse(utilisateur)

class Chasseur(Unit):
    def __init__(self, x, y, team):
        super().__init__(x, y, "images/chasseur_2.png", team,"Chasseur")
        self.image = pygame.transform.scale(self.image, (100, 75))  # Redimensionner à 50x50 pixels
        self.name="Chasseur"    
        self.attack_power = 17
        self.defense = 15
        self.speed = 2

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
        """
        Pose un piège sur une case adjacente dans la zone accessible.
        """
        accessible_positions = get_accessible_positions(utilisateur, game.grid_size)
        for pos in accessible_positions:
            x, y = pos
            if game.grid[y][x].type == "normale":  # Vérifier que la case est normale
                game.grid[y][x].type = "piège"  # Modifier le type de la case
                print(f"{utilisateur.name} pose un piège sur la case ({x}, {y}).")
                game.tile_images["piège"] = pygame.image.load("images/case_piege2.png")  # Charger l'image du piège
                game.tile_images["piège"] = pygame.transform.scale(
                    game.tile_images["piège"], (game.cell_size, game.cell_size)
                )  # Ajuster la taille
                game.afficher_effet_pose_piege((x, y))  # Afficher l'effet visuel
                break  # Limiter à un piège par tour


    def brouillard_de_guerre(self, utilisateur, game):
        """
        Applique un brouillard de guerre sur les ennemis en les forçant à reculer de deux cases.
        """
        ennemis = game.enemy_units if utilisateur.team == "player" else game.player_units

        for ennemi in ennemis:
            # Reculer chaque ennemi de 2 cases, dans la direction opposée à l'Explorateur
            dx = ennemi.x - utilisateur.x
            dy = ennemi.y - utilisateur.y
            recul_x = ennemi.x + (2 if dx > 0 else -2 if dx < 0 else 0)
            recul_y = ennemi.y + (2 if dy > 0 else -2 if dy < 0 else 0)

            # Vérifier que le recul reste dans les limites de la grille
            if 0 <= recul_x < game.grid_size and 0 <= recul_y < game.grid_size:
                ennemi.x, ennemi.y = recul_x, recul_y
                print(f"{ennemi.name} a reculé à la position ({recul_x}, {recul_y}).")
        game.afficher_effet_brouillard(utilisateur)
