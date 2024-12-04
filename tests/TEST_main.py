import pygame
from TEST_GAME2 import Game

# Dimensions
WIDTH, HEIGHT = 1300, 800  # Largeur totale pour inclure la zone UI
GRID_WIDTH = 800  # Largeur de la grille
UI_WIDTH = WIDTH - GRID_WIDTH  # Largeur de la zone UI
CELL_SIZE = GRID_WIDTH // 10  # Taille des cellules
FPS = 30  # Limitation à 30 images par seconde

player_turn = True 

def main():
    global player_turn
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Jeu des Ruines")
    clock = pygame.time.Clock()

    # Bloquer les événements souris
    pygame.event.set_blocked([pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])

    # Initialisation du jeu
    game = Game(screen)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        if player_turn:
            game.handle_player_turn()  # Tour du joueur
            player_turn = False  # Passer au tour de l'IA
        else:
            game.handle_enemy_turn()  # Tour de l'IA
            player_turn = True  # Revenir au tour du joueur

        # Rafraîchissement de l'affichage
        game.flip_display()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
