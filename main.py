import pygame
import random
import math

# --- Initialization ---
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Title and Icon
pygame.display.set_caption("Space Invaders")

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# --- Player ---
player_width = 50
player_height = 50
player_x = 370
player_y = 480
player_x_change = 0
player_speed = 4

def player(x, y):
    # Draw player as a Green Triangle (Ship)
    points = [(x, y + player_height), (x + player_width // 2, y), (x + player_width, y + player_height)]
    pygame.draw.polygon(screen, GREEN, points)

# --- Enemy ---
enemy_width = 40
enemy_height = 40
num_of_enemies = 6
enemy_x = []
enemy_y = []
enemy_x_change = []
enemy_y_change = []
enemy_speed = 3

for i in range(num_of_enemies):
    enemy_x.append(random.randint(0, SCREEN_WIDTH - enemy_width))
    enemy_y.append(random.randint(50, 150))
    enemy_x_change.append(enemy_speed)
    enemy_y_change.append(40) # How much they drop down

def enemy(x, y):
    # Draw enemy as a Red Rectangle
    pygame.draw.rect(screen, RED, (x, y, enemy_width, enemy_height))

# --- Bullet ---
bullet_width = 5
bullet_height = 15
bullet_x = 0
bullet_y = 480
bullet_x_change = 0
bullet_y_change = 10
bullet_state = "ready" # "ready" means you can't see it; "fire" means it is moving

def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    pygame.draw.rect(screen, YELLOW, (x + player_width // 2 - bullet_width // 2, y, bullet_width, bullet_height))

def is_collision(enemyX, enemyY, bulletX, bulletY):
    # Simple distance formula
    distance = math.sqrt(math.pow(enemyX - bulletX, 2) + (math.pow(enemyY - bulletY, 2)))
    if distance < 27:
        return True
    return False

# --- Score ---
score_value = 0
font = pygame.font.Font(None, 32) # Default system font
text_x = 10
text_y = 10

def show_score(x, y):
    score = font.render("Score: " + str(score_value), True, WHITE)
    screen.blit(score, (x, y))

def game_over_text():
    over_font = pygame.font.Font(None, 64)
    over_text = over_font.render("GAME OVER", True, WHITE)
    text_rect = over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
    screen.blit(over_text, text_rect)

# --- Game Loop ---
running = True
game_over = False

while running:
    # Background Color (RGB)
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Keystroke checks
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player_x_change = -player_speed
            if event.key == pygame.K_RIGHT:
                player_x_change = player_speed
            if event.key == pygame.K_SPACE:
                if bullet_state == "ready" and not game_over:
                    bullet_x = player_x
                    fire_bullet(bullet_x, bullet_y)

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                player_x_change = 0

    if not game_over:
        # Player Movement
        player_x += player_x_change
        # Boundaries
        if player_x <= 0:
            player_x = 0
        elif player_x >= SCREEN_WIDTH - player_width:
            player_x = SCREEN_WIDTH - player_width

        # Enemy Movement
        for i in range(num_of_enemies):
            # Game Over Logic
            if enemy_y[i] > 440: 
                for j in range(num_of_enemies):
                    enemy_y[j] = 2000 # Move all enemies off screen
                game_over = True
                break

            enemy_x[i] += enemy_x_change[i]
            
            # Enemy boundary check and drop down
            if enemy_x[i] <= 0:
                enemy_x_change[i] = enemy_speed
                enemy_y[i] += enemy_y_change[i]
            elif enemy_x[i] >= SCREEN_WIDTH - enemy_width:
                enemy_x_change[i] = -enemy_speed
                enemy_y[i] += enemy_y_change[i]

            # Collision
            collision = is_collision(enemy_x[i], enemy_y[i], bullet_x, bullet_y)
            if collision:
                bullet_y = 480
                bullet_state = "ready"
                score_value += 1
                enemy_x[i] = random.randint(0, SCREEN_WIDTH - enemy_width)
                enemy_y[i] = random.randint(50, 150)

            enemy(enemy_x[i], enemy_y[i])

        # Bullet Movement
        if bullet_y <= 0:
            bullet_y = 480
            bullet_state = "ready"

        if bullet_state == "fire":
            fire_bullet(bullet_x, bullet_y)
            bullet_y -= bullet_y_change

        player(player_x, player_y)
        show_score(text_x, text_y)
    
    else:
        game_over_text()

    pygame.display.update()
