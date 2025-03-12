import pygame
import sys
import time

pygame.init()
pygame.font.init()

info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)

background_img = pygame.image.load("Assets/Images/background_2.png")
background = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

WHITE = (255, 255, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE  = (0, 0, 255)

# Platform sizes
PLATFORM_WIDTH = int(SCREEN_WIDTH / 1.3)
PLATFORM_HEIGHT = 100
PLATFORM_X = (SCREEN_WIDTH - PLATFORM_WIDTH) // 2
PLATFORM_Y = SCREEN_HEIGHT - 200

MINI_PLATFORM_WIDTH = 330
MINI_PLATFORM_HEIGHT = 30
MINI_PLATFORM_X = 425
MINI_PLATFORM_Y = 645

MINI_PLATFORM_WIDTH_2 = 330
MINI_PLATFORM_HEIGHT_2 = 30
MINI_PLATFORM_X_2 = 1180
MINI_PLATFORM_Y_2 = 645

# Player/game constants
PLAYER_WIDTH = 100
PLAYER_HEIGHT = 100
PLAYER_SPEED = 10
GRAVITY = 0.5
JUMP_STRENGTH = 13
MAX_LIVES = 3
FALL_FAST = 15

# Attack constants
ATTACK_COOLDOWN = 0.5
RANGED_COOLDOWN = 0.5
RANGED_LENGTH = 1
RANGED_RELOAD = 3
CUBE_LIFETIME = 0.01
BASE_KNOCKBACK = 15
KNOCKBACK_RESISTANCE_FACTOR = 0.1

# Map names to images
CHARACTER_IMAGES = {
    "King Von":   "assets/images/kingvon.jpg",
    "Tyler":      "assets/images/tyler.jpg",
    "Chief Keef": "assets/images/cheif.jpg",
    "Hector":     "assets/images/hector.jpg",
}

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((0, 0, 0, 0))  # Invisible
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color, controls, playable_character):
        super().__init__()
        # Load image if recognized
        image_path = CHARACTER_IMAGES.get(playable_character, None)
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
        self.on_ground = False
        self.can_double_jump = True
        self.jump_count = 0
        self.jump_button_pressed = False

        # Stats
        self.lives = MAX_LIVES
        self.playable_character = playable_character
        self.damage_knockback = 1

        # Attacks
        self.last_attack_time = 0
        self.last_ranged_time = 0
        self.last_direction = "none"
        self.bullet_count = RANGED_RELOAD
        self.can_shoot = True

        self.controls = controls

    def update(self, platforms):
        # Gravity
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        # Friction
        self.rect.x += self.vel_x
        self.vel_x *= 0.9

        # Collisions with platforms
        self.on_ground = False
        for p in platforms:
            if self.rect.colliderect(p.rect):
                # Landing on top
                if self.vel_y > 0 and self.rect.bottom <= p.rect.bottom:
                    self.rect.bottom = p.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.jump_count = 0
                    self.can_double_jump = True

    def move_left(self):
        self.rect.x -= PLAYER_SPEED
        self.last_direction = "left"

    def move_right(self):
        self.rect.x += PLAYER_SPEED
        self.last_direction = "right"

    def jump(self):
        if self.on_ground:
            self.vel_y = -JUMP_STRENGTH
            self.jump_count += 1
            self.jump_button_pressed = True
        elif self.can_double_jump and self.jump_count < 2 and not self.jump_button_pressed:
            self.vel_y = -JUMP_STRENGTH
            self.jump_count += 1
            self.can_double_jump = False

    def fall(self):
        self.vel_y = 0
        self.rect.y += FALL_FAST

    def respawn(self):
        self.rect.x = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2
        self.rect.y = PLATFORM_Y - PLAYER_HEIGHT
        self.vel_x = 0
        self.vel_y = 0
        self.lives -= 1
        self.damage_knockback = 1
        self.can_double_jump = True

    def attack(self, attack_sprites, current_time):
        if current_time - self.last_attack_time >= ATTACK_COOLDOWN:
            cube = Cube(self.rect.x, self.rect.y, self.last_direction)
            attack_sprites.add(cube)
            self.last_attack_time = current_time

    def upperattack(self, attack_sprites, current_time):
        if current_time - self.last_attack_time >= ATTACK_COOLDOWN:
            upper_cube = upperCube(self.rect.x, self.rect.y, self.last_direction)
            attack_sprites.add(upper_cube)
            self.last_attack_time = current_time

    def lowerattack(self, attack_sprites, current_time):
        if current_time - self.last_attack_time >= ATTACK_COOLDOWN:
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

        if (current_time - self.last_ranged_time) >= RANGED_LENGTH:
            self.bullet_count = RANGED_RELOAD
            self.can_shoot = True

    # Knockback
    def apply_knockback(self, knockback_amount, direction):
        import math
        resistance = (1 + KNOCKBACK_RESISTANCE_FACTOR * self.damage_knockback)
        knockback = knockback_amount * resistance
        if direction == "right":
            self.vel_x = knockback
            self.vel_y = -knockback * 0.4
        else:
            self.vel_x = -knockback
            self.vel_y = -knockback * 0.4
        self.damage_knockback += resistance

    def apply_upper_knockback(self, knockback_amount, direction):
        resistance = (1 + KNOCKBACK_RESISTANCE_FACTOR * self.damage_knockback)
        knockback = knockback_amount * resistance
        if direction == "right":
            self.vel_x = knockback * 0.3
            self.vel_y = -knockback * 0.4
        else:
            self.vel_x = -knockback * 0.3
            self.vel_y = -knockback * 0.4
        self.damage_knockback += resistance

    def apply_lower_knockback(self, knockback_amount, direction):
        resistance = (1 + KNOCKBACK_RESISTANCE_FACTOR * self.damage_knockback)
        knockback = knockback_amount * resistance
        if direction == "right":
            self.vel_x = knockback * 0.3
            self.vel_y = knockback * 0.5
        else:
            self.vel_x = -knockback * 0.3
            self.vel_y = knockback * 0.5
        self.damage_knockback += resistance

    def apply_ranged_knockback(self, knockback_amount, direction):
        if direction == "right":
            self.vel_x = 10
            self.vel_y = -5
        else:
            self.vel_x = -10
            self.vel_y = -5
        self.damage_knockback += 0.5


# Attack Sprites
class Cube(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill((25, 25, 25))
        self.rect = self.image.get_rect()
        self.direction = direction
        self.creation_time = time.time()
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
        self.direction = direction
        self.creation_time = time.time()
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
        self.direction = direction
        self.creation_time = time.time()
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
        self.player_type = player_type
        self.creation_time = time.time()
        self.lifetime = RANGED_LENGTH

        if direction == "right":
            self.rect.x = x + PLAYER_WIDTH
        else:
            self.rect.x = x - 10

        self.rect.y = y + (PLAYER_HEIGHT // 2) - 5
        self.vel_y = -5 if (player_type == "Tyler") else 0

    def update(self):
        # expire after some time
        if (time.time() - self.creation_time) >= self.lifetime:
            self.kill()
            return

        # if "Tyler", bullet arcs upward due to gravity
        if self.player_type == "Tyler":
            self.vel_y += GRAVITY
            self.rect.y += self.vel_y

        # horizontal movement
        speed = 20
        if self.direction == "right":
            self.rect.x += speed
        else:
            self.rect.x -= speed


def main(p1_char, p2_char):
    """
    p1_char: name of the character chosen for Player 1 (e.g. "Tyler")
    p2_char: name of the character chosen for Player 2 (e.g. "Hector")
    """
    clock = pygame.time.Clock()

    #
    # 1) Initialize and pick joysticks for each player, if available
    #
    pygame.joystick.init()
    joysticks = []
    for i in range(pygame.joystick.get_count()):
        js = pygame.joystick.Joystick(i)
        js.init()
        joysticks.append(js)

    # Force each player to have a different joystick index if possible
    joystick1 = joysticks[0] if len(joysticks) > 0 else None
    joystick2 = joysticks[1] if len(joysticks) > 1 else None

    print(f"Detected {len(joysticks)} total joystick(s).")
    if joystick1:
        print(f"Player 1 using joystick #0: {joystick1.get_name()}, instanceID={joystick1.get_instance_id()}")
    else:
        print("Player 1 has no joystick (keyboard only).")

    if joystick2:
        print(f"Player 2 using joystick #1: {joystick2.get_name()}, instanceID={joystick2.get_instance_id()}")
    else:
        print("Player 2 has no joystick (keyboard only).")

    #
    # 2) Create two players
    #
    player1 = Player(
        x=SCREEN_WIDTH // 3,
        y=PLATFORM_Y - PLAYER_HEIGHT,
        color=RED,
        controls={
            "left": pygame.K_a,
            "right": pygame.K_d,
            "jump": pygame.K_w,
            "fall": pygame.K_s,
            "attack": pygame.K_x,
            "upperattack": pygame.K_c,
            "lowerattack": pygame.K_v,
            "rangeattack": pygame.K_z,
        },
        playable_character=p1_char
    )

    player2 = Player(
        x=2 * SCREEN_WIDTH // 3,
        y=PLATFORM_Y - PLAYER_HEIGHT,
        color=GREEN,
        controls={
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "jump": pygame.K_UP,
            "fall": pygame.K_DOWN,
            "attack": pygame.K_m,
            "upperattack": pygame.K_n,
            "lowerattack": pygame.K_b,
            "rangeattack": pygame.K_COMMA
        },
        playable_character=p2_char
    )

    #
    # 3) Setup sprite groups & platforms
    #
    all_sprites = pygame.sprite.Group(player1, player2)
    attack_sprites = pygame.sprite.Group()

    platform_main = Platform(PLATFORM_X, PLATFORM_Y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
    platform_small1 = Platform(MINI_PLATFORM_X, MINI_PLATFORM_Y, MINI_PLATFORM_WIDTH, MINI_PLATFORM_HEIGHT)
    platform_small2 = Platform(MINI_PLATFORM_X_2, MINI_PLATFORM_Y_2, MINI_PLATFORM_WIDTH_2, MINI_PLATFORM_HEIGHT_2)
    platforms = pygame.sprite.Group(platform_main, platform_small1, platform_small2)

    font = pygame.font.Font("assets/fonts/smash_font.ttf", int(SCREEN_HEIGHT / 18))

    running = True
    while running:
        current_time = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        #
        # 4) Read input for Player 1
        #
        # If joystick1 is present, check its axis/buttons. Otherwise do keyboard only.
        if joystick1:
            axis_x = joystick1.get_axis(0)
            if axis_x < -0.5:
                player1.move_left()
            elif axis_x > 0.5:
                player1.move_right()

            if joystick1.get_button(0):  # jump
                player1.jump()
            if joystick1.get_button(1):  # fall
                player1.fall()
            if joystick1.get_button(2):  # attack
                player1.attack(attack_sprites, current_time)
            if joystick1.get_button(3):  # upper attack
                player1.upperattack(attack_sprites, current_time)

        # Also allow keyboard fallback
        keys = pygame.key.get_pressed()
        if keys[player1.controls["left"]]:
            player1.move_left()
        if keys[player1.controls["right"]]:
            player1.move_right()
        if keys[player1.controls["jump"]]:
            if not player1.jump_button_pressed:
                player1.jump()
            player1.jump_button_pressed = True
        else:
            player1.jump_button_pressed = False
        if keys[player1.controls["fall"]]:
            player1.fall()

        if keys[player1.controls["attack"]]:
            player1.attack(attack_sprites, current_time)
        if keys[player1.controls["upperattack"]]:
            player1.upperattack(attack_sprites, current_time)
        if keys[player1.controls["lowerattack"]]:
            player1.lowerattack(attack_sprites, current_time)
        if keys[player1.controls["rangeattack"]]:
            player1.rangedattack(attack_sprites, current_time)

        #
        # 5) Read input for Player 2
        #
        # If joystick2 is present, check axis/buttons. Otherwise do keyboard only.
        if joystick2:
            axis_x_2 = joystick2.get_axis(0)
            if axis_x_2 < -0.5:
                player2.move_left()
            elif axis_x_2 > 0.5:
                player2.move_right()

            if joystick2.get_button(0):  # jump
                player2.jump()
            if joystick2.get_button(1):  # fall
                player2.fall()
            if joystick2.get_button(2):  # attack
                player2.attack(attack_sprites, current_time)
            if joystick2.get_button(3):  # upper attack
                player2.upperattack(attack_sprites, current_time)

        # Also allow keyboard fallback
        if keys[player2.controls["left"]]:
            player2.move_left()
        if keys[player2.controls["right"]]:
            player2.move_right()
        if keys[player2.controls["jump"]]:
            if not player2.jump_button_pressed:
                player2.jump()
            player2.jump_button_pressed = True
        else:
            player2.jump_button_pressed = False
        if keys[player2.controls["fall"]]:
            player2.fall()

        if keys[player2.controls["attack"]]:
            player2.attack(attack_sprites, current_time)
        if keys[player2.controls["upperattack"]]:
            player2.upperattack(attack_sprites, current_time)
        if keys[player2.controls["lowerattack"]]:
            player2.lowerattack(attack_sprites, current_time)
        if keys[player2.controls["rangeattack"]]:
            player2.rangedattack(attack_sprites, current_time)

        #
        # 6) Handle off-screen respawn for each
        #
        for p in [player1, player2]:
            off_screen_y = p.rect.y > SCREEN_HEIGHT + SCREEN_HEIGHT // 2 or p.rect.y < -SCREEN_HEIGHT // 2
            off_screen_x = p.rect.x < -SCREEN_WIDTH // 2 or p.rect.x > SCREEN_WIDTH + SCREEN_WIDTH // 2
            if off_screen_y or off_screen_x:
                if p.lives > 1:
                    p.respawn()
                else:
                    all_sprites.remove(p)
                    p.lives = 0

        #
        # 7) Update players (apply gravity, collisions, etc.)
        #
        player1.update(platforms)
        player2.update(platforms)

        #
        # 8) Update attack sprites
        #
        attack_sprites.update()

        #
        # 9) Check collisions (knockback)
        #
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

        #
        # 10) Draw everything
        #
        SCREEN.blit(background, (0, 0))
        all_sprites.draw(SCREEN)
        attack_sprites.draw(SCREEN)

        # Show P1 vs. P2 lives
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


if __name__ == "__main__":
    # Test defaults
    main("Tyler", "Hector")
