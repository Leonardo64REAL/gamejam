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
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

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

# Amount of Players
AMOUNT_OF_PLAYERS = 2

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color, controls):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.on_ground = False
        self.lives = MAX_LIVES  # Initialize lives
        self.controls = controls  # Control keys for this player
        self.jump_count = 0  # Track the number of jumps
        self.can_double_jump = True  # Allow double jump

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
                    self.jump_count = 0  # Reset jump count when landing
                    self.can_double_jump = True  # Reset double jump ability

    def jump(self):
        if self.on_ground:
            self.vel_y = -JUMP_STRENGTH
            self.jump_count += 1
        elif self.can_double_jump and self.jump_count < 2:  # Allow double jump
            self.vel_y = -JUMP_STRENGTH
            self.jump_count += 1
            self.can_double_jump = False  # Disable double jump after use

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

    # Create players
    player1 = Player(SCREEN_WIDTH // 4, PLATFORM_Y - PLAYER_HEIGHT, RED, {
        "left": pygame.K_a,
        "right": pygame.K_d,
        "jump": pygame.K_w,
        "fall": pygame.K_s
    })
    player2 = Player(SCREEN_WIDTH // 2, PLATFORM_Y - PLAYER_HEIGHT, GREEN, {
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "jump": pygame.K_UP,
        "fall": pygame.K_DOWN
    })
    player3 = Player(3 * SCREEN_WIDTH // 4, PLATFORM_Y - PLAYER_HEIGHT, BLUE, {
        "left": pygame.K_j,
        "right": pygame.K_l,
        "jump": pygame.K_i,
        "fall": pygame.K_k
    })

    all_sprites = pygame.sprite.Group()
    if AMOUNT_OF_PLAYERS == 2:
        all_sprites.add(player1, player2)
    if AMOUNT_OF_PLAYERS == 3:
        all_sprites.add(player1, player2, player3)

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
        for player in [player1, player2, player3]:
            if keys[player.controls["left"]]:
                player.move_left()
            if keys[player.controls["right"]]:
                player.move_right()
            if keys[player.controls["jump"]]:
                player.jump()
            if keys[player.controls["fall"]]:
                player.fall()

            # Check if player falls off the screen or touches the edges
            if player.rect.y > SCREEN_HEIGHT + 300 or player.rect.x < -300 or player.rect.x > SCREEN_WIDTH + 300 or player.rect.y < -300:
                if player.lives > 1:
                    player.respawn()  # Respawn if lives remain
                else:
                    all_sprites.remove(player)  # Remove player if no lives left

        # Update
        all_sprites.update(platforms)

        # Draw
        SCREEN.fill(BLACK)
        all_sprites.draw(SCREEN)

        # Display lives
        if AMOUNT_OF_PLAYERS == 2:
            lives_text1 = font.render(f"P1 Lives: {player1.lives}", True, RED)
            lives_text2 = font.render(f"P2 Lives: {player2.lives}", True, GREEN)
        if AMOUNT_OF_PLAYERS == 3:
            lives_text1 = font.render(f"P1 Lives: {player1.lives}", True, RED)
            lives_text2 = font.render(f"P2 Lives: {player2.lives}", True, GREEN)
            lives_text3 = font.render(f"P3 Lives: {player3.lives}", True, BLUE)
        
        if AMOUNT_OF_PLAYERS == 2:
            SCREEN.blit(lives_text1, (20, 20))
            SCREEN.blit(lives_text2, (20, 100))
        if AMOUNT_OF_PLAYERS == 3:
            SCREEN.blit(lives_text1, (20, 20))
            SCREEN.blit(lives_text2, (20, 100))
            SCREEN.blit(lives_text3, (20, 180))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()