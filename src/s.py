import pygame

class Player:
    def __init__(self, x, y):
        self.width = 50  # Bredden på spilleren
        self.height = 50  # Høyden på spilleren
        self.rect = pygame.Rect(x, y, self.width, self.height)  # Spillerens hitbox
        self.color = (0, 128, 255)  # Blå farge for spilleren (brukes hvis ingen sprite er lastet)
        self.velocity_y = 0  # Vertikal hastighet (for tyngdekraft)
        self.jump_power = -15  # Hvor høyt spilleren kan hoppe
        self.gravity = 0.8  # Tyngdekraften som påvirker spilleren
        self.on_ground = False  # Sjekker om spilleren står på plattformen

        # Last inn sprite sheet for idle-animasjon
        self.sprite_sheet = pygame.image.load("Assets/sprites/kingvon/walk.png")  # Bytt ut med din sprite sheet
        self.frame_width = 64  # Bredden på hver ramme i sprite sheet
        self.frame_height = 55  # Høyden på hver ramme i sprite sheet
        self.frames = self.load_frames()  # Last inn alle rammene fra sprite sheet
        self.current_frame = 0  # Hvilken ramme som vises nå
        self.animation_speed = 0.1  # Hastighet på animasjonen
        self.animation_counter = 0  # Teller for animasjonen

        # Spillerens retning (1 for høyre, -1 for venstre)
        self.direction = 1

    def load_frames(self):
        # Del opp sprite sheet i enkeltrammer
        frames = []
        for i in range(9):  # Anta at det er 9 rammer i sprite sheet
            frame = self.sprite_sheet.subsurface(pygame.Rect(i * self.frame_width, 0, self.frame_width, self.frame_height))
            frames.append(frame)
        return frames

    def move(self, dx, dy):
        # Flytt spilleren horisontalt og vertikalt
        self.rect.x += dx
        self.rect.y += dy

        # Oppdater retningen basert på bevegelse
        if dx > 0:
            self.direction = 1  # Høyre
        elif dx < 0:
            self.direction = -1  # Venstre

    def jump(self):
        # Hopp bare hvis spilleren står på plattformen
        if self.on_ground:
            self.velocity_y = self.jump_power
            self.on_ground = False

    def update(self, platforms):
        # Oppdater spilleren sin posisjon og tyngdekraft
        self.velocity_y += self.gravity
        self.move(0, self.velocity_y)

        # Sjekk kollisjon med plattformer
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:  # Hvis spilleren faller
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True

        # Oppdater idle-animasjonen
        self.animation_counter += self.animation_speed
        if self.animation_counter >= len(self.frames):
            self.animation_counter = 0
        self.current_frame = int(self.animation_counter)

    def draw(self, screen):
        # Tegn spilleren som en sprite
        frame = self.frames[self.current_frame]
        if self.direction == -1:
            frame = pygame.transform.flip(frame, True, False)  # Speilvend rammen hvis spilleren ser til venstre
        screen.blit(frame, self.rect.topleft)

class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)  # Plattformens hitbox
        self.color = (0, 255, 0)  # Grønn farge for plattformen

    def draw(self, screen):
        # Tegn plattformen på skjermen
        pygame.draw.rect(screen, self.color, self.rect)

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()

        # Opprett spilleren
        self.player = Player(self.screen_width // 2, self.screen_height // 2)

        # Opprett plattformer for et klassisk Smash Bros.-kart
        self.platforms = [
            Platform(0, self.screen_height - 50, self.screen_width, 50),  # Hovedplattform
            Platform(self.screen_width // 4 - 100, self.screen_height - 200, 200, 20),  # Venstre flytende plattform
            Platform(self.screen_width * 3 // 4 - 100, self.screen_height - 200, 200, 20),  # Høyre flytende plattform
            Platform(self.screen_width // 2 - 100, self.screen_height - 350, 200, 20),  # Midtre flytende plattform
        ]

        # Spillvariabler
        self.running = True

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.move(-5, 0)  # Flytt til venstre
        if keys[pygame.K_RIGHT]:
            self.player.move(5, 0)  # Flytt til høyre
        if keys[pygame.K_SPACE]:
            self.player.jump()  # Hopp

    def update(self):
        # Oppdater spilleren og sjekk kollisjoner
        self.player.update(self.platforms)

    def draw(self):
        # Fyll skjermen med svart bakgrunn
        self.screen.fill((0, 0, 0))

        # Tegn plattformene
        for platform in self.platforms:
            platform.draw(self.screen)

        # Tegn spilleren
        self.player.draw(self.screen)

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Håndter input
            self.handle_input()

            # Oppdater spilltilstanden
            self.update()

            # Tegn spillobjekter
            self.draw()

            # Oppdater skjermen
            pygame.display.flip()

            # Begrens oppdateringshastigheten til 60 FPS
            clock.tick(60)