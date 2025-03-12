"""
TO DO LIST:

* fikse forskjellige ranged attacks
* tracker for spilleren hvis spilleren er utenfor skjermen
* Prosent damage for spilleren (knockback)
    VARIABLE: knockback_amount
    knockback_amount skal vises på skjermen
* Ultimates

"""
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
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE  = (0, 0, 255)

"""
Platform størrelser
"""
PLATFORM_WIDTH = int(SCREEN_WIDTH / 1.3)
PLATFORM_HEIGHT = 100
PLATFORM_X = (SCREEN_WIDTH - PLATFORM_WIDTH) // 2
PLATFORM_Y = SCREEN_HEIGHT - 200

"""Mini platformer"""
MINI_PLATFORM_WIDTH = 330
MINI_PLATFORM_HEIGHT = 30
MINI_PLATFORM_X = 425
MINI_PLATFORM_Y = 645

MINI_PLATFORM_WIDTH_2 = 330
MINI_PLATFORM_HEIGHT_2 = 30
MINI_PLATFORM_X_2 = 1180
MINI_PLATFORM_Y_2 = 645

# Max spillere: fra 2 til 3
AMOUNT_OF_PLAYERS = 2

# Konstanter
PLAYER_WIDTH = 100
PLAYER_HEIGHT = 100
PLAYER_SPEED = 10
GRAVITY = 0.5
JUMP_STRENGTH = 13
MAX_LIVES = 3
FALL_FAST = 15

# Attack konstant
ATTACK_COOLDOWN = 0.5
RANGED_COOLDOWN = 0.5
RANGED_LENGTH = 1
RANGED_RELOAD = 3
CUBE_LIFETIME = 0.01
BASE_KNOCKBACK = 15
KNOCKBACK_RESISTANCE_FACTOR = 0.1

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
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

        # vektor og hopp
        self.vel_y = 0
        self.vel_x = 0
        self.on_ground = False
        self.can_double_jump = True
        self.jump_count = 0
        self.jump_button_pressed = False  # to prevent instant double-jumps

        # player stats
        self.lives = MAX_LIVES
        self.playable_character = playable_character  # e.g., "tyler"
        self.damage_knockback = 1  # used for knockback progression

        # attack og retning
        self.last_attack_time = 0
        self.last_ranged_time = 0
        self.last_direction = "none"  # "left" or "right"
        self.bullet_count = RANGED_RELOAD
        self.can_shoot = True

        self.controls = controls

    def update(self, platforms, joystick = None):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        self.rect.x += self.vel_x
        self.vel_x *= 0.9

        # 🎮 Joystick movement
        if joystick:
            axis_x = joystick.get_axis(0)  # Left Stick X-axis
            if axis_x < -0.5:
                self.move_left()
            elif axis_x > 0.5:
                self.move_right()

            if joystick.get_button(0):  # X button (Jump)
                self.jump()
            if joystick.get_button(1):  # Circle button (Fast Fall)
                self.fall()
            if joystick.get_button(2):  # Square button (Attack)
                self.attack()
            if joystick.get_button(3):  # Triangle button (Upper Attack)
                self.upperattack()

        """Platform Collision Check"""
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # If landing on top
                if self.vel_y > 0 and (self.rect.bottom <= platform.rect.bottom):
                    self.rect.bottom = platform.rect.top
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
        """Force a faster fall"""
        self.vel_y = 0
        self.rect.y += FALL_FAST

    def respawn(self):
        """Respawn Player når Player er utenfor skjermen"""
        self.rect.x = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2
        self.rect.y = PLATFORM_Y - PLAYER_HEIGHT
        self.vel_y = 0
        self.vel_x = 0
        self.lives -= 1
        self.damage_knockback = 1
        self.can_double_jump = True

    def attack(self, attack_sprites, current_time):
        """X-akse attack"""
        if (current_time - self.last_attack_time) >= ATTACK_COOLDOWN:
            cube = Cube(self.rect.x, self.rect.y, self.last_direction)
            attack_sprites.add(cube)
            self.last_attack_time = current_time

    def upperattack(self, attack_sprites, current_time):
        """Y-akse i player > 0 attack"""
        if (current_time - self.last_attack_time) >= ATTACK_COOLDOWN:
            upper_cube = upperCube(self.rect.x, self.rect.y, self.last_direction)
            attack_sprites.add(upper_cube)
            self.last_attack_time = current_time

    def lowerattack(self, attack_sprites, current_time):
        """Y-akse i player < 0 attack"""
        if (current_time - self.last_attack_time) >= ATTACK_COOLDOWN:
            lower_cube = lowerCube(self.rect.x, self.rect.y, self.last_direction)
            attack_sprites.add(lower_cube)
            self.last_attack_time = current_time

    def rangedattack(self, attack_sprites, current_time):
        """Range attack"""
        if self.bullet_count <= 0:
            self.bullet_count = 0

        if (current_time - self.last_ranged_time) >= RANGED_COOLDOWN and self.can_shoot:
            range_cube = rangeCube(self.rect.x, self.rect.y, self.last_direction, self.playable_character)
            attack_sprites.add(range_cube)
            self.bullet_count -= 1
            self.last_ranged_time = current_time

            if self.bullet_count <= 0:
                self.can_shoot = False

        """Etter et vis lengde av tid og skudd"""
        if (current_time - self.last_ranged_time) >= RANGED_LENGTH:
            self.bullet_count = RANGED_RELOAD
            self.can_shoot = True

    """# ------------------ Knockback Metoder ------------------"""
    def apply_knockback(self, knockback_amount, direction):
        """Generic side-attack knockback."""
        # The more the player is hit, the larger the knockback
        resistance = 1 * (1 + KNOCKBACK_RESISTANCE_FACTOR * self.damage_knockback)
        knockback_amount *= resistance

        if direction == "right":
            self.vel_x = knockback_amount
            self.vel_y = -knockback_amount * 0.4
        else:  # direction == "left"
            self.vel_x = -knockback_amount
            self.vel_y = -knockback_amount * 0.4

        self.damage_knockback += resistance

    def apply_upper_knockback(self, knockback_amount, direction):
        resistance = 1 * (1 + KNOCKBACK_RESISTANCE_FACTOR * self.damage_knockback)
        knockback_amount *= resistance

        if direction == "right":
            self.vel_x = knockback_amount * 0.3
            self.vel_y = -knockback_amount * 0.4
        else:
            self.vel_x = -knockback_amount * 0.3
            self.vel_y = -knockback_amount * 0.4

        self.damage_knockback += resistance

    def apply_lower_knockback(self, knockback_amount, direction):
        resistance = 1 * (1 + KNOCKBACK_RESISTANCE_FACTOR * self.damage_knockback)
        knockback_amount *= resistance

        if direction == "right":
            self.vel_x = knockback_amount * 0.3
            self.vel_y = knockback_amount * 0.5
        else:
            self.vel_x = -knockback_amount * 0.3
            self.vel_y = knockback_amount * 0.5

        self.damage_knockback += resistance

    def apply_ranged_knockback(self, knockback_amount, direction):
        """Knockback specifically for ranged attacks (slightly weaker)."""
        if direction == "right":
            self.vel_x = 10
            self.vel_y = -5
        else:
            self.vel_x = -10
            self.vel_y = -5

        self.damage_knockback += 0.5

"""# ------------------- Attack Sprite Classes -------------------"""

class Cube(pygame.sprite.Sprite):
    """Attack hitbox."""
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill((25, 25, 25))
        self.rect = self.image.get_rect()
        self.creation_time = time.time()
        self.direction = direction  # store the direction in the sprite

        if direction == "right":
            self.rect.x = x + 120
        elif direction == "left":
            self.rect.x = x - 120
        self.rect.y = y
        self.lifetime = CUBE_LIFETIME

    def update(self):
        if (time.time() - self.creation_time) >= self.lifetime:
            self.kill()

class upperCube(pygame.sprite.Sprite):
    """Attack hitbox."""
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
    """Attack hitbox."""
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
    """Attack hitbox."""
    def __init__(self, x, y, direction, player_type):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.direction = direction
        self.player_type = player_type

        if direction == "right":
            self.rect.x = x + PLAYER_WIDTH
        else:
            self.rect.x = x - 10
        """Fra Player center + x ^^^^^ """
        self.rect.y = y + (PLAYER_HEIGHT // 2) - 5

        self.creation_time = time.time()
        self.lifetime = RANGED_LENGTH

        """FOR TYLER THE CREATOR"""
        self.vel_y = -5 if (player_type == "tyler") else 0

    def update(self):
        if (time.time() - self.creation_time) >= self.lifetime:
            self.kill()
            return

        """FOR "tyler" """
        if self.player_type == "tyler":
            self.vel_y += GRAVITY
            self.rect.y += self.vel_y

        """Hastighet for ranged"""
        speed = 20
        if self.direction == "right":
            self.rect.x += speed
        else:
            self.rect.x -= speed

"""# ------------------- Main Game Loop -------------------"""

def main():
    clock = pygame.time.Clock()

    """LAGE SPILLERE"""
    player1 = Player(
        SCREEN_WIDTH // 4, PLATFORM_Y - PLAYER_HEIGHT, RED,
        {
            "left": pygame.K_a,
            "right": pygame.K_d,
            "jump": pygame.K_w,
            "fall": pygame.K_s,
            "attack": pygame.K_x,
            "upperattack": pygame.K_c,
            "lowerattack": pygame.K_v,
            "rangeattack": pygame.K_z,
        },
        playable_character="tyler"
    )
    player2 = Player(
        SCREEN_WIDTH // 2, PLATFORM_Y - PLAYER_HEIGHT, GREEN,
        {
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "jump": pygame.K_UP,
            "fall": pygame.K_DOWN,
            "attack": pygame.K_m,
            "upperattack": pygame.K_n,
            "lowerattack": pygame.K_b,
            "rangeattack": pygame.K_COMMA
        },
        playable_character=None
    )
    player3 = Player(
        3 * SCREEN_WIDTH // 4, PLATFORM_Y - PLAYER_HEIGHT, BLUE,
        {
            "left": pygame.K_j,
            "right": pygame.K_l,
            "jump": pygame.K_i,
            "fall": pygame.K_k,
            "attack": pygame.K_u,
            "upperattack": pygame.K_y,
            "lowerattack": pygame.K_t,
            "rangeattack": pygame.K_h
        },
        playable_character=None
    )

    """Hvor mange spillere"""
    players = []
    if AMOUNT_OF_PLAYERS == 2:
        players = [player1, player2]
    elif AMOUNT_OF_PLAYERS == 3:
        players = [player1, player2, player3]

    """Sprite groups"""
    all_sprites = pygame.sprite.Group()
    attack_sprites = pygame.sprite.Group()
    all_sprites.add(*players)

    """PLATFORMER"""
    platform_main = Platform(PLATFORM_X, PLATFORM_Y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
    platform_small1 = Platform(MINI_PLATFORM_X, MINI_PLATFORM_Y, MINI_PLATFORM_WIDTH, MINI_PLATFORM_HEIGHT)
    platform_small2 = Platform(MINI_PLATFORM_X_2, MINI_PLATFORM_Y_2, MINI_PLATFORM_WIDTH_2, MINI_PLATFORM_HEIGHT_2)
    platforms = pygame.sprite.Group(platform_main, platform_small1, platform_small2)

    """FONT FOR LIVES"""
    font = pygame.font.Font("assets/fonts/smash_font.ttf", int(SCREEN_HEIGHT/18))

    running = True
    while running:
        current_time = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # 🎮 Detect PS4 Controller
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
        else:
            joystick = None  # No controller detected


        """INPUT"""
        keys = pygame.key.get_pressed()
        for player in players:
            """A og D, <- og ->"""
            if keys[player.controls["left"]]:
                player.move_left()
            if keys[player.controls["right"]]:
                player.move_right()

            """JUMP"""
            if keys[player.controls["jump"]]:
                if not player.jump_button_pressed:
                    player.jump()
                player.jump_button_pressed = True
            else:
                player.jump_button_pressed = False

            """FAST FALL"""
            if keys[player.controls["fall"]]:
                player.fall()

            """ATTACK"""
            if keys[player.controls["attack"]]:
                player.attack(attack_sprites, current_time)
            if keys[player.controls["upperattack"]]:
                player.upperattack(attack_sprites, current_time)
            if keys[player.controls["lowerattack"]]:
                player.lowerattack(attack_sprites, current_time)
            if keys[player.controls["rangeattack"]]:
                player.rangedattack(attack_sprites, current_time)

            """OUT OF BOUNDS?"""
            off_screen_y = (
                player.rect.y > SCREEN_HEIGHT + SCREEN_HEIGHT // 2 or
                player.rect.y < -SCREEN_HEIGHT // 2
            )
            off_screen_x = (
                player.rect.x < -SCREEN_WIDTH // 2 or
                player.rect.x > SCREEN_WIDTH + SCREEN_WIDTH // 2
            )
            if off_screen_y or off_screen_x:
                if player.lives > 1:
                    player.respawn()
                else:
                    all_sprites.remove(player)
                    if player in players:
                        players.remove(player)
                    player.lives = 0

        """Oppdater spiller (gravity, kollisjoner, platformer)"""
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
        else:
            joystick = None  # No controller connected
            
        for player in players:
            player.update(platforms, joystick)

        """Oppdater ATTACK (livstid+)"""
        attack_sprites.update()

        """Kollisjon check (attacks)"""
        collided_pairs = []
        for player in players:
            collided_attacks = pygame.sprite.spritecollide(player, attack_sprites, dokill=True)
            for attack_sprite in collided_attacks:
                # Use the attack sprite's stored direction
                direction = attack_sprite.direction
                if isinstance(attack_sprite, Cube):
                    player.apply_knockback(BASE_KNOCKBACK, direction)
                elif isinstance(attack_sprite, upperCube):
                    player.apply_upper_knockback(BASE_KNOCKBACK, direction)
                elif isinstance(attack_sprite, lowerCube):
                    player.apply_lower_knockback(BASE_KNOCKBACK, direction)
                elif isinstance(attack_sprite, rangeCube):
                    player.apply_ranged_knockback(BASE_KNOCKBACK, direction)

        """Draw"""
        SCREEN.blit(background, (0, 0))
        all_sprites.draw(SCREEN)
        attack_sprites.draw(SCREEN)

        """Draw Lives Tekst"""
        if AMOUNT_OF_PLAYERS == 2 and len(players) == 2:
            p1, p2 = players
            lives_text1 = font.render(f"P1 Lives: {p1.lives}", True, RED)
            lives_text2 = font.render(f"P2 Lives: {p2.lives}", True, GREEN)
            text_rect1 = lives_text1.get_rect(center=((SCREEN_WIDTH // 2) + SCREEN_WIDTH // 15,
                                                       SCREEN_HEIGHT - SCREEN_HEIGHT // 15))
            text_rect2 = lives_text2.get_rect(center=((SCREEN_WIDTH // 2) - SCREEN_WIDTH // 15,
                                                       SCREEN_HEIGHT - SCREEN_HEIGHT // 15))
            SCREEN.blit(lives_text1, text_rect1)
            SCREEN.blit(lives_text2, text_rect2)

        elif AMOUNT_OF_PLAYERS == 3 and len(players) == 3:
            p1, p2, p3 = players
            lives_text1 = font.render(f"P1 Lives: {p1.lives}", True, RED)
            lives_text2 = font.render(f"P2 Lives: {p2.lives}", True, GREEN)
            lives_text3 = font.render(f"P3 Lives: {p3.lives}", True, BLUE)
            text_rect1 = lives_text1.get_rect(center=((SCREEN_WIDTH // 2) + SCREEN_WIDTH // 8,
                                                       SCREEN_HEIGHT - SCREEN_HEIGHT // 15))
            text_rect2 = lives_text2.get_rect(center=(SCREEN_WIDTH // 2,
                                                       SCREEN_HEIGHT - SCREEN_HEIGHT // 15))
            text_rect3 = lives_text3.get_rect(center=((SCREEN_WIDTH // 2) - SCREEN_WIDTH // 8,
                                                       SCREEN_HEIGHT - SCREEN_HEIGHT // 15))
            SCREEN.blit(lives_text1, text_rect1)
            SCREEN.blit(lives_text2, text_rect2)
            SCREEN.blit(lives_text3, text_rect3)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
