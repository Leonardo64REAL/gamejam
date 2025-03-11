"""


DETTE ER TEST KODE


"""

import pygame

pygame.init()

# Set up the display
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Invisible Rect Example")

# Create a Rect object
rect = pygame.Rect(100, 100, 200, 100)

# Variable to control visibility
visible = False

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Toggle visibility when spacebar is pressed
                visible = not visible

    # Clear the screen
    screen.fill((0, 255, 0))

    # Draw the rect only if it's visible
    if visible:
        pygame.draw.rect(screen, (255, 0, 0), rect)

    # Update the display
    pygame.display.flip()

pygame.quit()