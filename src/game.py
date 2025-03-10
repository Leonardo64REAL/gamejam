"""
TO DO LIST:

* fikse forskjellige ranged attacks
* maps
* tracker for spilleren hvis spilleren er utenfor skjermen
* Prosent damage for spilleren (knockback)
    VARIABLE: knockback_amount
    knockback_amount skal vises på skjermen

"""

import pygame
import sys
import time

pygame.init()
pygame.font.init()

# henter skjerm informasjon, samtidig fullskjerm
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)

# farger
WHITE = (255, 255, 255) 
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# platformen sin størrelse.
PLATFORM_WIDTH = SCREEN_WIDTH // 2
PLATFORM_HEIGHT = 100
PLATFORM_X = (SCREEN_WIDTH - PLATFORM_WIDTH) // 2
PLATFORM_Y = SCREEN_HEIGHT - 200

# Hvor mange spillere (maks 3)
AMOUNT_OF_PLAYERS = 2

# hoved player innstillinger (navnet forteller)
PLAYER_WIDTH = 100
PLAYER_HEIGHT = 100
PLAYER_SPEED = 9
GRAVITY = 0.5
JUMP_STRENGTH = 13
MAX_LIVES = 3

# player y+ bevegelse (ikke gravity eller fysikk)
FALL_FAST = 15

# attack cooldown (sekunder)
ATTACK_COOLDOWN = 0.5
RANGED_COOLDOWN = 0.5

# ikke pixel lengde, men sekunder lengde
# v = s/t -> s = v*t
RANGED_LENGTH = 1
RANGED_RELOAD = 3 # hvor mange skudd en spiller har før reload

# attack hitbox sin frametime
CUBE_LIFETIME = 0.01  # Cube will disappear after 0.1 seconds

# knockback konstanter
BASE_KNOCKBACK = 15  # base knockback
KNOCKBACK_RESISTANCE_FACTOR = 0.1  # *0.1

"""
SPILLER TYPER.
class Player innstillinger
"""

player_class_type = ["king_von", "tyler", "chief", "hector"]

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color, controls, playable_character):
        super().__init__()

        # Spiller
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # velocity
        self.vel_y = 0
        self.vel_x = 0

        # jump mekanikk
        self.on_ground = False
        self.can_double_jump = True
        self.jump_count = 0  # teller jumps for dobbel (scaler ikke over, bare 1 og 2)
        self.jump_button_pressed = False  # fix til instant dobbel hopp "bug"

        self.lives = MAX_LIVES  # Initialize lives
        self.controls = controls  # Control keys for this player

        # attack variabler
        self.last_attack_time = 0 # (sekunder)
        self.last_ranged_time = 0 # (sekunder)
        self.last_direction = "none"  # retning for attack/ranged
        self.damage_knockback = 1  # EKTE vel_x og vel_y resistans for knockback (ikke rediger)
        self.can_shoot = True
        self.bullet_count = 3
        
        # knockback konstant
        self.resistance = 1
        self.total_damage = 0 # knockback verdi som vises på skjermen
        self.playable_character = playable_character # player types (king von, tyler, chief, hector)

    def update(self, platforms):
        # GRAVITY
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        # Horisontal knockback
        self.rect.x += self.vel_x
        self.vel_x *= 0.9  # luftmotstand/friksjon

        # sjekker hvis player er på bakken
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:  # faller

                    # nullstiller hopping
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.jump_count = 0  
                    self.can_double_jump = True

    def jump(self):
        if self.on_ground:
            self.vel_y = -JUMP_STRENGTH
            self.jump_count += 1
            self.jump_button_pressed = True  # Jump button is pressed
        elif self.can_double_jump and self.jump_count < 2 and not self.jump_button_pressed:
            # lar dobbel hopp skje hvis hopp knappen har blitt sluppet før
            self.vel_y = -JUMP_STRENGTH
            self.jump_count += 1
            self.can_double_jump = False  # skrur av dobbel hopp etter andre hopp

    def move_left(self):
        self.rect.x -= PLAYER_SPEED
        self.last_direction = "left"

    def move_right(self):
        self.rect.x += PLAYER_SPEED
        self.last_direction = "right"

    def fall(self):
        self.vel_y = 0
        self.rect.y += FALL_FAST

    def respawn(self):
        """ Setter opp player som falt ut av mappet inn i spillet"""
        self.rect.x = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2
        self.rect.y = PLATFORM_Y - PLAYER_HEIGHT
        self.vel_y = 0
        self.vel_x = 0
        self.lives -= 1  # Lose a life
        self.damage_percentage = 0
        self.resistance = 1
        self.damage_knockback = 1
    
    """
    ATTACK:

    1. Skaper ATTACK objektet i "all_sprites"
    2. Sjekker om objekten har stått lengre enn ATTACK_COOLDOWN
    
    """

    def attack(self, all_sprites):
        """Create a cube at the player's position if the cooldown has passed."""
        current_time = time.time()
        if current_time - self.last_attack_time >= ATTACK_COOLDOWN:
            cube = Cube(self.rect.x, self.rect.y, self.image.get_at((0, 0)), self.last_direction)
            all_sprites.add(cube)
            self.last_attack_time = current_time
    
    def upperattack(self, all_sprites):
        current_time = time.time()
        if current_time - self.last_attack_time >= ATTACK_COOLDOWN:
            upper_cube = upperCube(self.rect.x, self.rect.y, self.image.get_at((0,0)), self.last_direction)
            all_sprites.add(upper_cube)
            self.last_attack_time = current_time
    
    def lowerattack(self, all_sprites):
        current_time = time.time()
        if current_time - self.last_attack_time >= ATTACK_COOLDOWN:
            lower_cube = lowerCube(self.rect.x, self.rect.y, self.image.get_at((0,0)), self.last_direction)
            all_sprites.add(lower_cube)
            self.last_attack_time = current_time
    
    def rangedattack(self, all_sprites, playertype):
        current_time = time.time()
        if self.bullet_count <= 0:
            self.bullet_count = 0
        if current_time - self.last_ranged_time >= RANGED_COOLDOWN and self.can_shoot:
            range_cube = rangeCube(self.rect.x, self.rect.y, self.image.get_at((0,0)), self.last_direction, playertype)
            self.bullet_count -= 1
            all_sprites.add(range_cube)
            self.last_ranged_time = current_time
            if self.bullet_count == 0:
                self.can_shoot = False
        if current_time - self.last_attack_time >= RANGED_COOLDOWN + RANGED_LENGTH:
            self.bullet_count = 3
            self.can_shoot = True
    
    """
    KNOCKBACK:

    1. Lager bare knockback til spilleren
    2. Regner ut resistance for spilleren og legger til på prosenten.

    """

    def apply_knockback(self, knockback_amount, direction):
        """Apply knockback to the player."""
        resistance = 1 * (1  + KNOCKBACK_RESISTANCE_FACTOR * self.damage_knockback)
        knockback_amount *= resistance
        temp = -knockback_amount

        """Sett knockback"""
        if direction == "right":
            self.vel_x = knockback_amount
            self.vel_y = -knockback_amount*0.4
        elif direction == "left":
            self.vel_x = temp
            self.vel_y = -knockback_amount*0.4
        
        self.damage_knockback += resistance
    
    def apply_upper_knockback(self, knockback_amount, direction):
        resistance = 1 * (1  + KNOCKBACK_RESISTANCE_FACTOR * self.damage_knockback)
        knockback_amount *= resistance
        temp = -knockback_amount

        """Sett knockback"""
        if direction == "right":
            self.vel_x = knockback_amount*0.3
            self.vel_y = -knockback_amount*0.4
        elif direction == "left":
            self.vel_x = temp*0.3
            self.vel_y = -knockback_amount*0.4
        
        self.damage_knockback += resistance
    
    def apply_lower_knockback(self, knockback_amount, direction):
        resistance = 1 * (1  + KNOCKBACK_RESISTANCE_FACTOR * self.damage_knockback)
        knockback_amount *= resistance
        temp = -knockback_amount

        """Sett knockback"""
        if direction == "right":
            self.vel_x = knockback_amount*0.3
            self.vel_y = knockback_amount*0.5
        elif direction == "left":
            self.vel_x = temp*0.3
            self.vel_y = knockback_amount*0.5
        
        self.damage_knockback += resistance
    
    def apply_ranged_knockback(self, knockback_amount, direction):
        resistance = 1 * (1  + KNOCKBACK_RESISTANCE_FACTOR * self.damage_knockback)
        knockback_amount *= resistance
        temp = -knockback_amount

        """Sett knockback"""
        if direction == "right":
            self.vel_x = 10
            self.vel_y = -5
        elif direction == "left":
            self.vel_x = -10
            self.vel_y = -5
        
        self.damage_knockback += resistance/2

"""

RANGED ATTACK:
Denne skal være basert på de ulike karakterene


"""

class rangeCube(pygame.sprite.Sprite):
    def __init__(self, x, y, color, last_direction, playertype):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill((WHITE))
        self.rect = self.image.get_rect()
        self.rect.x = x 
        self.rect.y = y + (PLAYER_HEIGHT//2) - 5

        self.vel_y = -5 # tyler type ranged (faller ned mot bakken)

        self.creation_time = time.time()
        self.direction = last_direction
        self.player_type = playertype
        if self.direction == "right":
            self.rect.x = x + 100
        else:
            self.rect.x = x - 10

    def update(self):
        current_time = time.time()
        if current_time - self.creation_time >= RANGED_LENGTH:
            self.kill()
        else:
            self.vel_y += GRAVITY
            if self.direction == "right":
                self.rect.x += 20 
            elif self.direction == "left":
                self.rect.x -= 20
        
        if self.player_type == "tyler":
            self.rect.y += self.vel_y

"""
Upper Cube er ned angrepet der den er basert på y aksen.
DET ER EN ATTACK, IKKE EN UDØDELIG OBJEKT.

"""
class upperCube(pygame.sprite.Sprite):
    def __init__(self, x, y, color, Last_direction):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, 20))
        self.image.fill((25, 25, 25))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y - 80
        self.creation_time = time.time()
    
    def update(self):
        current_time = time.time()
        if current_time - self.creation_time >= CUBE_LIFETIME:
            self.kill()


"""
Lower Cube er ned angrepet der den er basert på y aksen.
DET ER EN ATTACK, IKKE EN UDØDELIG OBJEKT.
"""

class lowerCube(pygame.sprite.Sprite):
    def __init__(self, x, y, color, last_direction):
        super().__init__()
        self.image = pygame.Surface((PLAYER_WIDTH, 20))
        self.image.fill((25, 25, 25))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y + 150
        self.creation_time = time.time()
    
    def update(self):
        current_time = time.time()
        if current_time - self.creation_time >= CUBE_LIFETIME:
            self.kill()


"""
Cube er en attack, ikke spilleren.
Attacken er basert på x-aksen, altså den ordinære angrepet.

DET ER EN ATTACK, IKKE EN UDØDELIG OBJEKT.
"""

class Cube(pygame.sprite.Sprite):
    def __init__(self, x, y, color, last_direction):
        super().__init__()
        self.image = pygame.Surface((20, PLAYER_HEIGHT))
        self.image.fill((25, 25, 25))
        self.rect = self.image.get_rect()
        self.rect.y = y
        
        """RETNING FOR ATTACK (sjekker sist retning)"""
        if last_direction == "right":
            self.rect.x = x + 180 # venstre + player_widt + 80 (80 + 20 bredde)
        elif last_direction == "left":
            self.rect.x = x - 100 # 0 + playerwidt + 20 (bredde)
        else:
            self.rect.x = x
        self.creation_time = time.time()

    def update(self):
        """Delete the cube after 0.1 seconds."""
        current_time = time.time()
        if current_time - self.creation_time >= CUBE_LIFETIME:
            self.kill()

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
    """

    PLAYER CONTROLS
    For å tilkalle en player sin input, så bruker du ordboken og ordenen inne "left", "right", "attack"

    """

    # LAGE SPILLERE MED SETTINGS/INPUTS + playable_character (player type: king_von, tyler, chief, hector)
    player1 = Player(SCREEN_WIDTH // 4, PLATFORM_Y - PLAYER_HEIGHT, RED, {
        "left": pygame.K_a,
        "right": pygame.K_d,
        "jump": pygame.K_w,
        "fall": pygame.K_s,
        "attack": pygame.K_x,
        "upperattack": pygame.K_c,
        "lowerattack": pygame.K_v,
        "rangeattack": pygame.K_z,
    }, playable_character="tyler")
    player2 = Player(SCREEN_WIDTH // 2, PLATFORM_Y - PLAYER_HEIGHT, GREEN, {
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "jump": pygame.K_UP,
        "fall": pygame.K_DOWN,
        "attack": pygame.K_m,
        "upperattack": pygame.K_n,
        "lowerattack": pygame.K_b,
        "rangeattack": pygame.K_COMMA
    }, playable_character=None)
    player3 = Player(3 * SCREEN_WIDTH // 4, PLATFORM_Y - PLAYER_HEIGHT, BLUE, {
        "left": pygame.K_j,
        "right": pygame.K_l,
        "jump": pygame.K_i,
        "fall": pygame.K_k,
        "attack": pygame.K_u,
        "upperattack": pygame.K_y,
        "lowerattack": pygame.K_t,
        "rangeattack": pygame.K_h
    }, playable_character=None)

    # sjekker hvor mange spillere det er
    all_sprites = pygame.sprite.Group()
    if AMOUNT_OF_PLAYERS == 2:
        all_sprites.add(player1, player2)
    if AMOUNT_OF_PLAYERS == 3:
        all_sprites.add(player1, player2, player3)

    # lager platform
    platform = Platform(PLATFORM_X, PLATFORM_Y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
    platforms = pygame.sprite.Group()
    platforms.add(platform)
    all_sprites.add(platform)

    # font
    font = pygame.font.SysFont("arialextrabold", int(SCREEN_HEIGHT / 18))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # player movement
        keys = pygame.key.get_pressed()
        for player in [player1, player2, player3]:
            if keys[player.controls["left"]]:
                knockback_direction = "left"
                player.move_left()
            if keys[player.controls["right"]]:
                knockback_direction = "right"
                player.move_right()
            
            if keys[player.controls["jump"]]:
                if not player.jump_button_pressed:
                    player.jump()
                player.jump_button_pressed = True
            else:
                player.jump_button_pressed = False
            
            if keys[player.controls["fall"]]:
                player.fall()
            if keys[player.controls["attack"]]:
                player.attack(all_sprites)
            if keys[player.controls["upperattack"]]:
                player.upperattack(all_sprites)
            if keys[player.controls["lowerattack"]]:
                player.lowerattack(all_sprites)
            if keys[player.controls["rangeattack"]]:
                player.rangedattack(all_sprites, player.playable_character) # """SYNTAX: all_sprites, (player: king_von, tyler, chief, hector)"""

            # Sjekker hvis spiller er utenfor skjermen + skjerm//2 på alle sider
            if player.rect.y > SCREEN_HEIGHT + SCREEN_HEIGHT//2 or player.rect.x < -(SCREEN_WIDTH//2) or player.rect.x > SCREEN_WIDTH + SCREEN_WIDTH//2 or player.rect.y < -SCREEN_HEIGHT//2:
                if player.lives > 1:
                    player.respawn()
                else:
                    all_sprites.remove(player)
                    player.lives = 0

        # kollisjoner med spillere og hitboxes
        for player in [player1, player2, player3]:
            """normal attack hitbox check"""
            for cube in all_sprites:
                if isinstance(cube, Cube) and player.rect.colliderect(cube.rect):
                    player.apply_knockback(BASE_KNOCKBACK, knockback_direction)
                    cube.kill()  # Remove the cube after collision
            
            """upper attack hitbox check"""
            for upper_cube in all_sprites:
                if isinstance(upper_cube, upperCube) and player.rect.colliderect(upper_cube.rect):
                    player.apply_upper_knockback(BASE_KNOCKBACK, knockback_direction)
                    upper_cube.kill()
            
            """lower attack hitbox check"""
            for lower_cube in all_sprites:
                if isinstance(lower_cube, lowerCube) and player.rect.colliderect(lower_cube.rect):
                    player.apply_lower_knockback(BASE_KNOCKBACK, knockback_direction)
                    lower_cube.kill()
            
            """ranged attack hitbox check"""
            for range_cube in all_sprites:
                if isinstance(range_cube, rangeCube) and player.rect.colliderect(range_cube.rect):
                    player.apply_ranged_knockback(BASE_KNOCKBACK, knockback_direction)
                    lower_cube.kill()
            
        # Oppdaterer alle objekter innenfor all_sprites
        for sprite in all_sprites:
            if isinstance(sprite, Player):
                sprite.update(platforms)  # Pass platforms to Player.update()
            else:
                sprite.update()  # Call update() without arguments for other sprites

        """
        Plasserer alle objekter og tekst på skjermen for game.py
        """
        SCREEN.fill(BLACK)
        all_sprites.draw(SCREEN)
        
        # viser liv
        if AMOUNT_OF_PLAYERS == 2:
            lives_text1 = font.render(f"P1 Lives: {player1.lives}", True, RED)
            lives_text2 = font.render(f"P2 Lives: {player2.lives}", True, GREEN)

            text_rect1 = lives_text1.get_rect(center=((SCREEN_WIDTH // 2) + SCREEN_WIDTH//15, SCREEN_HEIGHT - SCREEN_HEIGHT // 15))
            text_rect2 = lives_text2.get_rect(center=((SCREEN_WIDTH // 2) - SCREEN_WIDTH//15, SCREEN_HEIGHT - SCREEN_HEIGHT // 15))

            SCREEN.blit(lives_text1, text_rect1)
            SCREEN.blit(lives_text2, text_rect2)

        if AMOUNT_OF_PLAYERS == 3:
            lives_text1 = font.render(f"P1 Lives: {player1.lives}", True, RED)
            lives_text2 = font.render(f"P2 Lives: {player2.lives}", True, GREEN)
            lives_text3 = font.render(f"P3 Lives: {player3.lives}", True, BLUE)

            text_rect1 = lives_text1.get_rect(center=((SCREEN_WIDTH // 2) + SCREEN_WIDTH//8, SCREEN_HEIGHT - SCREEN_HEIGHT // 15))
            text_rect2 = lives_text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - SCREEN_HEIGHT // 15))
            text_rect3 = lives_text3.get_rect(center=((SCREEN_WIDTH // 2) - SCREEN_WIDTH//8, SCREEN_HEIGHT - SCREEN_HEIGHT // 15))
            
            SCREEN.blit(lives_text1, text_rect1)
            SCREEN.blit(lives_text2, text_rect2)
            SCREEN.blit(lives_text3, text_rect3)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()