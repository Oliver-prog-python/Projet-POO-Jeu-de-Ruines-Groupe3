import pygame
from TEST_GAME import Game

pygame.init()


# Dimensions de l'écran du jeu 
SCREEN_WIDTH = 1300  # Largeur fixe
SCREEN_HEIGHT = 750  # Hauteur fixe

FPS = 30  # Limitation à 30 images par seconde


def main_menu(screen):
    # Couleurs
    WHITE = (255, 255, 255)

    # Chargement des images
    background = pygame.image.load("images/map_maya.png")  # L'image du fond
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    start_button_image = pygame.image.load("images/start.png")  # Bouton Start
    start_button_image = pygame.transform.scale(start_button_image, (150, 75))  # Taille réduite
    start_button_rect = start_button_image.get_rect(center=(SCREEN_WIDTH // 2.7, SCREEN_HEIGHT // 6.5))



    running=True
    
    while running:
        screen.fill(WHITE)
        screen.blit(background, (0, 0))
        screen.blit(start_button_image, start_button_rect.topleft)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:  # Clic gauche
                return  # Quitter le menu pour démarrer le jeu
        

        pygame.display.flip()
        
def main():
    
    pygame.init()
    
    # Créer une fenêtre adaptée
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Les Mystérieuses Cités D'or")

    
    # Afficher le menu principal
    main_menu(screen)
    
    # Bloquer les événements souris
    pygame.event.set_blocked([pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])
    
    
    # Initialisation du jeuc
    clock = pygame.time.Clock()
    game = Game(screen)
    game.running = True

    while game.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False

        # Gestion du tour de jeu
        game.handle_player_turn()

        # Vérifiez les conditions de fin de jeu
        if game.fin_de_jeu():
            game.running = False

        # Mise à jour de l'affichage
        game.flip_display()
        clock.tick(FPS)

    pygame.quit()
    print("Jeu terminé.")
if __name__ == "__main__":
    main()


