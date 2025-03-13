# settings.py
import pygame
import cv2
import numpy as np

def play_video_and_audio(screen):
    """
    Plays an audio track in the background, loops the video infinitely,
    and exits if the user presses Circle (button=1) on a PS4 controller.
    """
    # Initialize joystick if not already done elsewhere
    # (If you're doing this in main.py, you can omit these lines)
    pygame.joystick.init()
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
    else:
        joystick = None

    # Load and play your audio on a loop
    pygame.mixer.music.load("Assets/Audio/saw.mp3")  
    pygame.mixer.music.play(-1, 0.0, 3000)                

    # Set up a cv2 video capture
    cap = cv2.VideoCapture("Assets/Videos/settings.mp4")  
    clock = pygame.time.Clock()
    desired_fps = 30
    playing = True

    while playing:
        ret, frame = cap.read()
        if not ret:
            # If video ended or read failed, rewind to the beginning and continue
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        # Flip horizontally, convert to RGB, resize, rotate for Pygame
        frame = cv2.flip(frame, 2)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = cv2.resize(frame_rgb, (screen.get_width(), screen.get_height()))
        frame_rgb = np.rot90(frame_rgb)

        # Convert the array to a Pygame surface
        surf = pygame.surfarray.make_surface(frame_rgb)
        screen.blit(surf, (0, 0))
        pygame.display.flip()

        # Handle events: look for Circle button or Quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False
            elif event.type == pygame.JOYBUTTONDOWN:
                # On many PS4 controllers, Circle is button 1
                if event.button == 1:
                    playing = False

        clock.tick(desired_fps)

    # Cleanup
    cap.release()
    pygame.mixer.music.stop()
    return
