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
# CONTROLS
# =============================
PLAYER1_CONTROLS = {
    "forward": pygame.K_w,
    "backward": pygame.K_s,
    "left": pygame.K_a,
    "right": pygame.K_d,
    "shoot": pygame.K_SPACE,
}

PLAYER2_CONTROLS = {
    "forward": pygame.K_UP,
    "backward": pygame.K_DOWN,
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "shoot": pygame.K_RETURN,
}