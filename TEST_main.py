import pygame
from game import Game

# Configuration
CELL_SIZE = 60
GRID_SIZE = 10
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE
FPS = 30

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Jeu de stratégie : Humain vs IA")
    clock = pygame.time.Clock()

    game = Game(screen, GRID_SIZE, CELL_SIZE)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        game.handle_player_turn()
        game.handle_enemy_turn()
        game.flip_display()

        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
