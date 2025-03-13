import pygame
from menu import Menu
from character import CharacterSelect
# Note: Be sure to remove or comment out any `pygame.quit()` or `sys.exit()` calls
# at the END of your `game.py` so that `game_main(...)` can simply return when done.
from game import main as game_main

def main():
    pygame.init()
    # Initialize the audio mixer
    pygame.mixer.init()

    # Load menu screen music
    pygame.mixer.music.load("Assets/Audio/menu.mp3")
    # Loop forever: -1 means infinite loops
    pygame.mixer.music.play(-1, 0.0, 3000)

    # Fullscreen setup
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Super Smash Bros. Pygame Edition")

    clock = pygame.time.Clock()

    # IMPORTANT: We do NOT call pygame.joystick.init() here,
    # because in game.py we handle the multi-joystick setup.

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

            # Purely optional debug info while in the menu:
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
            # Fade out the current track, load battle music, play in a loop
            pygame.mixer.music.fadeout(3000)
            pygame.mixer.music.load("Assets/Audio/battle.mp3")
            pygame.mixer.music.play(-1, 0.0, 3000)

            # Pass both picks into the new game logic
            # Be sure `game_main()` ends with `return` (not `sys.exit()`),
            # so we can come back here afterward.
            game_main(p1_character, p2_character)

            # After the game_main function returns, go back to the menu
            current_screen = "menu"

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
