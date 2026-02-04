import pygame
import random
import math
import os

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
GREEN = (0, 255, 0)

# --- Assets Loading ---
def load_asset(name):
    path = os.path.join("assets", name)
    if os.path.exists(path):
        return pygame.image.load(path)
    else:
        # Fallback surface if asset missing (shouldn't happen if generator ran)
        s = pygame.Surface((30, 30))
        s.fill(WHITE)
        return s

player_img = load_asset("player.png")
enemy_squid_img = load_asset("enemy_squid.png")
enemy_crab_img = load_asset("enemy_crab.png")
enemy_octopus_img = load_asset("enemy_octopus.png")
bunker_img = load_asset("bunker.png")
bullet_img = load_asset("laser.png")

# Get dimensions from loaded assets
player_width, player_height = player_img.get_size()
enemy_width, enemy_height = enemy_crab_img.get_size() # Assuming similar sizes
bunker_width, bunker_height = bunker_img.get_size()

# --- Player ---
player_x = 370
player_y = 520 # Lowered slightly
player_x_change = 0
player_speed = 4
lives = 3

def player(x, y):
    screen.blit(player_img, (x, y))

# --- Enemy ---
enemies = []
enemy_speed = 1
enemy_drop = 10

def create_enemies():
    enemies.clear()
    rows = 5
    cols = 11
    start_x = 75
    start_y = 100
    x_gap = 50
    y_gap = 40
    
    # Rows: 0=Squid, 1-2=Crab, 3-4=Octopus (Standard Setup uses this order often, or reversed. 
    # Arcade: Top=Squid(30), Mid=Crab(20), Bot=Octopus(10))
    # Let's map row index 0 to Squid, 1-2 to Crab, 3-4 to Octopus
    
    for row in range(rows):
        for col in range(cols):
            if row == 0:
                img = enemy_squid_img
                score_val = 30
            elif row in [1, 2]:
                img = enemy_crab_img
                score_val = 20
            else:
                img = enemy_octopus_img
                score_val = 10
                
            enemy = {
                "img": img,
                "x": start_x + (col * x_gap),
                "y": start_y + (row * y_gap),
                "x_change": enemy_speed,
                "score": score_val,
                "rect": pygame.Rect(start_x + (col * x_gap), start_y + (row * y_gap), enemy_width, enemy_height)
            }
            enemies.append(enemy)

create_enemies()

def draw_enemy(enemy):
    screen.blit(enemy["img"], (enemy["x"], enemy["y"]))

# --- Bunkers ---
bunkers = []
def create_bunkers():
    bunkers.clear()
    num_bunkers = 4
    # Spacing logic
    gap = SCREEN_WIDTH // (num_bunkers + 1)
    for i in range(num_bunkers):
        x = gap * (i + 1) - (bunker_width // 2)
        y = 450
        # For pixel-perfect collision, we could mask, but rects for snippets is easier.
        # Let's just use a list of small rects to allow destruction?
        # For simplicity in this iteration, one big rect per bunker. 
        # Collision with bullets destroys the bullet. Repeated hits?
        # Let's just draw them for now and maybe destroy them fully on hit if simple.
        # Or better: make multiple small rects for each bunker to simulate damage?
        # Let's stick to simple single-object bunkers that take 5 hits to destroy for now, 
        # or just permanent shields that block bullets.
        # Arcade behavior: pixels get eaten. That's complex.
        # Let's Implement "Health" based bunkers.
        rect = pygame.Rect(x, y, bunker_width, bunker_height)
        bunkers.append({"rect": rect, "health": 10})

create_bunkers()

def draw_bunkers():
    for b in bunkers:
        # Scale alpha or color based on health? Or just draw if health > 0
        if b["health"] > 0:
            screen.blit(bunker_img, (b["rect"].x, b["rect"].y))

# --- Bullet ---
# Player Bullet
bullet_x = 0
bullet_y = 480
bullet_y_change = 10
bullet_state = "ready" 
bullet_rect = pygame.Rect(0, 0, bullet_img.get_width(), bullet_img.get_height())

def fire_bullet(x, y):
    global bullet_state, bullet_x, bullet_y
    bullet_state = "fire"
    bullet_x = x + (player_width // 2) - (bullet_img.get_width() // 2)
    bullet_y = y
    bullet_rect.topleft = (bullet_x, bullet_y)

def draw_bullet():
    if bullet_state == "fire":
        screen.blit(bullet_img, (bullet_x, bullet_y))

def is_collision(rect1, rect2):
    return rect1.colliderect(rect2)

# --- Score ---
score_value = 0
hi_score_value = 0 # Placeholder
font = pygame.font.Font(None, 32) # Default system font. For arcade look, a pixel font would be better but default is safe.
font_small = pygame.font.Font(None, 24)

def show_ui():
    score_text = font.render(f"SCORE<1>   HI-SCORE   SCORE<2>", True, WHITE)
    score_nums = font.render(f"  {score_value:04d}        {hi_score_value:04d}", True, WHITE)
    screen.blit(score_text, (100, 10))
    screen.blit(score_nums, (120, 40))
    
    # Bottom Line
    pygame.draw.line(screen, GREEN, (0, SCREEN_HEIGHT - 30), (SCREEN_WIDTH, SCREEN_HEIGHT - 30), 3)
    
    # Lives (bottom left)
    lives_text = font.render(str(lives), True, WHITE)
    screen.blit(lives_text, (20, SCREEN_HEIGHT - 25))
    # Draw mini ships for lives
    for i in range(max(0, lives - 1)):
        # Scale down player img for icon
        small_ship = pygame.transform.scale(player_img, (30, 20))
        screen.blit(small_ship, (40 + (i * 40), SCREEN_HEIGHT - 25))

    # Credits (bottom right)
    cred_text = font.render("CREDIT 00", True, WHITE)
    screen.blit(cred_text, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 25))

def game_over_text():
    over_font = pygame.font.Font(None, 64)
    over_text = over_font.render("GAME OVER", True, GREEN)
    text_rect = over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))    
    screen.blit(over_text, text_rect)

# --- Game Loop ---
running = True
game_over = False
clock = pygame.time.Clock()

while running:
    clock.tick(60) # Limit to 60 FPS
    
    # Background
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Input
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player_x_change = -player_speed
            if event.key == pygame.K_RIGHT:
                player_x_change = player_speed
            if event.key == pygame.K_SPACE:
                if bullet_state == "ready" and not game_over:
                    fire_bullet(player_x, player_y)
            if event.key == pygame.K_r and game_over:
                # Reset
                game_over = False
                score_value = 0
                lives = 3
                enemies.clear()
                bunkers.clear()
                create_enemies()
                create_bunkers()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                player_x_change = 0

    if not game_over:
        # Player Movement
        player_x += player_x_change
        if player_x <= 0: player_x = 0
        elif player_x >= SCREEN_WIDTH - player_width: player_x = SCREEN_WIDTH - player_width
        
        # Enemy Movement Logic
        move_down = False
        # Calculate bounds
        # If any enemy hits wall, all move down and change direction
        # Find min/max x of current swarm? Or just check all?
        # Checking all is O(N), N=55. Fast enough.
        
        for e in enemies:
            e["x"] += e["x_change"]
            e["rect"].topleft = (e["x"], e["y"])
            if e["x"] <= 0 or e["x"] >= SCREEN_WIDTH - enemy_width:
                move_down = True

        if move_down:
            for e in enemies:
                e["x_change"] *= -1
                e["y"] += enemy_drop
                e["rect"].topleft = (e["x"], e["y"])
                # Boundary check - if too low, Game Over
                if e["y"] > 400: # Approximate line
                    game_over = True

        # Collisions
        # Bullet vs Enemies
        if bullet_state == "fire":
            bullet_y -= bullet_y_change
            bullet_rect.topleft = (bullet_x, bullet_y)
            if bullet_y <= 0:
                bullet_state = "ready"
            
            # Use a copy of list to allow removal during iteration
            for e in enemies[:]:
                if is_collision(e["rect"], bullet_rect):
                    bullet_state = "ready"
                    bullet_y = 480 # Reset
                    score_value += e["score"]
                    enemies.remove(e)
                    break # Bullet destroys one enemy
            
            # Bullet vs Bunkers
            for b in bunkers:
                if b["health"] > 0 and is_collision(b["rect"], bullet_rect):
                    bullet_state = "ready"
                    bullet_y = 480
                    b["health"] -= 1
                    break

        # Draw Everything
        draw_bunkers()
        draw_bullet()
        
        for e in enemies:
            draw_enemy(e)
            
        player(player_x, player_y)
        show_ui()
        
        if len(enemies) == 0:
            # You win level? Respawn?
            create_enemies()
            
    else:
        show_ui()
        game_over_text()

    pygame.display.update()

