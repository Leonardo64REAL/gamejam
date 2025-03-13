import pygame
from menu import Menu
from character import CharacterSelect
from game import main as game_main

def main():
    pygame.init()
    pygame.mixer.init()

    pygame.mixer.music.load("Assets/Audio/menu.mp3")
    pygame.mixer.music.play(-1, 0.0, 3000)

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Super Smash Bros. Pygame Edition")

    clock = pygame.time.Clock()

    menu = Menu(screen)
    # Remove the old line: character_select = CharacterSelect(screen)
    # We'll create it each time below instead.

    running = True
    current_screen = "menu"

    p1_character = None
    p2_character = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.JOYBUTTONDOWN:
                print(f"[MENU DEBUG] Joystick {event.joy} button {event.button} pressed")

        if current_screen == "menu":
            action = menu.run()
            if action == "Start Game":
                # Re-initialize the character select screen each time
                character_select = CharacterSelect(screen)
                current_screen = "character_select"
            elif action == "Quit":
                running = False

        elif current_screen == "character_select":
            picks = character_select.run()
            if picks:  # (p1_char, p2_char)
                p1_character, p2_character = picks
                print("P1 picked:", p1_character, " | P2 picked:", p2_character)
                current_screen = "game"
            else:
                # user closed character select or pressed ESC => back to menu
                current_screen = "menu"

        elif current_screen == "game":
            pygame.mixer.music.fadeout(3000)
            pygame.mixer.music.load("Assets/Audio/battle.mp3")
            pygame.mixer.music.play(-1, 0.0, 3000)

            # Launch the actual game
            game_main(p1_character, p2_character)

            # After the match ends, go back to menu
            current_screen = "menu"

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
