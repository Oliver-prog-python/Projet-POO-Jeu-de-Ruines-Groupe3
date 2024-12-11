import pygame
from TEST_GAME import Game

# Dimensions
WIDTH, HEIGHT = 1300, 800  # Largeur totale pour inclure la zone UI
GRID_WIDTH = 800  # Largeur de la grille
UI_WIDTH = WIDTH - GRID_WIDTH  # Largeur de la zone UI
CELL_SIZE = GRID_WIDTH // 10 # Taille des cellules
FPS = 30  # Limitation à 30 images par seconde


def main_menu(screen):
    # Couleurs
    WHITE = (255, 255, 255)

    # Chargement des images
    background = pygame.image.load("images/map_maya.png")  # L'image du fond
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    start_button_image = pygame.image.load("images/start.png")  # Bouton Start
    start_button_image = pygame.transform.scale(start_button_image, (150, 75))  # Taille réduite
    start_button_rect = start_button_image.get_rect(center=(WIDTH // 2.7, HEIGHT // 6.5))



    running=True
    while running:
        screen.fill(WHITE)
        screen.blit(background, (0, 0))
        screen.blit(start_button_image, start_button_rect.topleft)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Clic gauche
                if start_button_rect.collidepoint(event.pos):
                    return  # Quitter le menu pour démarrer le jeu

        pygame.display.flip()


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Les Mystérieuses Cités D'or")
    clock = pygame.time.Clock()

    # Afficher le menu principal
    main_menu(screen)
    # Bloquer les événements souris
    pygame.event.set_blocked([pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])

    # Initialisation du jeu
    game = Game(screen)
    running = True

    while running:
        # Gestion des événements
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
