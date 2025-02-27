import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Platform dimensions
PLATFORM_WIDTH = SCREEN_WIDTH // 2
PLATFORM_HEIGHT = 100
PLATFORM_X = (SCREEN_WIDTH - PLATFORM_WIDTH) // 2
PLATFORM_Y = SCREEN_HEIGHT - 200

# Player dimensions
PLAYER_WIDTH = 100
PLAYER_HEIGHT = 100
PLAYER_SPEED = 8
GRAVITY = 0.5
JUMP_STRENGTH = 13
FALL_FAST = 15

# Lives
MAX_LIVES = 3

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.on_ground = False
        self.lives = MAX_LIVES  # Initialize lives

    def update(self, platforms):
        # Apply gravity
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        # Check for collision with platforms
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:  # Falling
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True

    def jump(self):
        if self.on_ground:
            self.vel_y = -JUMP_STRENGTH

    def move_left(self):
        self.rect.x -= PLAYER_SPEED

    def move_right(self):
        self.rect.x += PLAYER_SPEED

    def fall(self):
        self.vel_y = 0
        self.rect.y += FALL_FAST

    def respawn(self):
        """Respawn the player in the center of the screen."""
        self.rect.x = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2
        self.rect.y = PLATFORM_Y - PLAYER_HEIGHT
        self.vel_y = 0
        self.lives -= 1  # Lose a life

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def main():
    clock = pygame.time.Clock()

    # Create player
    player = Player(SCREEN_WIDTH // 2, PLATFORM_Y - PLAYER_HEIGHT)
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    # Create platform
    platform = Platform(PLATFORM_X, PLATFORM_Y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
    platforms = pygame.sprite.Group()
    platforms.add(platform)
    all_sprites.add(platform)

    # Font for displaying lives
    font = pygame.font.Font(None, 74)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move_left()
        if keys[pygame.K_RIGHT]:
            player.move_right()
        if keys[pygame.K_UP]:
            player.jump()
        if keys[pygame.K_DOWN]:
            player.fall()

        # Check if player falls off the screen or touches the edges
        if player.rect.y > SCREEN_HEIGHT+100 or player.rect.x < -100 or player.rect.x > SCREEN_WIDTH + 100 or player.rect.y < -100:
            if player.lives > 1:
                player.respawn()  # Respawn if lives remain
            else:
                running = False  # Game over if no lives left

        # Update
        all_sprites.update(platforms)

        # Draw
        SCREEN.fill(BLACK)
        all_sprites.draw(SCREEN)

        # Display lives
        lives_text = font.render(f"Lives: {player.lives}", True, WHITE)
        SCREEN.blit(lives_text, (20, 20))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()