import pygame
from menu import Menu
from character import CharacterSelect
from game import main as game_main

def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Super Smash Bros. Pygame Edition")
    clock = pygame.time.Clock()

    # IMPORTANT: We do NOT call pygame.joystick.init() here,
    # because in game.py we will handle the multi-joystick setup.
    # Doing so here might “lock in” a single recognized controller.

    menu = Menu(screen)
    character_select = CharacterSelect(screen)

    running = True
    current_screen = "menu"

    # We'll hold the two characters the players pick
    p1_character = None
    p2_character = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # This is purely optional debug info while in the menu:
            elif event.type == pygame.JOYBUTTONDOWN:
                print(f"[MENU DEBUG] Joystick {event.joy} button {event.button} pressed")

        if current_screen == "menu":
            action = menu.run()
            if action == "Start Game":
                current_screen = "character_select"
            elif action == "Quit":
                running = False

        elif current_screen == "character_select":
            picks = character_select.run()
            # `picks` is None if the user closed the window,
            # or a tuple (p1_char, p2_char) if both players locked in characters.
            if picks:
                p1_character, p2_character = picks
                print("P1 picked:", p1_character, " | P2 picked:", p2_character)
                current_screen = "game"
            else:
                # user escaped or closed; go back to menu
                current_screen = "menu"

        elif current_screen == "game":
            # Pass both picks into the new game logic
            game_main(p1_character, p2_character)
            # After the game closes, return to menu
            current_screen = "menu"

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
