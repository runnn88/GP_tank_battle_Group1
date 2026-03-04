import pygame
import random
from config import TILE_SIZE
from game.wall import Wall
from game.settings_manager import settings


class Level:
    def __init__(self, path):
        self.walls = []
        self.spawn_p1 = None
        self.spawn_p2 = None
        self.width = 0
        self.height = 0

        # Background
        # self.background = pygame.image.load("assets/BG/content.png").convert()

        # Load textures
        self.ground_image = pygame.image.load("assets/image/road1.png").convert_alpha()
        self.ground_image = pygame.transform.scale(
            self.ground_image, (TILE_SIZE, TILE_SIZE)
        )
        wall_image = pygame.image.load("assets/image/wall1.png").convert_alpha()
        self.wall_image = pygame.transform.scale(
            wall_image, (TILE_SIZE, TILE_SIZE)
        )
        destructible_wall_image = pygame.image.load("assets/image/road1.png").convert_alpha()
        self.destructible_wall_image = pygame.transform.scale(
            destructible_wall_image, (TILE_SIZE, TILE_SIZE)
        )

        # Decide generation mode
        if settings.random_map:
            self._generate_random()
        else:
            if path is None:
                raise ValueError("Path required when random_map is False.")
            self._load_from_file(path)

        if self.spawn_p1 is None or self.spawn_p2 is None:
            raise ValueError("Spawn points P1 or P2 not found in level file.")

        # Compute level pixel dimensions from walls (fallback to map size if no walls)
        if self.walls:
            self.width = max(w.rect.right for w in self.walls)
            self.height = max(w.rect.bottom for w in self.walls)
        else:
            self.width = settings.map_width * TILE_SIZE
            self.height = settings.map_height * TILE_SIZE

        # self.background = pygame.transform.scale(self.background, (self.width, self.height))

    # ======================================================
    # FILE LOADING 
    # ======================================================
    def _load_from_file(self, path):
        with open(path, "r") as f:
            rows = f.readlines()
        
        self.rows = [row.strip() for row in rows]

        for row_index, row in enumerate(self.rows):
            col_index = 0

            while col_index < len(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE

                # Detect P1
                if row[col_index:col_index+2] == "P1":
                    self.spawn_p1 = (
                        x + TILE_SIZE // 2,
                        y + TILE_SIZE // 2
                    )
                    col_index += 2
                    continue

                # Detect P2
                if row[col_index:col_index+2] == "P2":
                    self.spawn_p2 = (
                        x + TILE_SIZE // 2,
                        y + TILE_SIZE // 2
                    )
                    col_index += 2
                    continue

                # Detect Wall
                if row[col_index] == "W":
                    self.walls.append(Wall(x, y, TILE_SIZE, image=self.wall_image))

                # Detect Destructible Wall
                if row[col_index] == "D":
                    self.walls.append(Wall(x, y, TILE_SIZE, destructible=True, image=self.destructible_wall_image))

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

    def render(self, screen, offset=pygame.Vector2(0, 0)):
        # screen.blit(self.background, (offset.x, offset.y))
        # screen.blit(self.background, (0, 0))


        # Draw tiled background for entire level area
        # for row_index, row in enumerate(self.rows):
        #     for col_index in range(len(row)):
        #         # x = col_index * TILE_SIZE + offset.x
        #         # y = row_index * TILE_SIZE + offset.y
        #         # screen.blit(self.ground_image, (x, y))
        #         x = int(col_index * TILE_SIZE + offset.x)  # Làm tròn tọa độ x
        #         y = int(row_index * TILE_SIZE + offset.y)  # Làm tròn tọa độ y
        #         screen.blit(self.ground_image, (x, y))

        # Draw walls on top
        for wall in self.walls:
            wall.render(screen, offset)