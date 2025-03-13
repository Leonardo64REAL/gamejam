import pygame

class CharacterSelect:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()

        # Font setup
        self.font = pygame.font.Font("assets/fonts/smash_font.ttf", int(self.screen_height / 10))
        self.small_font = pygame.font.Font("assets/fonts/smash_font.ttf", int(self.screen_height / 30))

        # Available characters
        self.characters = ["King Von", "Tyler", "Chief Keef", "Hector"]

        # Two players: each has an index of the currently hovered character
        self.p1_index = 0
        self.p2_index = 1

        # Lock states: once a player presses ENTER, they're "locked in"
        self.p1_locked = False
        self.p2_locked = False

        # Which player is moving the cursor right now? (0 -> P1, 1 -> P2)
        self.current_player = 0

        # Colors
        self.color_normal = (255, 255, 255)  # White frame for unselected
        self.color_p1 = (255, 0, 0)         # Red for player 1
        self.color_p2 = (0, 255, 0)         # Green for player 2

        # Images for each character (scaled to box size in draw())
        self.character1_image = pygame.image.load("assets/images/kingvon.jpg")
        self.character2_image = pygame.image.load("assets/images/tyler.jpg")
        self.character3_image = pygame.image.load("assets/images/cheif.jpg")
        self.character4_image = pygame.image.load("assets/images/hector.jpg")

        self.fade_speed = 3  # Hvor raskt fade-in skal skje (høyere tall = raskere)
        self.alpha = 0  # Startverdi for gjennomsiktighet


    def draw(self):
        self.screen.fill((0, 0, 0))

        # Oppdater gjennomsiktigheten for fade-in effekt
        if self.alpha < 255:  # 255 er fullt synlig
            self.alpha += self.fade_speed
            if self.alpha > 255:
                self.alpha = 255
            self.screen.set_alpha(self.alpha)

        # Title
        title = self.font.render("Select Your Characters", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 10))
        self.screen.blit(title, title_rect)

        # Dimensions for each character box
        character_width = self.screen_width // 6
        character_height = self.screen_height // 4
        spacing = self.screen_width // 10

        total_width = len(self.characters) * character_width + (len(self.characters) - 1) * spacing
        start_x = (self.screen_width - total_width) // 2
        y = self.screen_height // 2 - character_height // 2

        for i, char_name in enumerate(self.characters):
            x = start_x + i * (character_width + spacing)

            # Decide which color outline to draw
            outline_width = 5
            # If both players happen to hover the same character, you'll see 2 outlines
            # (but we'll typically prevent them from locking the same).
            # We'll draw multiple rectangles if i == p1_index or i == p2_index.
            if i == self.p1_index:
                pygame.draw.rect(self.screen, self.color_p1, (x, y, character_width, character_height), outline_width)
            else:
                pygame.draw.rect(self.screen, self.color_normal, (x, y, character_width, character_height), 2)

            if i == self.p2_index:
                pygame.draw.rect(self.screen, self.color_p2, (x, y, character_width, character_height), outline_width)
            else:
                # If not hovered by P2, we won't overwrite P1's outline
                pass

            # Draw the character's image
            # We'll scale the images on the fly so they fit the box
            resized = None
            if char_name == "King Von":
                resized = pygame.transform.scale(self.character1_image, (character_width - 6, character_height - 6))
            elif char_name == "Tyler":
                resized = pygame.transform.scale(self.character2_image, (character_width - 6, character_height - 6))
            elif char_name == "Chief Keef":
                resized = pygame.transform.scale(self.character3_image, (character_width - 6, character_height - 6))
            elif char_name == "Hector":
                resized = pygame.transform.scale(self.character4_image, (character_width - 6, character_height - 6))

            if resized:
                self.screen.blit(resized, (x + 2, y + 2))

            # Character name under the box
            text = self.small_font.render(char_name, True, (255, 255, 255))
            text_rect = text.get_rect(center=(x + character_width // 2, y + character_height + 40))
            self.screen.blit(text, text_rect)

        # Instructions
        instructions = self.small_font.render(
            "Arrow keys (P1) / Press ENTER to lock. Then arrow keys (P2) / ENTER to lock. No duplicates!",
            True,
            (128, 128, 128)
        )
        instructions_rect = instructions.get_rect(center=(self.screen_width // 2, self.screen_height - self.screen_height // 12))
        self.screen.blit(instructions, instructions_rect)

    def handle_input(self, event):
        """Handle keyboard input for both players depending on `current_player`."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                if self.current_player == 0 and not self.p1_locked:
                    self.p1_index = (self.p1_index - 1) % len(self.characters)
                elif self.current_player == 1 and not self.p2_locked:
                    self.p2_index = (self.p2_index - 1) % len(self.characters)

            elif event.key == pygame.K_RIGHT:
                if self.current_player == 0 and not self.p1_locked:
                    self.p1_index = (self.p1_index + 1) % len(self.characters)
                elif self.current_player == 1 and not self.p2_locked:
                    self.p2_index = (self.p2_index + 1) % len(self.characters)

            elif event.key == pygame.K_RETURN:
                # Lock in whichever player is currently picking
                if self.current_player == 0 and not self.p1_locked:
                    self.p1_locked = True
                    # Move on to player 2
                    self.current_player = 1
                elif self.current_player == 1 and not self.p2_locked:
                    # Check if same pick as P1
                    if self.p2_index == self.p1_index:
                        print("Player 2 cannot pick the same character as Player 1!")
                        # We'll just refuse to lock in
                    else:
                        self.p2_locked = True
                        # Both locked now? Return the final picks
                        return (
                            self.characters[self.p1_index],
                            self.characters[self.p2_index]
                        )
        return None

    def run(self):
        """Loop until both players pick distinct characters, or user quits."""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None  # user closed the window
                result = self.handle_input(event)
                if result:
                    # This is a tuple of (p1_char, p2_char)
                    return result

            self.draw()
            pygame.display.flip()
        return None  # Shouldn’t really get here unless forcibly ended
