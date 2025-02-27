import pygame
from menu import Menu

def main():
    pygame.init()
    
    # Sett opp fullskjermmodus
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_width, screen_height = screen.get_size()  # Hent skjermstørrelsen
    pygame.display.set_caption("Super Smash Bros. Pygame Edition")
    clock = pygame.time.Clock()

    menu = Menu(screen)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Kjør menyen og få brukerens valg
        action = menu.run()

        if action == "Start Game":
            print("Starting game...")  # Her kan du starte spillet
        elif action == "Settings":
            print("Opening settings...")  # Her kan du åpne innstillinger
        elif action == "Quit":
            running = False  # Avslutt spillet

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()