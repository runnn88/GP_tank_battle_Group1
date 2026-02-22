import pygame
from config import TILE_SIZE
from game.wall import Wall


class Level:
    def __init__(self, path):
        self.walls = []
        self.spawn_p1 = None
        self.spawn_p2 = None

        with open(path, "r") as f:
            rows = f.readlines()

        for row_index, row in enumerate(rows):
            row = row.strip()
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
                    self.walls.append(Wall(x, y, TILE_SIZE))

                col_index += 1

        if self.spawn_p1 is None or self.spawn_p2 is None:
            raise ValueError("Spawn points P1 or P2 not found in level file.")

    # ✅ ADD THIS
    def render(self, screen):
        for wall in self.walls:
            wall.render(screen)