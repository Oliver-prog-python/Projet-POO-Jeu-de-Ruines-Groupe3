import pygame
from TEST_Jeu_Units import Explorateur, Archeologue, Chasseur

# Initialiser pygame et la grille
pygame.init()

# Dimensions
WIDTH, HEIGHT = 1300, 800  # Plus large pour inclure la zone des boutons
GRID_WIDTH = 800  # Largeur de la grille
UI_WIDTH = WIDTH - GRID_WIDTH  # Largeur de la zone UI
CELL_SIZE = GRID_WIDTH // 10


# Initialiser l'écran
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jeu des Ruines")

# Classe Case
class Case:
    """Classe pour représenter une case sur la grille."""
    def __init__(self, type_case="normale"):
        self.type = type_case
        self.hidden = False

# Créer une grille de test
def creer_grille_test():
    grid = [[Case() for _ in range(10)] for _ in range(10)]
    grid[2][2].type = "piège"
    grid[5][5].type = "indice"
    return grid

# Dessiner la grille
def draw_grid(grid, screen):
    for x, row in enumerate(grid):
        for y, case in enumerate(row):
            color = (200, 200, 200) if case.hidden else (255, 255, 255)
            pygame.draw.rect(
                screen,
                color,
                (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                1
            )
def draw_unit_with_selection(unit, screen, cell_size, is_selected):
    """Dessine une unité avec une bordure si elle est sélectionnée."""
    if is_selected:
        # Dessiner une bordure jaune autour de l'unité
        pygame.draw.rect(
            screen,
            (255, 255, 0),  # Jaune
            (
                unit.x * cell_size,  # Position x
                unit.y * cell_size,  # Position y
                cell_size,  # Largeur
                cell_size   # Hauteur
            ),
            3  # Épaisseur de la bordure
        )
    # Dessiner l'unité
    unit.draw(screen, cell_size)
    
def draw_ui(screen, selected_unit, last_action_message):
    pygame.draw.rect(screen, (50, 50, 50), (GRID_WIDTH, 0, UI_WIDTH, HEIGHT))
    
    # Fontes pour le texte
    font_small = pygame.font.Font(None, 24)
    font_medium = pygame.font.Font(None, 28)
    font_large = pygame.font.Font(None, 36)
    font_title = pygame.font.Font(None, 40)
    
    y_offset = 20  # Position de départ verticale pour les commandes
    
    #Section 1 : Touche de commandes :
    title_commands = font_title.render("Touches de commandes :", True, (255, 255, 255))
    screen.blit(title_commands, (GRID_WIDTH + 20, y_offset))
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
        screen.blit(line, (GRID_WIDTH + 20, y_offset))
        y_offset += 25  # Espacement entre les commandes

    # Pour separer la section control et la section informations (Mieux visuellement)
    y_offset += 20
    pygame.draw.line(screen, (255, 255, 255), (GRID_WIDTH + 10, y_offset), (WIDTH - 10, y_offset), 2)
    y_offset += 20
    
    #Section 2 : Infos sur l'unité :
    title_unit_info = font_title.render("Informations sur l'unité :", True, (255, 255, 255))
    screen.blit(title_unit_info, (GRID_WIDTH + 20, y_offset))
    y_offset += 50 
    # Informations sur l'unité sélectionnée
    unit_info = [
        f"Unité : {selected_unit.name}",
        f"PV : {selected_unit.health}",
        f"Défense : {selected_unit.defense}",
        f"Position : ({selected_unit.x}, {selected_unit.y})"
    ]
    for info in unit_info:
        line = font_medium.render(info, True, (255, 255, 0))
        screen.blit(line, (GRID_WIDTH + 20, y_offset))
        y_offset += 35  # Espacement entre les infos

    # Pour separer la section Informations et Action realiser par une unité
    y_offset += 20
    pygame.draw.line(screen, (255, 255, 255), (GRID_WIDTH + 10, y_offset), (WIDTH - 10, y_offset), 2)
    y_offset += 20
    
    # Section 3 :  Action fait par l'unité :
    title_action = font_title.render("Dernière action :", True, (255, 255, 255))
    screen.blit(title_action, (GRID_WIDTH + 20, y_offset))
    y_offset += 50  # Espacement après le titre
    # Section 3 : Dernière action
    action_message = font_large.render(f"Action : {last_action_message}", True, (255, 255, 255))
    screen.blit(action_message, (GRID_WIDTH + 20, y_offset))

def draw_accessible_areas_with_selection(unit, screen, cell_size, selected_position):
    """Dessine les zones accessibles et surligne la position sélectionnée."""
    x, y = unit.x, unit.y

    # Définir la portée de déplacement selon le type d'unité
    if isinstance(unit, Archeologue) or isinstance(unit, Chasseur):
        max_range = 1
    elif isinstance(unit, Explorateur):
        max_range = 2
    else:
        max_range = 0

    for dx in range(-max_range, max_range + 1):
        for dy in range(-max_range, max_range + 1):
            nx, ny = x + dx, y + dy

            # Vérifier que la case est dans la grille et respecte la distance de Manhattan
            if 0 <= nx < 10 and 0 <= ny < 10 and abs(dx) + abs(dy) <= max_range:
                # Remplir l'intérieur de la case
                color = (173, 216, 230)  # Bleu pâle pour les zones accessibles
                if selected_position == (nx, ny):
                    color = (0, 255, 0)  # Vert pour la position sélectionnée
                pygame.draw.rect(
                    screen,
                    color,
                    (nx * cell_size, ny * cell_size, cell_size, cell_size),
                    0  # Remplissage complet
                )

                # Dessiner les contours de la case pour rendre les traits visibles
                pygame.draw.rect(
                    screen,
                    (0, 0, 0),  # Noir pour les contours
                    (nx * cell_size, ny * cell_size, cell_size, cell_size),
                    1  # Épaisseur de la ligne de contour
                )

def get_accessible_positions(unit, grid_size):
    """Retourne une liste des positions accessibles en fonction du type d'unité."""
    x, y = unit.x, unit.y

    # Définir la portée de déplacement selon le type d'unité
    if isinstance(unit, Archeologue) or isinstance(unit, Chasseur):
        max_range = 1  # 1 case dans les 4 directions
    elif isinstance(unit, Explorateur):
        max_range = 2  # 2 cases dans les 4 directions
    else:
        max_range = 0  # Par défaut, aucune zone

    accessible_positions = []

    # Parcourir toutes les cases accessibles dans les limites définies
    for dx in range(-max_range, max_range + 1):
        for dy in range(-max_range, max_range + 1):
            nx, ny = x + dx, y + dy
            # Vérifier que la case est dans les limites de la grille et respecte la distance de Manhattan
            if 0 <= nx < grid_size and 0 <= ny < grid_size and abs(dx) + abs(dy) <= max_range:
                accessible_positions.append((nx, ny))

    return accessible_positions


# Boucle principale
def main():
    running = True
    clock = pygame.time.Clock()
    grid = creer_grille_test()

    # Initialiser des unités
    explorateur = Explorateur(4, 4)
    archeologue = Archeologue(5, 5)
    chasseur = Chasseur(6, 6)
    units = [explorateur, archeologue, chasseur]

    # Variable pour suivre l'unité sélectionnée
    selected_unit_index = 0  # Indice de l'unité sélectionnée (commence par Explorateur)
    selected_position = None  # Position en cours de sélection
    turn_done = False  # Indique si l'unité a terminé son tour

    global last_action_message
    last_action_message = "Aucune action effectuée."  # Message par défaut
    
    while running:
        screen.fill((0, 0, 0))  # Remplir l'écran avec du noir
        draw_grid(grid, screen)  # Dessiner la grille
        # 2. Dessiner les cases accessibles pour l'unité sélectionnée
        draw_accessible_areas_with_selection(units[selected_unit_index], screen, CELL_SIZE,selected_position)

        # Dessiner toutes les unités avec leur sélection
        for i, unit in enumerate(units):
            is_selected = (i == selected_unit_index)
            draw_unit_with_selection(unit, screen, CELL_SIZE, is_selected)
        # Dessiner l'interface utilisateur
        draw_ui(screen, units[selected_unit_index], last_action_message)
        # Dessiner toutes les unités avec leur sélection
        for i, unit in enumerate(units):
            is_selected = (i == selected_unit_index)
            draw_unit_with_selection(unit, screen, CELL_SIZE, is_selected)

        
        # Gérer les événements et actualiser l'écran
        """for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:  # Changer d'unité
                    selected_unit_index = (selected_unit_index + 1) % len(units)
                    print(f"Unité sélectionnée : {units[selected_unit_index].name}")
                
                # Déplacement de l'unité selectionnée
                elif event.key == pygame.K_UP and units[selected_unit_index].y > 0:
                    units[selected_unit_index].y -= 1
                elif event.key == pygame.K_DOWN and units[selected_unit_index].y < 9:
                    units[selected_unit_index].y += 1
                elif event.key == pygame.K_LEFT and units[selected_unit_index].x > 0:
                    units[selected_unit_index].x -= 1
                elif event.key == pygame.K_RIGHT and units[selected_unit_index].x < 9:
                    units[selected_unit_index].x += 1"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if not turn_done:  # Si le tour n'est pas terminé
                    accessible_positions = get_accessible_positions(units[selected_unit_index], 10)

                    # Initialiser la position sélectionnée si ce n'est pas déjà fait
                    if selected_position is None:
                        selected_position = (units[selected_unit_index].x, units[selected_unit_index].y)

                    # Navigation dans les zones accessibles
                    current_x, current_y = selected_position
                    if event.key == pygame.K_UP:
                        next_position = (current_x, current_y - 1)
                    elif event.key == pygame.K_DOWN:
                        next_position = (current_x, current_y + 1)
                    elif event.key == pygame.K_LEFT:
                        next_position = (current_x - 1, current_y)
                    elif event.key == pygame.K_RIGHT:
                        next_position = (current_x + 1, current_y)
                    else:
                        next_position = selected_position

                    # Vérifier si la position sélectionnée est dans les zones accessibles
                    if next_position in accessible_positions:
                        selected_position = next_position

                    # Validation du déplacement
                    if event.key == pygame.K_SPACE:
                        # Déplacer l'unité à la position sélectionnée
                        units[selected_unit_index].x, units[selected_unit_index].y = selected_position
                        turn_done = True  # Fin du tour pour cette unité
                        print(f"Déplacement validé pour {units[selected_unit_index].name} à {selected_position}.")

                # Changer d'unité avec TAB
                if event.key == pygame.K_TAB and turn_done:
                    turn_done = False
                    selected_position = None
                    selected_unit_index = (selected_unit_index + 1) % len(units)
                        
                
                # Activer les compétences:
                
                #====================
                #Pour l'explorateur :
                #====================
                    
                elif event.key == pygame.K_e:  # Compétence 1 : Révéler une zone (Explorateur):
                    if isinstance(units[selected_unit_index], Explorateur):
                        revealed = units[selected_unit_index].revele_zone(grid)
                        last_action_message = f"Zone révélée par {units[selected_unit_index].name}"
               
                elif event.key == pygame.K_q:  #Compétence 2 : Détection de pièges (Explorateur):
                    if isinstance(units[selected_unit_index], Explorateur):
                        last_action_message = units[selected_unit_index].detecte_piege(grid)

                elif event.key == pygame.K_r: #Compétence 3: Coup rapide dégats (Explorateur):
                    if isinstance(units[selected_unit_index], Explorateur):
                        cible = ...  
                        last_action_message = units[selected_unit_index].coup_rapide(cible)
                
                #======================
                # Pour l'Archeologue :
                #======================
                
                elif event.key == pygame.K_d:  # Compétence 1 : Décrypter un indice (Archéologue):
                    if isinstance(units[selected_unit_index], Archeologue):
                        case = grid[units[selected_unit_index].x][units[selected_unit_index].y]
                        last_action_message = units[selected_unit_index].decrypter_indice(case)
               
                elif event.key == pygame.K_a:  #Compétence 2 : Analyse de l'environnement (Archéologue):
                    if isinstance(units[selected_unit_index], Archeologue):
                        last_action_message = units[selected_unit_index].analyse_environnement(grid)

                elif event.key == pygame.K_t: #Compétence 3 : Attaque ciblé (Archeologue):
                    if isinstance(units[selected_unit_index], Archeologue):
                        cible = ...  
                        last_action_message = units[selected_unit_index].attaque_ciblee(cible)
                
                #===================
                #Pour le chasseur :
                #====================
                
                elif event.key == pygame.K_p:  # Compétence 1 : Poser un piège (Chasseur):
                    if isinstance(units[selected_unit_index], Chasseur):
                        x, y = units[selected_unit_index].x, units[selected_unit_index].y
                        last_action_message = units[selected_unit_index].poser_piege(grid, x, y)
                
                elif event.key == pygame.K_b: # Compétence 2 : Brouillard de guerre (Chasseur):
                    if isinstance(units[selected_unit_index], Chasseur):
                        enemy_units = [unit for unit in units if unit != units[selected_unit_index]]  # Liste des unités ennemies
                        last_action_message = units[selected_unit_index].brouillard_de_guerre(enemy_units, grid)

                elif event.key == pygame.K_y: #Compétence 3 : Tire à distance (Chasseur):
                    if isinstance(units[selected_unit_index], Chasseur):
                        cible = ...  
                        last_action_message = units[selected_unit_index].tir_distance(cible)
                        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    
    main()