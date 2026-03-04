import pygame
import random

from states.base_state import BaseState
from states.pause_state import PauseState

from game.level import Level
from game.tank import Tank
from game.powerup import PowerUp
from ui.hud import HUD
from config import (
    PLAYER1_CONTROLS,
    PLAYER2_CONTROLS,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    UI_SIDE_WIDTH,
    TOP_UI_HEIGHT
)

class GameplayState(BaseState):
    def __init__(self, state_machine):
        super().__init__(state_machine)

        # Background
        self.background = pygame.image.load("assets/BG/content.png").convert()
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.level = Level("data/maps/level2.txt")
        self.hud = HUD()

        self.player1 = Tank(
            position=self.level.spawn_p1,
            controls=PLAYER1_CONTROLS, 
            color=(150, 200, 255),
            turret_left_key_name="p1_turret_left",
            turret_right_key_name="p1_turret_right"
        )
        
        self.player2 = Tank(
            position=self.level.spawn_p2,
            controls=PLAYER2_CONTROLS, 
            color=(255, 100, 120),
            turret_left_key_name="p2_turret_left",
            turret_right_key_name="p2_turret_right"
        )

        play_area_width = SCREEN_WIDTH
        play_area_height = SCREEN_HEIGHT - TOP_UI_HEIGHT

        # Center horizontally
        if self.level.width <= play_area_width:
            offset_x = (play_area_width - self.level.width) / 2
        else:
            offset_x = 0

        # Center vertically trong phần dưới UI
        if self.level.height <= play_area_height:
            offset_y = TOP_UI_HEIGHT + (play_area_height - self.level.height) / 2
        else:
            offset_y = TOP_UI_HEIGHT

        self.level_offset = pygame.Vector2(offset_x, offset_y)

        # Power-up management
        self.powerups = []
        self.powerup_spawn_timer = 0
        self.powerup_spawn_interval = 3  # spawn mỗi 8s


        # Explosion timer
        self.explosion_timer = 0.0
        self.explosion_duration = 2.5  # Duration of explosion effect
        self.waiting_for_explosion = False
        self.death_text_timer = 2.0

        # Win screen animation
        self.win_alpha = 0
        self.win_scale = 0.8
        self.win_anim_speed = 2.5
        self.show_win_screen = False
        self.winner_text = ""

        self.sparkles = []
        self.sparkle_spawn_timer = 0


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if self.show_win_screen:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.state_machine.change_state("start")
                continue  # Ignore other events while win screen is active

            self.player1.handle_event(event)
            self.player2.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not isinstance(self.state_machine.current_state, PauseState):
                        self.state_machine.current_state = PauseState(self.state_machine, self)

        return True

    def update(self, dt):
        self.hud.update(dt)

        if self.show_win_screen:
            self.win_alpha = min(255, self.win_alpha + 300 * dt)
            self.win_scale = min(1.0, self.win_scale + self.win_anim_speed * dt)
            
            # Spawn sparkle
            self.sparkle_spawn_timer += dt
            if self.sparkle_spawn_timer > 0.08:
                self.sparkle_spawn_timer = 0

                sparkle = {
                    "x": random.randint(SCREEN_WIDTH//2 - 250, SCREEN_WIDTH//2 + 250),
                    "y": random.randint(SCREEN_HEIGHT//2 - 120, SCREEN_HEIGHT//2 + 120),
                    "size": random.randint(2, 5),
                    "alpha": 255,
                    "speed": random.uniform(20, 50)
                }

                self.sparkles.append(sparkle)

            # Update sparkle
            for sparkle in self.sparkles:
                sparkle["y"] -= sparkle["speed"] * dt
                sparkle["alpha"] -= 120 * dt

            # Remove dead sparkles
            self.sparkles = [s for s in self.sparkles if s["alpha"] > 0]
            return

        if self.waiting_for_explosion:
            # Update explosion timer
            self.explosion_timer += dt

            # VẪN update tank để animation chết chạy
            self.player1.update(dt, self.level.walls, self.player2)
            self.player2.update(dt, self.level.walls, self.player1)

            if self.explosion_timer >= self.explosion_duration:
                if not self.player1.alive:
                    self.winner_text = "Player 2 Wins"
                elif not self.player2.alive:
                    self.winner_text = "Player 1 Wins"
                self.show_win_screen = True
            return  # Skip updating players and level during explosion

        # Update players and check for gameover condition
        self.player1.update(dt, self.level.walls, self.player2)
        self.player2.update(dt, self.level.walls, self.player1)

        # Spawn powerup
        self.powerup_spawn_timer += dt
        if self.powerup_spawn_timer >= self.powerup_spawn_interval:
            self.powerup_spawn_timer = 0

            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(150, SCREEN_HEIGHT - 100)

            self.powerups.append(PowerUp((x, y)))

        # Update powerups
        for powerup in self.powerups:
            powerup.update(dt)

            # Check pickup P1
            if powerup.rect.collidepoint(self.player1.position):
                self.player1.apply_powerup(powerup.type, powerup.duration)
                self.powerups.remove(powerup)
                break

            # Check pickup P2
            if powerup.rect.collidepoint(self.player2.position):
                self.player2.apply_powerup(powerup.type, powerup.duration)
                self.powerups.remove(powerup)
                break

        # Remove expired
        self.powerups = [p for p in self.powerups if not p.is_expired()]

        if (self.player1.is_dying or self.player2.is_dying) and not self.waiting_for_explosion:
            self.waiting_for_explosion = True
            self.explosion_timer = 0.0


    def render(self, screen):
        screen.fill((30, 30, 30))
        screen.blit(self.background, (0, 0))

        # Draw level and tanks centered in the middle play area
        self.level.render(screen, self.level_offset)

        for powerup in self.powerups:
            powerup.render(screen, self.level_offset)
        
        self.player1.render(screen, self.level_offset)
        self.player2.render(screen, self.level_offset)

        # Draw side HUD panels on top
        self.hud.render(screen, self.player1, self.player2)

        if self.show_win_screen:
            # 🌙 Pastel overlay
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((40, 20, 60, int(self.win_alpha * 0.6)))
            screen.blit(overlay, (0, 0))

            # 💎 Glass panel
            panel_width = 500
            panel_height = 250

            panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
            pygame.draw.rect(
                panel_surface,
                (180, 150, 255, 160),
                (0, 0, panel_width, panel_height),
                border_radius=30
            )

            pygame.draw.rect(
                panel_surface,
                (255, 255, 255, 80),
                (0, 0, panel_width, panel_height),
                width=3,
                border_radius=30
            )

            # 🌸 Scale animation
            scaled_surface = pygame.transform.smoothscale(
                panel_surface,
                (int(panel_width * self.win_scale),
                int(panel_height * self.win_scale))
            )

            panel_rect = scaled_surface.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            )

            screen.blit(scaled_surface, panel_rect)

            # ✨ Sparkle effect
            for sparkle in self.sparkles:
                sparkle_surface = pygame.Surface((20, 20), pygame.SRCALPHA)

                color = (255, 230, 255, int(sparkle["alpha"]))

                pygame.draw.circle(
                    sparkle_surface,
                    color,
                    (10, 10),
                    sparkle["size"]
                )

                screen.blit(sparkle_surface, (sparkle["x"], sparkle["y"]))

            # 🌟 Winner Text
            title_font = pygame.font.Font("assets/fonts/Star Crush.ttf", 65)
            subtitle_font = pygame.font.Font("assets/fonts/Star Crush.ttf", 36)

            color = (200, 180, 255)  # pastel purple

            title_surface = title_font.render(self.winner_text, True, color)
            subtitle_surface = subtitle_font.render(
                "Press Enter to continue",
                True,
                (230, 210, 255)
            )

            title_surface.set_alpha(self.win_alpha)
            subtitle_surface.set_alpha(self.win_alpha)

            screen.blit(
                title_surface,
                title_surface.get_rect(
                    center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)
                )
            )

            screen.blit(
                subtitle_surface,
                subtitle_surface.get_rect(
                    center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
                )
            )