import pygame
from menu import Menu
from character import CharacterSelect
from game import main as game_main

def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Super Smash Bros. Pygame Edition")
    clock = pygame.time.Clock()

    # 🎮 Initialize joystick module
    pygame.joystick.init()
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        print(f"Detected controller: {joystick.get_name()}")

    menu = Menu(screen)
    character_select = CharacterSelect(screen)

    running = True
    current_screen = "menu"
    selected_character = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.JOYBUTTONDOWN:
                print(f"Joystick button {event.button} pressed")  # Debugging

        # 🎮 Read Joystick Input (Move with Left Stick)
        if pygame.joystick.get_count() > 0:
            axis_x = joystick.get_axis(0)  # Left Stick X
            axis_y = joystick.get_axis(1)  # Left Stick Y
            if axis_x < -0.5:  # Move left
                print("Joystick moving left")
            if axis_x > 0.5:  # Move right
                print("Joystick moving right")
            if axis_y < -0.5:  # Jump
                print("Joystick jumping")
            if axis_y > 0.5:  # Fast fall
                print("Joystick fast falling")

        if current_screen == "menu":
            action = menu.run()
            if action == "Start Game":
                current_screen = "character_select"
            elif action == "Quit":
                running = False
        elif current_screen == "character_select":
            selected_character = character_select.run()
            if selected_character:
                print(f"Selected character: {selected_character}")
                current_screen = "game"
            else:
                current_screen = "menu"
        elif current_screen == "game":
            game_main()
            current_screen = "menu"

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
