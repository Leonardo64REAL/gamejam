import pygame
import sys
import time

pygame.init()
pygame.font.init()

# Gather screen info
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

# Fullscreen
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)

# Load background image
background_img = pygame.image.load("Assets/Images/background_2.png")
background = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Colors
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GREEN = (0,   255,   0)

# Platform sizing (scaled to the screen)
PLATFORM_MAIN_WIDTH  = int(SCREEN_WIDTH * 0.77)
PLATFORM_MAIN_HEIGHT = int(SCREEN_HEIGHT * 0.05)
PLATFORM_MAIN_X      = (SCREEN_WIDTH - PLATFORM_MAIN_WIDTH) // 2
PLATFORM_MAIN_Y      = int(SCREEN_HEIGHT * 0.8)

# Two smaller "air" platforms
PLATFORM_AIR_WIDTH  = int(SCREEN_WIDTH * 0.17)
PLATFORM_AIR_HEIGHT = int(SCREEN_HEIGHT * 0.03)

PLATFORM_AIR_1_X = int(SCREEN_WIDTH * 0.22)
PLATFORM_AIR_1_Y = int(SCREEN_HEIGHT * 0.6)

PLATFORM_AIR_2_X = int(SCREEN_WIDTH * 0.62)
PLATFORM_AIR_2_Y = int(SCREEN_HEIGHT * 0.6)

# Player & Attack constants
PLAYER_WIDTH  = 100
PLAYER_HEIGHT = 100
PLAYER_SPEED  = 10
GRAVITY       = 0.5
JUMP_STRENGTH = 13
MAX_LIVES     = 3
FALL_FAST     = 15

ATTACK_COOLDOWN             = 0.5
RANGED_COOLDOWN             = 0.5
RANGED_LENGTH               = 1
RANGED_RELOAD               = 3
CUBE_LIFETIME               = 0.01
BASE_KNOCKBACK              = 15
KNOCKBACK_RESISTANCE_FACTOR = 0.1

# Example dictionary for character images
CHARACTER_IMAGES = {
    "tyler": "assets/images/tyler.jpg",     # use "tyler" in lowercase if you want the bullet arc
    "Tyler": "assets/images/tyler.jpg",     # or also handle uppercase if you prefer
    "Hector": "assets/images/hector.jpg",
    "King Von": "assets/images/kingvon.jpg",
    "Chief Keef": "assets/images/cheif.jpg",
}

#
# Invisible Platform
#
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        # Use an alpha surface for invisibility
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))  # fully transparent
        self.rect = self.image.get_rect(x=x, y=y)

#
# Player class with double jump logic from your snippet
#
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color, playable_character, joystick_index):
        super().__init__()

        # Load image or fallback color
        image_path = CHARACTER_IMAGES.get(playable_character)
        if image_path:
            raw_img = pygame.image.load(image_path)
            self.image = pygame.transform.scale(raw_img, (PLAYER_WIDTH, PLAYER_HEIGHT))
        else:
            self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
            self.image.fill(color)

        self.rect = self.image.get_rect(topleft=(x, y))

        # Physics
        self.vel_x = 0
        self.vel_y = 0

        # Double-jump state
        self.on_ground = False
        self.can_double_jump = True
        self.jump_count = 0
        self.jump_button_pressed = False

        # Stats
        self.lives = MAX_LIVES
        self.playable_character = playable_character
        self.damage_knockback = 1  # accumulative knockback factor
        self.last_direction = "none"

        # Attack tracking
        self.last_attack_time = 0
        self.last_ranged_time = 0
        self.bullet_count = RANGED_RELOAD
        self.can_shoot = True

        # Joystick assignment
        self.joystick = None
        if joystick_index is not None and joystick_index >= 0:
            if joystick_index < pygame.joystick.get_count():
                self.joystick = pygame.joystick.Joystick(joystick_index)
                self.joystick.init()

    def update_physics(self, platforms):
        # Gravity
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        # Basic friction
        self.rect.x += self.vel_x
        self.vel_x *= 0.9

        # Collision check → resets jumps if we land
        self.on_ground = False
        for p in platforms:
            if self.rect.colliderect(p.rect):
                # landing on top
                if self.vel_y > 0 and self.rect.bottom <= p.rect.bottom:
                    self.rect.bottom = p.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.jump_count = 0
                    self.can_double_jump = True

    #
    # Joystick input
    #
    def handle_joystick_input(self, attack_sprites, current_time):
        if not self.joystick:
            return

        axis_x = self.joystick.get_axis(0)
        if axis_x < -0.5:
            self.move_left()
        elif axis_x > 0.5:
            self.move_right()

        # Buttons (adjust indices to match your controller)
        # 0: jump, 1: fall, 2: normal attack, 3: upper attack, etc.
        if self.joystick.get_button(0):  # Jump
            self.jump()
        else:
            # if no jump button pressed this frame, reset jump_button_pressed
            self.jump_button_pressed = False

        if self.joystick.get_button(1):  # Fall
            self.fall()
        if self.joystick.get_button(2):  # Attack
            self.attack(attack_sprites, current_time)
        if self.joystick.get_button(3):  # Upper Attack
            self.upperattack(attack_sprites, current_time)

        # Additional buttons if desired
        if self.joystick.get_button(4):
            self.lowerattack(attack_sprites, current_time)
        if self.joystick.get_button(5):
            self.rangedattack(attack_sprites, current_time)

    #
    # Movement & Jump
    #
    def move_left(self):
        self.rect.x -= PLAYER_SPEED
        self.last_direction = "left"

    def move_right(self):
        self.rect.x += PLAYER_SPEED
        self.last_direction = "right"

    def jump(self):
        # First jump if on ground
        if self.on_ground:
            self.vel_y = -JUMP_STRENGTH
            self.jump_count += 1
            self.jump_button_pressed = True
        # Second jump if not grounded but can_double_jump is True
        elif self.can_double_jump and self.jump_count < 2 and not self.jump_button_pressed:
            self.vel_y = -JUMP_STRENGTH
            self.jump_count += 1
            self.can_double_jump = False

    def fall(self):
        self.vel_y = 0
        self.rect.y += FALL_FAST

    def respawn(self):
        # Place at center, above main platform
        self.rect.x = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2
        self.rect.y = PLATFORM_MAIN_Y - PLAYER_HEIGHT
        self.vel_x = 0
        self.vel_y = 0
        self.lives -= 1

        # Reset knockback & jump
        self.damage_knockback = 1
        self.can_double_jump = True
        self.jump_count = 0

    #
    # Basic Attacks
    #
    def attack(self, attack_sprites, current_time):
        if (current_time - self.last_attack_time) >= ATTACK_COOLDOWN:
            cube = Cube(self.rect.x, self.rect.y, self.last_direction)
            attack_sprites.add(cube)
            self.last_attack_time = current_time

    def upperattack(self, attack_sprites, current_time):
        if (current_time - self.last_attack_time) >= ATTACK_COOLDOWN:
            upper_cube = upperCube(self.rect.x, self.rect.y, self.last_direction)
            attack_sprites.add(upper_cube)
            self.last_attack_time = current_time

    def lowerattack(self, attack_sprites, current_time):
        if (current_time - self.last_attack_time) >= ATTACK_COOLDOWN:
            lower_cube = lowerCube(self.rect.x, self.rect.y, self.last_direction)
            attack_sprites.add(lower_cube)
            self.last_attack_time = current_time

    def rangedattack(self, attack_sprites, current_time):
        if self.bullet_count <= 0:
            self.bullet_count = 0

        if (current_time - self.last_ranged_time) >= RANGED_COOLDOWN and self.can_shoot:
            range_cube = rangeCube(self.rect.x, self.rect.y, self.last_direction, self.playable_character)
            attack_sprites.add(range_cube)
            self.bullet_count -= 1
            self.last_ranged_time = current_time

            if self.bullet_count <= 0:
                self.can_shoot = False

        # Reload after some time
        if (current_time - self.last_ranged_time) >= RANGED_LENGTH:
            self.bullet_count = RANGED_RELOAD
            self.can_shoot = True

    #
    # Knockback
    #
    def apply_knockback(self, knockback_amount, direction):
        import math
        resistance = (1 + KNOCKBACK_RESISTANCE_FACTOR * self.damage_knockback)
        kb = knockback_amount * resistance
        if direction == "right":
            self.vel_x = kb
            self.vel_y = -kb * 0.4
        else:
            self.vel_x = -kb
            self.vel_y = -kb * 0.4
        self.damage_knockback += resistance

    def apply_upper_knockback(self, knockback_amount, direction):
        resistance = (1 + KNOCKBACK_RESISTANCE_FACTOR * self.damage_knockback)
        kb = knockback_amount * resistance
        if direction == "right":
            self.vel_x = kb * 0.3
            self.vel_y = -kb * 0.4
        else:
            self.vel_x = -kb * 0.3
            self.vel_y = -kb * 0.4
        self.damage_knockback += resistance

    def apply_lower_knockback(self, knockback_amount, direction):
        resistance = (1 + KNOCKBACK_RESISTANCE_FACTOR * self.damage_knockback)
        kb = knockback_amount * resistance
        if direction == "right":
            self.vel_x = kb * 0.3
            self.vel_y = kb * 0.5
        else:
            self.vel_x = -kb * 0.3
            self.vel_y = kb * 0.5
        self.damage_knockback += resistance

    def apply_ranged_knockback(self, knockback_amount, direction):
        # Slightly smaller effect
        if direction == "right":
            self.vel_x = 10
            self.vel_y = -5
        else:
            self.vel_x = -10
            self.vel_y = -5
        self.damage_knockback += 0.5


#
# Attack Sprites
#
class Cube(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill((25, 25, 25))
        self.rect = self.image.get_rect()
        self.creation_time = time.time()
        self.direction = direction
        self.lifetime = CUBE_LIFETIME

        if direction == "right":
            self.rect.x = x + 120
        else:
            self.rect.x = x - 120
        self.rect.y = y

    def update(self):
        if (time.time() - self.creation_time) >= self.lifetime:
            self.kill()

class upperCube(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill((25, 25, 25))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y - 130
        self.creation_time = time.time()
        self.direction = direction
        self.lifetime = CUBE_LIFETIME

    def update(self):
        if (time.time() - self.creation_time) >= self.lifetime:
            self.kill()

class lowerCube(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill((25, 25, 25))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y + 130
        self.creation_time = time.time()
        self.direction = direction
        self.lifetime = CUBE_LIFETIME

    def update(self):
        if (time.time() - self.creation_time) >= self.lifetime:
            self.kill()

class rangeCube(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, player_type):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.direction = direction
        self.player_type = player_type if player_type else ""
        self.creation_time = time.time()
        self.lifetime = RANGED_LENGTH

        if direction == "right":
            self.rect.x = x + PLAYER_WIDTH
        else:
            self.rect.x = x - 10

        # Put it roughly in the middle of player vertically
        self.rect.y = y + (PLAYER_HEIGHT // 2) - 5

        # "tyler" arcs upward
        # (Comparing lowercase to match your snippet's logic)
        if self.player_type.lower() == "tyler":
            self.vel_y = -5
        else:
            self.vel_y = 0

    def update(self):
        if (time.time() - self.creation_time) >= self.lifetime:
            self.kill()
            return

        # If "tyler", bullet arcs upward due to gravity
        if self.player_type and self.player_type.lower() == "tyler":
            self.vel_y += GRAVITY
            self.rect.y += self.vel_y

        # Horizontal speed
        speed = 20
        if self.direction == "right":
            self.rect.x += speed
        else:
            self.rect.x -= speed


#
# Main game loop
#
def main(p1_char, p2_char):
    """
    Launches the game with:
      - Player 1 on Joystick #0
      - Player 2 on Joystick #1
      - Double jump logic from your snippet
      - Invisible platforms
    """
    clock = pygame.time.Clock()
    pygame.joystick.init()

    # Create Players
    player1 = Player(
        x = SCREEN_WIDTH // 3,
        y = PLATFORM_MAIN_Y - PLAYER_HEIGHT,
        color = RED,
        playable_character = p1_char,   # e.g. "tyler" or "Tyler"
        joystick_index = 0
    )
    player2 = Player(
        x = 2 * SCREEN_WIDTH // 3,
        y = PLATFORM_MAIN_Y - PLAYER_HEIGHT,
        color = GREEN,
        playable_character = p2_char,
        joystick_index = 1
    )

    all_sprites = pygame.sprite.Group(player1, player2)
    attack_sprites = pygame.sprite.Group()

    # Create invisible scaled platforms
    platform_main = Platform(
        PLATFORM_MAIN_X,
        PLATFORM_MAIN_Y,
        PLATFORM_MAIN_WIDTH,
        PLATFORM_MAIN_HEIGHT
    )
    platform_air_1 = Platform(
        PLATFORM_AIR_1_X,
        PLATFORM_AIR_1_Y,
        PLATFORM_AIR_WIDTH,
        PLATFORM_AIR_HEIGHT
    )
    platform_air_2 = Platform(
        PLATFORM_AIR_2_X,
        PLATFORM_AIR_2_Y,
        PLATFORM_AIR_WIDTH,
        PLATFORM_AIR_HEIGHT
    )

    platforms = pygame.sprite.Group(platform_main, platform_air_1, platform_air_2)

    # Font for displaying lives
    font = pygame.font.Font("assets/fonts/smash_font.ttf", int(SCREEN_HEIGHT / 18))

    running = True
    while running:
        current_time = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Press ESC to quit
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Player 1 joystick input
        player1.handle_joystick_input(attack_sprites, current_time)
        # Player 2 joystick input
        player2.handle_joystick_input(attack_sprites, current_time)

        # Off-screen check → respawn
        for p in [player1, player2]:
            off_screen_y = (p.rect.y > SCREEN_HEIGHT + SCREEN_HEIGHT // 2) or (p.rect.y < -SCREEN_HEIGHT // 2)
            off_screen_x = (p.rect.x < -SCREEN_WIDTH // 2) or (p.rect.x > SCREEN_WIDTH + SCREEN_WIDTH // 2)
            if off_screen_y or off_screen_x:
                if p.lives > 1:
                    p.respawn()
                else:
                    all_sprites.remove(p)
                    p.lives = 0

        # Update physics
        player1.update_physics(platforms)
        player2.update_physics(platforms)

        # Update attack sprites
        attack_sprites.update()

        # Collision check with attacks → apply knockback
        for p in [player1, player2]:
            collided = pygame.sprite.spritecollide(p, attack_sprites, dokill=True)
            for atk in collided:
                direction = atk.direction
                if isinstance(atk, Cube):
                    p.apply_knockback(BASE_KNOCKBACK, direction)
                elif isinstance(atk, upperCube):
                    p.apply_upper_knockback(BASE_KNOCKBACK, direction)
                elif isinstance(atk, lowerCube):
                    p.apply_lower_knockback(BASE_KNOCKBACK, direction)
                elif isinstance(atk, rangeCube):
                    p.apply_ranged_knockback(BASE_KNOCKBACK, direction)

        # Render
        SCREEN.blit(background, (0, 0))

        # Draw players and attacks
        all_sprites.draw(SCREEN)
        attack_sprites.draw(SCREEN)

        # Draw invisible platforms (still needed for collisions)
        platforms.draw(SCREEN)

        # Display lives
        lives_text1 = font.render(f"P1 Lives: {player1.lives}", True, RED)
        lives_text2 = font.render(f"P2 Lives: {player2.lives}", True, GREEN)

        text_rect1 = lives_text1.get_rect(
            center=((SCREEN_WIDTH // 2) + SCREEN_WIDTH // 15, SCREEN_HEIGHT - SCREEN_HEIGHT // 15)
        )
        text_rect2 = lives_text2.get_rect(
            center=((SCREEN_WIDTH // 2) - SCREEN_WIDTH // 15, SCREEN_HEIGHT - SCREEN_HEIGHT // 15)
        )

        SCREEN.blit(lives_text1, text_rect1)
        SCREEN.blit(lives_text2, text_rect2)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()
