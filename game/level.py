import pygame
import random
from config import TILE_SIZE
from game.wall import Wall
from game.settings_manager import settings


class Level:
    def __init__(self, path=None):
        self.walls = []
        self.spawn_p1 = None
        self.spawn_p2 = None
        self.width = 0
        self.height = 0

        # Decide generation mode
        if settings.random_map:
            self._generate_random()
        else:
            if path is None:
                raise ValueError("Path required when random_map is False.")
            self._load_from_file(path)

        if self.spawn_p1 is None or self.spawn_p2 is None:
            raise ValueError("Spawn points P1 or P2 not found.")

        # Compute level dimensions
        if self.walls:
            self.width = max(w.rect.right for w in self.walls)
            self.height = max(w.rect.bottom for w in self.walls)
        else:
            self.width = settings.map_width * TILE_SIZE
            self.height = settings.map_height * TILE_SIZE

    # ======================================================
    # FILE LOADING 
    # ======================================================
    def _load_from_file(self, path):
        with open(path, "r") as f:
            rows = f.readlines()

        for row_index, row in enumerate(rows):
            row = row.strip()
            col_index = 0

            while col_index < len(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE

                # Detect P1
                if row[col_index:col_index + 2] == "P1":
                    self.spawn_p1 = (
                        x + TILE_SIZE // 2,
                        y + TILE_SIZE // 2
                    )
                    col_index += 2
                    continue

                # Detect P2
                if row[col_index:col_index + 2] == "P2":
                    self.spawn_p2 = (
                        x + TILE_SIZE // 2,
                        y + TILE_SIZE // 2
                    )
                    col_index += 2
                    continue

                # Detect Wall
                if row[col_index] == "W":
                    self.walls.append(Wall(x, y, TILE_SIZE))

                col_index += 1

    # ======================================================
    # RANDOM MAP GENERATION 
    # ======================================================
    def _generate_random(self):

        width = settings.map_width
        height = settings.map_height

        for y in range(height):
            for x in range(width):

                world_x = x * TILE_SIZE
                world_y = y * TILE_SIZE

                # Always keep border solid
                if x == 0 or y == 0 or x == width - 1 or y == height - 1:
                    self.walls.append(Wall(world_x, world_y, TILE_SIZE))
                    continue

                if random.random() < settings.wall_density:

                    # Determine wall type
                    if settings.allow_destructible and settings.allow_indestructible:
                        destructible = random.choice([True, False])

                    elif settings.allow_destructible:
                        destructible = True

                    elif settings.allow_indestructible:
                        destructible = False

                    else:
                        continue  # No walls allowed

                    self.walls.append(
                        Wall(world_x, world_y, TILE_SIZE, destructible)
                    )

        # Safe spawn positions in opposite corners
        self.spawn_p1 = (
            TILE_SIZE * 1.5,
            TILE_SIZE * 1.5
        )

        self.spawn_p2 = (
            TILE_SIZE * (width - 1.5),
            TILE_SIZE * (height - 1.5)
        )

    # ======================================================
    # RENDER 
    # ======================================================
    def render(self, screen, offset=pygame.Vector2(0, 0)):
        for wall in self.walls:
            wall.render(screen, offset)