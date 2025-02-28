import pygame

class CharacterSelect:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()

        # Last inn font (bruk smash_font.ttf som du allerede har)
        self.font = pygame.font.Font("assets/fonts/smash_font.ttf", int(self.screen_height / 10))
        self.small_font = pygame.font.Font("assets/fonts/smash_font.ttf", int(self.screen_height / 25))

        # Karakterer (foreløpig bare navn, kan erstattes med bilder eller annet)
        self.characters = ["King Von", "Tyler", "Character 3", "Character 4"]
        self.selected_character = 0  # Hvilken karakter som er valgt (indeks)

        # Last inn bildet for king von
        self.character1_image = pygame.image.load("assets/images/kingvon.jpg")
        self.character1_image = pygame.transform.scale(self.character1_image, (self.screen_width // 6 - 4, self.screen_height // 4 - 4))  # Skaler bildet til boksstørrelsen

        #Last inn bildet for tyler
        self.character2_image = pygame.image.load("assets/images/tyler.jpg")
        self.character2_image = pygame.transform.scale(self.character2_image, (self.screen_width // 6 - 4, self.screen_height // 4 - 4))  # Skaler bildet til boksstørrelsen
        # Farger
        self.color_normal = (255, 255, 255)  # Hvit farge for uvalgte karakterer
        self.color_selected = (255, 0, 0)  # Rød farge for valgt karakter

    def draw(self):
        # Fyll skjermen med svart bakgrunn
        self.screen.fill((0, 0, 0))

        # Tegn tittelen
        title = self.font.render("Select Your Character", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 6))
        self.screen.blit(title, title_rect)

        # Tegn karakterboksene
        character_width = self.screen_width // 6  # Bredden på hver karakterboks
        character_height = self.screen_height // 4  # Høyden på hver karakterboks
        spacing = self.screen_width // 10  # Avstand mellom boksene

        # Total bredde for alle boksene + mellomrom
        total_width = len(self.characters) * character_width + (len(self.characters) - 1) * spacing

        # Startposisjon for den første boksen (for å sentrere alle boksene)
        start_x = (self.screen_width - total_width) // 2
        y = self.screen_height // 2 - character_height // 2

        for i, character in enumerate(self.characters):
            x = start_x + i * (character_width + spacing)

            # Tegn en boks for hver karakter
            if i == self.selected_character:
                pygame.draw.rect(self.screen, self.color_selected, (x, y, character_width, character_height), 5)  # Valgt karakter (rød ramme)
            else:
                pygame.draw.rect(self.screen, self.color_normal, (x, y, character_width, character_height), 2)  # Uvalgte karakterer (hvit ramme)

            # Tegn bildet for "Character 1" inne i boksen
            if character == "King Von":
                self.screen.blit(self.character1_image, (x + 2, y + 2))
            elif character == "Tyler":
                self.screen.blit(self.character2_image, (x + 2, y + 2))

            # Tegn karakterens navn under boksen
            text = self.small_font.render(character, True, self.color_normal)
            text_rect = text.get_rect(center=(x + character_width // 2, y + character_height + 20))
            self.screen.blit(text, text_rect)

        # Tegn instruksjoner for navigering
        instructions = self.small_font.render("Use LEFT/RIGHT to select, ENTER to confirm", True, (128, 128, 128))
        instructions_rect = instructions.get_rect(center=(self.screen_width // 2, self.screen_height - self.screen_height // 10))
        self.screen.blit(instructions, instructions_rect)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                # Flytt til venstre i karaktervalget
                self.selected_character = (self.selected_character - 1) % len(self.characters)
            elif event.key == pygame.K_RIGHT:
                # Flytt til høyre i karaktervalget
                self.selected_character = (self.selected_character + 1) % len(self.characters)
            elif event.key == pygame.K_RETURN:
                # Returner den valgte karakteren
                return self.characters[self.selected_character]
        return None

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None  # Avslutt karaktervalget hvis brukeren lukker vinduet
                selected = self.handle_input(event)
                if selected:
                    return selected  # Returner den valgte karakteren

            # Tegn karaktervalg-skjermen
            self.draw()
            pygame.display.flip()