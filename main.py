"""
Space Invaders - A classic arcade game recreation using Pygame.

Security & Robustness Features:
- Centralized configuration in config.py
- Safe asset loading with path traversal protection
- Input validation on all game state variables
- Comprehensive error handling with graceful degradation
"""

import pygame
import sys
import os
from typing import List, Dict, Optional

# Import all configuration from centralized config module
from config import (
    # Display
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    # Colors
    BLACK, WHITE, GREEN,
    # Player
    PLAYER_SPEED, PLAYER_START_X, PLAYER_START_Y, 
    PLAYER_INITIAL_LIVES, PLAYER_MAX_LIVES,
    # Enemy
    ENEMY_SPEED, ENEMY_DROP_DISTANCE, ENEMY_ROWS, ENEMY_COLS,
    ENEMY_START_X, ENEMY_START_Y, ENEMY_X_GAP, ENEMY_Y_GAP,
    ENEMY_GAME_OVER_Y, ENEMY_SCORE_SQUID, ENEMY_SCORE_CRAB, ENEMY_SCORE_OCTOPUS,
    # Bullet
    BULLET_SPEED, BULLET_START_Y,
    # Bunker
    BUNKER_COUNT, BUNKER_Y_POSITION, BUNKER_HEALTH,
    # Score
    MAX_SCORE, MIN_SCORE,
    # Assets
    ALLOWED_ASSETS, ALLOWED_EXTENSIONS, ASSETS_DIR,
    FALLBACK_SURFACE_SIZE, FALLBACK_SURFACE_COLOR,
    # UI
    UI_FONT_SIZE, UI_FONT_SMALL_SIZE, UI_BOTTOM_LINE_Y_OFFSET,
    UI_LIVES_ICON_WIDTH, UI_LIVES_ICON_HEIGHT
)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def clamp(value: int, min_val: int, max_val: int) -> int:
    """
    Clamp a value between minimum and maximum bounds.
    
    Args:
        value: The value to clamp
        min_val: Minimum allowed value
        max_val: Maximum allowed value
    
    Returns:
        Clamped value within [min_val, max_val]
    """
    return max(min_val, min(value, max_val))


def create_fallback_surface(width: int = None, height: int = None) -> pygame.Surface:
    """
    Create a fallback surface for missing assets.
    
    Args:
        width: Surface width (defaults to FALLBACK_SURFACE_SIZE[0])
        height: Surface height (defaults to FALLBACK_SURFACE_SIZE[1])
    
    Returns:
        A colored surface to use as placeholder
    """
    w = width if width is not None else FALLBACK_SURFACE_SIZE[0]
    h = height if height is not None else FALLBACK_SURFACE_SIZE[1]
    surface = pygame.Surface((w, h))
    surface.fill(FALLBACK_SURFACE_COLOR)
    return surface


# =============================================================================
# SAFE FILE HANDLING
# =============================================================================

def load_asset(name: str) -> pygame.Surface:
    """
    Safely load an asset file with path traversal protection.
    
    Security measures:
    - Whitelist validation: Only allow known asset filenames
    - Extension validation: Only allow approved file extensions
    - Path traversal prevention: Verify resolved path stays within assets dir
    - Error handling: Return fallback surface on any failure
    
    Args:
        name: The filename of the asset to load (e.g., "player.png")
    
    Returns:
        Loaded pygame.Surface, or fallback surface on error
    """
    try:
        # SECURITY: Validate filename is in whitelist
        if name not in ALLOWED_ASSETS:
            print(f"[SECURITY] Asset '{name}' not in allowed list, using fallback")
            return create_fallback_surface()
        
        # SECURITY: Validate file extension
        _, ext = os.path.splitext(name)
        if ext.lower() not in ALLOWED_EXTENSIONS:
            print(f"[SECURITY] Extension '{ext}' not allowed, using fallback")
            return create_fallback_surface()
        
        # SECURITY: Prevent path traversal attacks
        # Get absolute path to assets directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.realpath(os.path.join(script_dir, ASSETS_DIR))
        
        # Resolve the full path to the requested asset
        full_path = os.path.realpath(os.path.join(assets_dir, name))
        
        # Verify the resolved path is still within assets directory
        if not full_path.startswith(assets_dir + os.sep):
            print(f"[SECURITY] Path traversal detected for '{name}', using fallback")
            return create_fallback_surface()
        
        # Verify file exists
        if not os.path.isfile(full_path):
            print(f"[WARNING] Asset file not found: {full_path}, using fallback")
            return create_fallback_surface()
        
        # Load the asset
        return pygame.image.load(full_path)
    
    except pygame.error as e:
        print(f"[ERROR] Failed to load asset '{name}': {e}, using fallback")
        return create_fallback_surface()
    except Exception as e:
        print(f"[ERROR] Unexpected error loading '{name}': {e}, using fallback")
        return create_fallback_surface()


# =============================================================================
# INITIALIZATION
# =============================================================================

def initialize_pygame() -> Optional[pygame.Surface]:
    """
    Initialize Pygame with error handling.
    
    Returns:
        Screen surface on success, None on failure
    """
    try:
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders")
        return screen
    except pygame.error as e:
        print(f"[FATAL] Failed to initialize Pygame: {e}")
        return None
    except Exception as e:
        print(f"[FATAL] Unexpected initialization error: {e}")
        return None


# Initialize game
screen = initialize_pygame()
if screen is None:
    print("Cannot start game - Pygame initialization failed")
    sys.exit(1)


# =============================================================================
# LOAD ASSETS
# =============================================================================

player_img = load_asset("player.png")
enemy_squid_img = load_asset("enemy_squid.png")
enemy_crab_img = load_asset("enemy_crab.png")
enemy_octopus_img = load_asset("enemy_octopus.png")
bunker_img = load_asset("bunker.png")
bullet_img = load_asset("laser.png")

# Get dimensions from loaded assets
player_width, player_height = player_img.get_size()
enemy_width, enemy_height = enemy_crab_img.get_size()
bunker_width, bunker_height = bunker_img.get_size()


# =============================================================================
# GAME STATE (with validation)
# =============================================================================

# Player state
player_x: int = PLAYER_START_X
player_y: int = PLAYER_START_Y
player_x_change: int = 0
lives: int = PLAYER_INITIAL_LIVES

# Score state
score_value: int = 0
hi_score_value: int = 0

# Bullet state
bullet_x: int = 0
bullet_y: int = BULLET_START_Y
bullet_state: str = "ready"
bullet_rect = pygame.Rect(0, 0, bullet_img.get_width(), bullet_img.get_height())

# Collections
enemies: List[Dict] = []
bunkers: List[Dict] = []


def validate_game_state() -> None:
    """
    Validate and clamp all game state variables to valid bounds.
    Prevents integer overflow, underflow, and out-of-bounds conditions.
    Should be called each frame before processing.
    """
    global score_value, lives, player_x, player_y, bullet_x, bullet_y
    
    # Validate score
    score_value = clamp(score_value, MIN_SCORE, MAX_SCORE)
    
    # Validate lives
    lives = clamp(lives, 0, PLAYER_MAX_LIVES)
    
    # Validate player position
    player_x = clamp(player_x, 0, SCREEN_WIDTH - player_width)
    player_y = clamp(player_y, 0, SCREEN_HEIGHT - player_height)
    
    # Validate bullet position
    bullet_x = clamp(bullet_x, 0, SCREEN_WIDTH)
    bullet_y = clamp(bullet_y, -bullet_img.get_height(), SCREEN_HEIGHT)


def reset_game_state() -> None:
    """Reset all game state to initial values."""
    global player_x, player_y, player_x_change, lives
    global score_value, bullet_state, bullet_y
    
    player_x = PLAYER_START_X
    player_y = PLAYER_START_Y
    player_x_change = 0
    lives = PLAYER_INITIAL_LIVES
    score_value = 0
    bullet_state = "ready"
    bullet_y = BULLET_START_Y
    
    enemies.clear()
    bunkers.clear()
    create_enemies()
    create_bunkers()


# =============================================================================
# DRAWING FUNCTIONS
# =============================================================================

def player(x: int, y: int) -> None:
    """Draw the player ship at specified position."""
    screen.blit(player_img, (x, y))


def draw_enemy(enemy: Dict) -> None:
    """Draw an enemy at its current position."""
    screen.blit(enemy["img"], (enemy["x"], enemy["y"]))


def draw_bullet() -> None:
    """Draw the player's bullet if it's in fire state."""
    if bullet_state == "fire":
        screen.blit(bullet_img, (bullet_x, bullet_y))


def draw_bunkers() -> None:
    """Draw all bunkers that have remaining health."""
    for b in bunkers:
        if b["health"] > 0:
            screen.blit(bunker_img, (b["rect"].x, b["rect"].y))


# =============================================================================
# ENTITY CREATION
# =============================================================================

def create_enemies() -> None:
    """Create the enemy formation grid."""
    enemies.clear()
    
    for row in range(ENEMY_ROWS):
        for col in range(ENEMY_COLS):
            # Determine enemy type and score based on row
            if row == 0:
                img = enemy_squid_img
                score_val = ENEMY_SCORE_SQUID
            elif row in [1, 2]:
                img = enemy_crab_img
                score_val = ENEMY_SCORE_CRAB
            else:
                img = enemy_octopus_img
                score_val = ENEMY_SCORE_OCTOPUS
            
            x = ENEMY_START_X + (col * ENEMY_X_GAP)
            y = ENEMY_START_Y + (row * ENEMY_Y_GAP)
            
            enemy = {
                "img": img,
                "x": x,
                "y": y,
                "x_change": ENEMY_SPEED,
                "score": score_val,
                "rect": pygame.Rect(x, y, enemy_width, enemy_height)
            }
            enemies.append(enemy)


def create_bunkers() -> None:
    """Create protective bunkers."""
    bunkers.clear()
    gap = SCREEN_WIDTH // (BUNKER_COUNT + 1)
    
    for i in range(BUNKER_COUNT):
        x = gap * (i + 1) - (bunker_width // 2)
        y = BUNKER_Y_POSITION
        rect = pygame.Rect(x, y, bunker_width, bunker_height)
        bunkers.append({"rect": rect, "health": BUNKER_HEALTH})


# =============================================================================
# GAME ACTIONS
# =============================================================================

def fire_bullet(x: int, y: int) -> None:
    """Fire a bullet from the given position."""
    global bullet_state, bullet_x, bullet_y
    bullet_state = "fire"
    bullet_x = x + (player_width // 2) - (bullet_img.get_width() // 2)
    bullet_y = y
    bullet_rect.topleft = (bullet_x, bullet_y)


def is_collision(rect1: pygame.Rect, rect2: pygame.Rect) -> bool:
    """Check if two rectangles collide."""
    return rect1.colliderect(rect2)


# =============================================================================
# UI RENDERING
# =============================================================================

# Initialize fonts with error handling
try:
    font = pygame.font.Font(None, UI_FONT_SIZE)
    font_small = pygame.font.Font(None, UI_FONT_SMALL_SIZE)
except pygame.error as e:
    print(f"[WARNING] Failed to load fonts: {e}")
    font = pygame.font.SysFont(None, UI_FONT_SIZE)
    font_small = pygame.font.SysFont(None, UI_FONT_SMALL_SIZE)


def show_ui() -> None:
    """Render the game UI (scores, lives, credits)."""
    score_text = font.render("SCORE<1>   HI-SCORE   SCORE<2>", True, WHITE)
    score_nums = font.render(f"  {score_value:04d}        {hi_score_value:04d}", True, WHITE)
    screen.blit(score_text, (100, 10))
    screen.blit(score_nums, (120, 40))
    
    # Bottom line
    line_y = SCREEN_HEIGHT - UI_BOTTOM_LINE_Y_OFFSET
    pygame.draw.line(screen, GREEN, (0, line_y), (SCREEN_WIDTH, line_y), 3)
    
    # Lives display
    lives_text = font.render(str(lives), True, WHITE)
    screen.blit(lives_text, (20, SCREEN_HEIGHT - 25))
    
    # Life icons
    for i in range(max(0, lives - 1)):
        small_ship = pygame.transform.scale(
            player_img, 
            (UI_LIVES_ICON_WIDTH, UI_LIVES_ICON_HEIGHT)
        )
        screen.blit(small_ship, (40 + (i * 40), SCREEN_HEIGHT - 25))
    
    # Credits
    cred_text = font.render("CREDIT 00", True, WHITE)
    screen.blit(cred_text, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 25))


def game_over_text() -> None:
    """Render the game over message."""
    try:
        over_font = pygame.font.Font(None, 64)
    except pygame.error:
        over_font = pygame.font.SysFont(None, 64)
    
    over_text = over_font.render("GAME OVER", True, GREEN)
    text_rect = over_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
    screen.blit(over_text, text_rect)


# =============================================================================
# MAIN GAME LOOP
# =============================================================================

def main() -> None:
    """Main game loop with comprehensive error handling."""
    global player_x, player_x_change, bullet_state, bullet_x, bullet_y
    global score_value, lives
    
    # Initialize entities
    create_enemies()
    create_bunkers()
    
    running = True
    game_over = False
    clock = pygame.time.Clock()
    
    while running:
        try:
            clock.tick(FPS)
            
            # Validate game state each frame
            validate_game_state()
            
            # Clear screen
            screen.fill(BLACK)
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        player_x_change = -PLAYER_SPEED
                    if event.key == pygame.K_RIGHT:
                        player_x_change = PLAYER_SPEED
                    if event.key == pygame.K_SPACE:
                        if bullet_state == "ready" and not game_over:
                            fire_bullet(player_x, player_y)
                    if event.key == pygame.K_r and game_over:
                        game_over = False
                        reset_game_state()
                
                if event.type == pygame.KEYUP:
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        player_x_change = 0
            
            if not game_over:
                # Player movement with bounds checking
                player_x += player_x_change
                player_x = clamp(player_x, 0, SCREEN_WIDTH - player_width)
                
                # Enemy movement
                move_down = False
                for e in enemies:
                    e["x"] += e["x_change"]
                    e["rect"].topleft = (e["x"], e["y"])
                    if e["x"] <= 0 or e["x"] >= SCREEN_WIDTH - enemy_width:
                        move_down = True
                
                if move_down:
                    for e in enemies:
                        e["x_change"] *= -1
                        e["y"] += ENEMY_DROP_DISTANCE
                        e["rect"].topleft = (e["x"], e["y"])
                        if e["y"] > ENEMY_GAME_OVER_Y:
                            game_over = True
                
                # Bullet movement and collisions
                if bullet_state == "fire":
                    bullet_y -= BULLET_SPEED
                    bullet_rect.topleft = (bullet_x, bullet_y)
                    
                    if bullet_y <= 0:
                        bullet_state = "ready"
                    
                    # Bullet vs Enemies
                    for e in enemies[:]:
                        if is_collision(e["rect"], bullet_rect):
                            bullet_state = "ready"
                            bullet_y = BULLET_START_Y
                            score_value += e["score"]
                            enemies.remove(e)
                            break
                    
                    # Bullet vs Bunkers
                    for b in bunkers:
                        if b["health"] > 0 and is_collision(b["rect"], bullet_rect):
                            bullet_state = "ready"
                            bullet_y = BULLET_START_Y
                            b["health"] -= 1
                            break
                
                # Draw game elements
                draw_bunkers()
                draw_bullet()
                for e in enemies:
                    draw_enemy(e)
                player(player_x, player_y)
                show_ui()
                
                # Check win condition
                if len(enemies) == 0:
                    create_enemies()
            
            else:
                show_ui()
                game_over_text()
            
            pygame.display.update()
        
        except pygame.error as e:
            print(f"[ERROR] Pygame error in game loop: {e}")
            # Attempt to continue
            continue
        except Exception as e:
            print(f"[ERROR] Unexpected error in game loop: {e}")
            # For unexpected errors, may need to exit
            running = False
    
    # Cleanup
    pygame.quit()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
        pygame.quit()
        sys.exit(0)
    except Exception as e:
        print(f"[FATAL] Unhandled exception: {e}")
        pygame.quit()
        sys.exit(1)
