# PYTHON game 
import pygame
from random import randint, choice
import sys

pygame.init()
pygame.mixer.init()  # Initialize the mixer for sound
last_score_time = pygame.time.get_ticks()  # Initialize last score time
Score_counter = 0
# Set up the game window
WIDTH, HEIGHT = 576, 324
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SPACE FLYER")
clock = pygame.time.Clock()
# surfaces 
# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
game_active = False
explosion_active = False
explosion_timer = 0
explosion_duration = 1000  # Duration in milliseconds (1 second)
#fonts
font_title = pygame.font.Font('SPACE FLYER SPRITES/PixelatedEleganceRegular-ovyAA.ttf', 30)
font_score = pygame.font.Font('SPACE FLYER SPRITES/PixelatedEleganceRegular-ovyAA.ttf', 20)

# Load sound effects (with error handling)
try:
    explosion_sound = pygame.mixer.Sound('SPACE FLYER SPRITES/explosion.wav')
    explosion_sound.set_volume(0.5)  # Adjust volume as needed
except:
    explosion_sound = None  # If sound file doesn't exist, set to None

# Load sprites
background = pygame.image.load(('SPACE FLYER SPRITES/1.png')).convert_alpha()
background_x = 0
background_y = 0
clouds = pygame.image.load(('SPACE FLYER SPRITES/clouds.png')).convert_alpha()
clouds_x = 0
clouds_y = 0

# Load explosion animation frames (with fallback)
explosion_frames = []
try:
    # Try to load explosion animation frames
    for i in range(1, 6):  # Assuming you have explosion1.png to explosion5.png
        frame = pygame.image.load(f'SPACE FLYER SPRITES/explosion{i}.png').convert_alpha()
        explosion_frames.append(frame)
except:
    # If explosion sprites don't exist, create simple colored circles as fallback
    explosion_frames = []
    colors = [(255, 100, 100), (255, 150, 0), (255, 200, 0), (255, 255, 100), (200, 200, 200)]
    for i, color in enumerate(colors):
        frame = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(frame, color, (30, 30), 30 - i * 3)
        pygame.draw.circle(frame, (255, 255, 255), (30, 30), 20 - i * 2)
        explosion_frames.append(frame)

explosion_frame_index = 0
explosion_pos = (0, 0)
text_surface = font_title.render('SPACE FLYER', False, '#FFFFFF')
text_x = WIDTH // 2 - text_surface.get_width() // 2
text_y = 10
Ship_surface = pygame.image.load(('SPACE FLYER SPRITES/tiny_ship.png')).convert_alpha()
Ship_x = 10
Ship_y = HEIGHT // 2 - Ship_surface.get_height() // 2
Asteroid_surface = pygame.image.load(('SPACE FLYER SPRITES/asteroids#01.png')).convert_alpha()
Asteroid_x = WIDTH - Asteroid_surface.get_width()
Asteroid_y = HEIGHT // 2 - Asteroid_surface.get_height() // 2

#rectangles
Ship_rect = Ship_surface.get_rect(topleft=(Ship_x, Ship_y))
Asteroid_rect = Asteroid_surface.get_rect(topleft=(Asteroid_x, Asteroid_y))

Score_surface1 = font_score.render(f'SCORE: {Score_counter}', False, '#FFFFFF')
Score_rect1 = Score_surface1.get_rect(center=(WIDTH // 2 - Score_surface1.get_width() // 2,50))
game_over_surface = font_title.render('GAME OVER', False, '#FFFFFF')
game_over_rect = game_over_surface.get_rect(center=(WIDTH // 2, 50))
tutorial_surface = font_title.render('Press Space to fly', False, '#FFFFFF')
tutorial_rect = tutorial_surface.get_rect(center=(WIDTH // 2, 250))

# Score counter
def Score():
    global Score_counter, last_score_time, Score_surface1, Score_rect1
    current_time = pygame.time.get_ticks()
    if current_time - last_score_time >= 100:  # 100 ms = 0.1 second
        Score_counter += 1
        last_score_time = current_time
    Score_surface1 = font_score.render(f'SCORE: {Score_counter}', False, '#FFFFFF')
    Score_rect1 = Score_surface1.get_rect(center=(WIDTH // 2 - Score_surface1.get_width() // 2, 50))
    screen.blit(Score_surface1, Score_rect1)

# asteroid timer with randomized spawning
Asteroid_timer = pygame.USEREVENT + 1
# Start with initial random timer
pygame.time.set_timer(Asteroid_timer, randint(3000, 7000))  # Random between 3-7 seconds

Asteroid_rect_list = []

def Asteroid_movement(Asteroid_rect_list):
    if Asteroid_rect_list:
        # Create a new list to store asteroids that are still on screen
        active_asteroids = []
        for Asteroid_rect in Asteroid_rect_list:
            Asteroid_rect.x -= 2  # Slightly faster movement for better gameplay
            # Only keep asteroids that are completely off screen (fully past left edge)
            if Asteroid_rect.x > -Asteroid_rect.width:
                screen.blit(Asteroid_surface, Asteroid_rect)
                active_asteroids.append(Asteroid_rect)
        return active_asteroids
    else:
        return []

# Collision detection function
def check_collisions(ship_rect, asteroid_list):
    for asteroid in asteroid_list:
        if ship_rect.colliderect(asteroid):
            return True, asteroid  # Return True and the colliding asteroid
    return False, None

# Explosion animation function
def update_explosion():
    global explosion_active, explosion_timer, explosion_frame_index
    
    if explosion_active:
        current_time = pygame.time.get_ticks()
        if current_time - explosion_timer > explosion_duration:
            explosion_active = False
            explosion_frame_index = 0
        else:
            # Update animation frame based on time
            frame_duration = explosion_duration // len(explosion_frames)
            explosion_frame_index = min((current_time - explosion_timer) // frame_duration, len(explosion_frames) - 1)

def draw_explosion():
    if explosion_active and explosion_frame_index < len(explosion_frames):
        frame = explosion_frames[explosion_frame_index]
        # Center the explosion on the collision point
        explosion_rect = frame.get_rect(center=explosion_pos)
        screen.blit(frame, explosion_rect)

# game loop continuously running the window keeping it open and taking inputs 
while True:
    # draw all elements and update the display
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # Move asteroid spawning inside the event loop
        if event.type == Asteroid_timer and game_active:
            # Spawn 2-3 asteroids at random positions
            num_asteroids = randint(2, 3)
            spawn_x_start = WIDTH + randint(0, 100)  # Starting x position with some variation
            
            for i in range(num_asteroids):
                # Spawn asteroids with some horizontal spacing
                spawn_x = spawn_x_start + (i * randint(150, 250))  # 150-250 pixels apart
                spawn_y = randint(0, HEIGHT - Asteroid_surface.get_height())
                
                Asteroid_rect_list.append(
                    Asteroid_surface.get_rect(topleft=(spawn_x, spawn_y))
                )
            
            # Set next random spawn time
            pygame.time.set_timer(Asteroid_timer, randint(3000, 7000))
    
    # event loop looks for inputs 
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] and game_active:
        Ship_rect.y -= 3  # Slightly stronger upward movement
        
    if not game_active:
        if keys[pygame.K_RETURN] and not explosion_active:  # Don't restart during explosion
            game_active = True
            Ship_rect.y = HEIGHT // 2 - Ship_surface.get_height() // 2
            # Clear all asteroids when restarting
            Asteroid_rect_list = []
            Score_counter = 0
            last_score_time = pygame.time.get_ticks()

    if game_active:
        # Apply gravity
        Ship_rect.y += 1.2  # Slightly stronger gravity to balance the stronger jump
        
        # Keep ship within screen bounds
        if Ship_rect.y < 0:
            Ship_rect.y = 0
        if Ship_rect.y > HEIGHT - Ship_surface.get_height():
            Ship_rect.y = HEIGHT - Ship_surface.get_height()
        
        # Draw everything
        screen.blit(background, (0, 0))
        screen.blit(clouds, (0, 0))
        screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2,10))
        screen.blit(Ship_surface, Ship_rect)
        
        # Update score and asteroids
        Score()
        Asteroid_rect_list = Asteroid_movement(Asteroid_rect_list)
        
        # Check for collisions with all asteroids
        collision_detected, colliding_asteroid = check_collisions(Ship_rect, Asteroid_rect_list)
        if collision_detected:
            # Start explosion animation at collision point
            explosion_active = True
            explosion_timer = pygame.time.get_ticks()
            explosion_frame_index = 0
            # Set explosion position to the center between ship and asteroid
            explosion_pos = (
                (Ship_rect.centerx + colliding_asteroid.centerx) // 2,
                (Ship_rect.centery + colliding_asteroid.centery) // 2
            )
            
            # Play explosion sound
            if explosion_sound:
                explosion_sound.play()
            
            game_active = False

    else:
        screen.fill(BLACK)
        
        # Update and draw explosion even when game is not active
        update_explosion()
        draw_explosion()
        
        if Score_counter == 0:
            # Welcome screen
            welcome_surface = font_title.render('SPACE FLYER', False, '#FFFFFF')
            welcome_rect = welcome_surface.get_rect(center=(WIDTH // 2, 50))
            screen.blit(welcome_surface, welcome_rect)
            screen.blit(tutorial_surface, tutorial_rect)
            start_surface = font_title.render('Press Enter to Start', False, '#FFFFFF')
            start_rect = start_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
            screen.blit(start_surface, start_rect)
        else:
            # Game over screen - only show after explosion is done
            if not explosion_active:
                screen.blit(game_over_surface, game_over_rect)
                final_score_surface = font_score.render(f'SCORE: {Score_counter}', False, '#FFFFFF')
                final_score_rect = final_score_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                screen.blit(final_score_surface, final_score_rect)
                restart_surface = font_title.render('Press Enter to Restart', False, '#FFFFFF')
                restart_rect = restart_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
                screen.blit(restart_surface, restart_rect)

    pygame.display.update()
    clock.tick(60)