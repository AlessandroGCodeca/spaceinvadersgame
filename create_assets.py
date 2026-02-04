import pygame
import os

# Initialize Pygame
pygame.init()

# Create assets directory if it doesn't exist
if not os.path.exists("assets"):
    os.makedirs("assets")

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
# Transparent background handled by SRCALPHA

# Function to create surface from ascii art
def create_sprite(data, color, filename):
    h = len(data)
    w = len(data[0])
    
    # Create a surface with alpha channel
    surface = pygame.Surface((w, h), pygame.SRCALPHA)
    
    for y, row in enumerate(data):
        for x, char in enumerate(row):
            if char == '1':
                surface.set_at((x, y), color)
    
    # Scale up. Original sprites are tiny.
    # Player: 13x8 -> Scale 3x -> 39x24
    # Enemies: ~11x8 -> Scale 3x -> 33x24
    scale = 3
    scaled_surface = pygame.transform.scale(surface, (w * scale, h * scale))
    pygame.image.save(scaled_surface, os.path.join("assets", filename))

# Data (1 = pixel, 0 = empty)
# Squid (8x8) - Top row invader
squid_data = [
    "00011000",
    "00111100",
    "01111110",
    "11011011",
    "11111111",
    "00100100",
    "01011010",
    "10100101"
]

# Crab (11x8) - Middle row invader
crab_data = [
    "00100000100",
    "00010001000",
    "00111111100",
    "01101110110",
    "11111111111",
    "10111111101",
    "10100000101",
    "00011011000"
]

# Octopus (12x8) - Bottom row invader
octopus_data = [
    "000011110000",
    "011111111110",
    "111111111111",
    "111001100111",
    "111111111111",
    "000110011000",
    "001101101100",
    "110000000011"
]

# Player (13x8) - approximating tank
player_data = [
    "0000001000000",
    "0000011100000",
    "0000011100000",
    "0111111111110",
    "1111111111111",
    "1111111111111",
    "1111111111111",
    "1111111111111"
]

# Bunker (22x16) - approx
bunker_data = [
    "00001111111111110000",
    "00111111111111111100",
    "01111111111111111110",
    "11111111111111111111",
    "11111111111111111111",
    "11111111111111111111",
    "11111111111111111111",
    "11111111111111111111",
    "11111111000011111111",
    "11111111000011111111",
    "11111111000011111111",
    "11111111000011111111",
    "11111111000011111111",
    "11111111000011111111",
    "11111111000011111111",
    "11111111000011111111"
]

# Bullet (1x4)
bullet_data = [
    "1",
    "1",
    "1",
    "1"
]

create_sprite(squid_data, WHITE, "enemy_squid.png")
create_sprite(crab_data, WHITE, "enemy_crab.png")
create_sprite(octopus_data, WHITE, "enemy_octopus.png")
create_sprite(player_data, GREEN, "player.png")
create_sprite(bunker_data, GREEN, "bunker.png")
create_sprite(bullet_data, WHITE, "laser.png")

print("Assets created successfully in 'assets/'")
pygame.quit()
