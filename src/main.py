import pygame
from menu import Menu
from character import CharacterSelect

def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_width, screen_height = screen.get_size()
    pygame.display.set_caption("Super Smash Bros. Pygame Edition")
    clock = pygame.time.Clock()

    menu = Menu(screen)
    character_select = CharacterSelect(screen)

    running = True
    current_screen = "menu"  # Starter med menyen
    selected_character = None  # Karakteren som er valgt

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if current_screen == "menu":
            action = menu.run()
            if action == "Start Game":
                current_screen = "character_select"  # Gå til karaktervalg
            elif action == "Quit":
                running = False
        elif current_screen == "character_select":
            selected_character = character_select.run()
            if selected_character:
                print(f"Selected character: {selected_character}")
                current_screen = "game"  # Gå til spillet
            else:
                current_screen = "menu"  # Tilbake til menyen hvis ingen karakter er valgt

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()