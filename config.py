import pygame

# =============================
# WINDOW SETTINGS
# =============================
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# =============================
# GAME RULES
# =============================
MAX_BULLETS = 5
MAX_BULLET_BOUNCES = 3   # -1 for infinite bounce
FRIENDLY_FIRE = False    # True = self damage allowed

# =============================
# TANK SETTINGS
# =============================
TANK_SPEED = 220
ROTATION_SPEED = 200
TANK_RADIUS = 20
TANK_HEALTH = 3

# =============================
# BULLET SETTINGS
# =============================
BULLET_SPEED = 500
BULLET_RADIUS = 5

# =============================
# MAP
# =============================
TILE_SIZE = 50

# =============================
# UI / HUD
# =============================
# Side banner width for each player (left/right)
UI_SIDE_WIDTH = 220

# Bullet shooting cooldown (seconds)
BULLET_COOLDOWN = 0.4

# =============================
# CONTROLS
# =============================
PLAYER1_CONTROLS = {
    "forward": pygame.K_w,
    "backward": pygame.K_s,
    "left": pygame.K_a,
    "right": pygame.K_d,
    # Allow multiple shoot keys (Space / F)
    "shoot": (pygame.K_SPACE, pygame.K_f),
}

PLAYER2_CONTROLS = {
    "forward": pygame.K_UP,
    "backward": pygame.K_DOWN,
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    # Allow multiple shoot keys (Enter / M)
    "shoot": (pygame.K_RETURN, pygame.K_m),
}