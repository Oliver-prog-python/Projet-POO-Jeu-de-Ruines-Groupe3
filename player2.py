import pygame

# Constantes
GRID_SIZE = 8
CELL_SIZE = 60
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

class Unit:
    """
    Classe de base pour représenter une unité.
    """
    def __init__(self, x, y, health, attack_power, defense, speed, team):
        self.x = x
        self.y = y
        self.health = health
        self.attack_power = attack_power
        self.defense = defense
        self.speed = speed
        self.team = team  # 'player' ou 'enemy'
        self.is_selected = False

    def move(self, dx, dy):
        """
        Déplace l'unité de dx, dy, en respectant les limites de la grille.
        """
        new_x = self.x + dx
        new_y = self.y + dy

        if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE:
            self.x = new_x
            self.y = new_y

    def attack(self, target):
        """
        Attaque une unité cible.
        """
        if abs(self.x - target.x) <= 1 and abs(self.y - target.y) <= 1:
            damage = max(0, self.attack_power - target.defense)
            target.health -= damage
            print(f"{self.__class__.__name__} inflige {damage} dégâts à {target.__class__.__name__}.")

    def draw(self, screen):
        """
        Dessine l'unité sur l'écran.
        """
        color = BLUE if self.team == 'player' else RED
        if self.is_selected:
            pygame.draw.rect(screen, GREEN, (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.draw.circle(screen, color, (self.x * CELL_SIZE + CELL_SIZE // 2, self.y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)


# Classe Aventurier
class Aventurier(Unit):
    """
    Classe pour représenter l'Aventurier.
    """
    def __init__(self, x, y, team='player'):
        super().__init__(x, y, health=80, attack_power=10, defense=10, speed=5, team=team)
        self.can_detect_traps = True  # Peut détecter les pièges

    def reveal_area(self, grid):
        """
        Révèle les cases autour de l'Aventurier (portée 2, zone 3x3).
        """
        print(f"{self.__class__.__name__} révèle les cases autour de lui.")
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                if 0 <= self.y + dy < GRID_SIZE and 0 <= self.x + dx < GRID_SIZE:
                    grid[self.y + dy][self.x + dx].is_visible = True

    def quick_attack(self, target):
        """
        Une attaque rapide infligeant des dégâts modérés (portée 1).
        """
        if abs(self.x - target.x) <= 1 and abs(self.y - target.y) <= 1:
            target.health -= 15
            print(f"{self.__class__.__name__} effectue un coup rapide et inflige 15 dégâts à {target.__class__.__name__}.")


# Classe Chasseur
class Chasseur(Unit):
    """
    Classe pour représenter le Chasseur.
    """
    def __init__(self, x, y, team='enemy'):
        super().__init__(x, y, health=120, attack_power=30, defense=20, speed=2, team=team)

    def ranged_attack(self, target):
        """
        Une attaque à distance infligeant des dégâts modérés (portée 3).
        """
        if abs(self.x - target.x) <= 3 and abs(self.y - target.y) <= 3:
            target.health -= 25
            print(f"{self.__class__.__name__} effectue une attaque à distance et inflige 25 dégâts à {target.__class__.__name__}.")

    def set_trap(self, grid):
        """
        Pose un piège sur la case actuelle.
        """
        print(f"{self.__class__.__name__} pose un piège sur sa position ({self.x}, {self.y}).")
        grid[self.y][self.x].case_type = "piège"

    def fog_of_war(self, players):
        """
        Crée un brouillard de guerre qui force tous les joueurs ennemis à revenir à leur position de départ.
        """
        print(f"{self.__class__.__name__} déclenche un brouillard de guerre !")
        for player in players:
            if player.team != self.team:  # Affecte uniquement les ennemis
                player.x = 0
                player.y = 0  # Retour à la case de départ


# Classe Archéologue
class Archeologue(Unit):
    """
    Classe pour représenter l'Archéologue.
    """
    def __init__(self, x, y, team='player'):
        super().__init__(x, y, health=100, attack_power=15, defense=10, speed=2, team=team)
        self.can_solve_puzzles = True  # Peut résoudre les énigmes
        self.can_detect_resources = True  # Peut détecter les ressources
        self.clues_collected = 0  # Nombre d'indices collectés

    def solve_puzzle(self):
        """
        Résout une énigme et collecte un indice.
        """
        print(f"{self.__class__.__name__} résout une énigme et collecte un indice.")
        self.clues_collected += 1

    def analyze_environment(self, grid):
        """
        Analyse les cases spéciales autour de l'Archéologue (portée 2, zone 3x3).
        """
        print(f"{self.__class__.__name__} analyse l'environnement autour de lui.")
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                if 0 <= self.y + dy < GRID_SIZE and 0 <= self.x + dx < GRID_SIZE:
                    cell = grid[self.y + dy][self.x + dx]
                    if cell.case_type in ["ressource", "énigme"]:
                        print(f"Case spéciale détectée en ({self.x + dx}, {self.y + dy}): {cell.case_type}")

    def targeted_attack(self, target):
        """
        Une attaque calculée qui ignore partiellement la défense ennemie.
        """
        if abs(self.x - target.x) <= 1 and abs(self.y - target.y) <= 1:
            damage = max(0, self.attack_power - (target.defense // 2))
            target.health -= damage
            print(f"{self.__class__.__name__} effectue une attaque ciblée et inflige {damage} dégâts à {target.__class__.__name__}.")


# Fonction de test pour afficher les unités
def test():
    pygame.init()
    screen = pygame.display.set_mode((GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE))
    screen.fill((255, 255, 255))

    aventurier = Aventurier(0, 0)
    chasseur = Chasseur(1, 1)
    archeologue = Archeologue(2, 2)

    players = [aventurier, chasseur, archeologue]

    running = True
    while running:
        screen.fill((255, 255, 255))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Dessiner les joueurs
        for player in players:
            player.draw(screen)

        pygame.display.flip()


if __name__ == "__main__":
    test()

