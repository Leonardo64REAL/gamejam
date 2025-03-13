import pygame

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()  # Hent skjermstørrelsen

        # Last inn den egendefinerte fonten
        self.font = pygame.font.Font("assets/fonts/smash_font.ttf", int(self.screen_height / 10))  # Adaptiv fontstørrelse
        self.small_font = pygame.font.Font("assets/fonts/smash_font.ttf", int(self.screen_height / 20))  # Mindre font for instruksjoner

        self.options = ["Start Game", "Settings", "Quit"]
        self.selected_option = 0  # Hvilket valg som er valgt (indeks)
        self.color_normal = (255, 255, 255)  # Hvit farge for uvalgte valg
        self.color_selected = (255, 0, 0)  # Rød farge for valgt valg

        # Last inn bakgrunnsbilde
        self.background_image = pygame.image.load("assets/images/menu_bg.jpg")
        self.background_image = pygame.transform.scale(self.background_image, (self.screen_width, self.screen_height))  # Skaler bildet til skjermstørrelsen

        # Lag en overflate for bakgrunnsbildet med alpha (gjennomsiktighet)
        #testkommentar
        self.background_surface = self.background_image.copy()
        self.background_surface.set_alpha(0)  # Start med fullstendig gjennomsiktig

        # Fade-in effekt variabler
        self.fade_speed = 3  # Hvor raskt fade-in skal skje (høyere tall = raskere)
        self.alpha = 0  # Startverdi for gjennomsiktighet

    def draw(self):
        # Fyll skjermen med svart bakgrunn (som fallback hvis bildet ikke dekker hele skjermen)
        self.screen.fill((0, 0, 0))

        # Oppdater gjennomsiktigheten for fade-in effekt
        if self.alpha < 255:  # 255 er fullt synlig
            self.alpha += self.fade_speed
            if self.alpha > 255:
                self.alpha = 255
            self.background_surface.set_alpha(self.alpha)

        # Tegn bakgrunnsbildet
        self.screen.blit(self.background_surface, (0, 0))

        # Tegn tittelen
        title = self.font.render("Compton Brawl", True, (0, 0, 0))
        title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 6))  # Sentrert øverst
        self.screen.blit(title, title_rect)

        # Tegn menyvalgene
        for i, option in enumerate(self.options):
            color = self.color_selected if i == self.selected_option else self.color_normal
            text = self.small_font.render(option, True, color)
            text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + i * (self.screen_height // 8)))  # Sentrert midt på skjermen
            self.screen.blit(text, text_rect)

        # Tegn instruksjoner for navigering
        instructions = self.small_font.render("Use UP/DOWN to navigate, X to select", True, (128, 128, 128))
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
        pygame.init()
        pygame.mixer.init()

        pygame.mixer.music.load("Assets/Audio/menu.mp3")
        pygame.mixer.music.play(-1, 0.0, 3000)
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