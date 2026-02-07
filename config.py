"""
Space Invaders Configuration Module

Centralizes all game settings, constants, and security configurations.
Separates configuration from logic for easier maintenance and security auditing.
"""

from typing import FrozenSet, Tuple

# =============================================================================
# DISPLAY SETTINGS
# =============================================================================
SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600
FPS: int = 60

# =============================================================================
# COLORS (RGB tuples)
# =============================================================================
BLACK: Tuple[int, int, int] = (0, 0, 0)
WHITE: Tuple[int, int, int] = (255, 255, 255)
GREEN: Tuple[int, int, int] = (0, 255, 0)

# =============================================================================
# PLAYER SETTINGS
# =============================================================================
PLAYER_SPEED: int = 4
PLAYER_START_X: int = 370
PLAYER_START_Y: int = 520
PLAYER_INITIAL_LIVES: int = 3
PLAYER_MAX_LIVES: int = 99

# =============================================================================
# ENEMY SETTINGS
# =============================================================================
ENEMY_SPEED: int = 1
ENEMY_DROP_DISTANCE: int = 10
ENEMY_ROWS: int = 5
ENEMY_COLS: int = 11
ENEMY_START_X: int = 75
ENEMY_START_Y: int = 100
ENEMY_X_GAP: int = 50
ENEMY_Y_GAP: int = 40
ENEMY_GAME_OVER_Y: int = 400  # Y position threshold for game over

# Enemy score values by row type
ENEMY_SCORE_SQUID: int = 30   # Row 0
ENEMY_SCORE_CRAB: int = 20    # Rows 1-2
ENEMY_SCORE_OCTOPUS: int = 10 # Rows 3-4

# =============================================================================
# BULLET SETTINGS
# =============================================================================
BULLET_SPEED: int = 10
BULLET_START_Y: int = 480

# =============================================================================
# BUNKER SETTINGS
# =============================================================================
BUNKER_COUNT: int = 4
BUNKER_Y_POSITION: int = 450
BUNKER_HEALTH: int = 10

# =============================================================================
# SCORE SETTINGS
# =============================================================================
MAX_SCORE: int = 999999
MIN_SCORE: int = 0

# =============================================================================
# ASSET SECURITY CONFIGURATION
# =============================================================================
# Whitelist of allowed asset filenames - prevents path traversal attacks
ALLOWED_ASSETS: FrozenSet[str] = frozenset({
    "player.png",
    "enemy_squid.png",
    "enemy_crab.png",
    "enemy_octopus.png",
    "bunker.png",
    "laser.png"
})

# Allowed file extensions for assets
ALLOWED_EXTENSIONS: FrozenSet[str] = frozenset({".png"})

# Assets directory name (relative to main.py)
ASSETS_DIR: str = "assets"

# Fallback surface settings for missing assets
FALLBACK_SURFACE_SIZE: Tuple[int, int] = (30, 30)
FALLBACK_SURFACE_COLOR: Tuple[int, int, int] = WHITE

# =============================================================================
# UI SETTINGS
# =============================================================================
UI_FONT_SIZE: int = 32
UI_FONT_SMALL_SIZE: int = 24
UI_BOTTOM_LINE_Y_OFFSET: int = 30
UI_LIVES_ICON_WIDTH: int = 30
UI_LIVES_ICON_HEIGHT: int = 20
