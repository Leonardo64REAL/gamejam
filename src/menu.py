import pygame

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()  # Hent skjermstørrelsen
        self.font = pygame.font.Font(None, int(self.screen_height / 10))  # Adaptiv fontstørrelse
        self.small_font = pygame.font.Font(None, int(self.screen_height / 15))  # Mindre font for instruksjoner
        self.options = ["Start Game", "Settings", "Quit"]
        self.selected_option = 0  # Hvilket valg som er valgt (indeks)
        self.color_normal = (255, 255, 255)  # Hvit farge for uvalgte valg
        self.color_selected = (255, 0, 0)  # Rød farge for valgt valg

    def draw(self):
        # Fyll skjermen med svart bakgrunn
        self.screen.fill((0, 0, 0))

        # Tegn tittelen
        title = self.font.render("Super Smash Bros. Pygame", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 6))  # Sentrert øverst
        self.screen.blit(title, title_rect)

        # Tegn menyvalgene
        for i, option in enumerate(self.options):
            color = self.color_selected if i == self.selected_option else self.color_normal
            text = self.small_font.render(option, True, color)
            text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + i * (self.screen_height // 8)))  # Sentrert midt på skjermen
            self.screen.blit(text, text_rect)

        # Tegn instruksjoner for navigering
        instructions = self.small_font.render("Use UP/DOWN to navigate, ENTER to select", True, (128, 128, 128))
        instructions_rect = instructions.get_rect(center=(self.screen_width // 2, self.screen_height - self.screen_height // 10))  # Nederst på skjermen
        self.screen.blit(instructions, instructions_rect)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                # Flytt opp i menyen
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                # Flytt ned i menyen
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                # Returner det valgte alternativet
                return self.options[self.selected_option]
        return None

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "Quit"  # Avslutt spillet hvis brukeren lukker vinduet
                selected = self.handle_input(event)
                if selected:
                    return selected  # Returner det valgte alternativet

            # Tegn menyen
            self.draw()
            pygame.display.flip()