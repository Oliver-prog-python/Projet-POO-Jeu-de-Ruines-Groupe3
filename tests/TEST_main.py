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

        # Gestion des tours pour les deux joueurs
        game.handle_player_turn()

         # Vérifier les conditions de fin de jeu
        if game.fin_de_jeu():
            running = False  # Arrêter la boucle principale si le jeu est terminé

        # Rafraîchissement de l'affichage
        game.flip_display()
        clock.tick(FPS)

    pygame.quit()
    print("Jeu terminé.")

if __name__ == "__main__":
    main()
