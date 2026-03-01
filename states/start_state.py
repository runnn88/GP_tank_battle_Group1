import pygame
from states.base_state import BaseState
from utils.helpers import draw_text_with_outline

class StartState(BaseState):
    def __init__(self, state_machine):
        super().__init__(state_machine)
        # Fonts for game title and button text
        # self.title_font = pygame.font.SysFont(None, 96)
        self.title_font = pygame.font.Font("assets/fonts/Tricky Jimmy.ttf", 96)
        self.button_font = pygame.font.Font("assets/fonts/NanoPixDEMO-Regular.ttf", 48)  # Font for buttons
        self.hover_scale = 1.1  # Scale factor for hover effect

        # Background and Sounds
        self.background = pygame.image.load("assets/BG/bgmainmenu.png").convert()
        self.background = pygame.transform.scale(self.background, self.state_machine.screen.get_size())
        self.click_sound = pygame.mixer.Sound("assets/sounds/click.mp3")
        
        # Loop bgm
        # self.bgm = pygame.mixer.Sound("assets/sounds/bgm.mp3")
        # self.bgm.set_volume(0.5)
        # self.bgm.play(-1)  # Loop background music

        # Define buttons in the middle of the screen
        screen_rect = self.state_machine.screen.get_rect()

        # "Press Start" button
        self.button_rect = pygame.Rect(0, 0, 320, 90)
        self.button_rect.center = (screen_rect.centerx, screen_rect.centery + 80)

        # "Settings" button (placed below Start)
        self.setting_button_rect = pygame.Rect(0, 0, 240, 80)
        self.setting_button_rect.center = (screen_rect.centerx, screen_rect.centery + 140)

        # "Quit" button
        self.quit_button_rect = pygame.Rect(0, 0, 240, 80)
        self.quit_button_rect.center = (screen_rect.centerx, screen_rect.centery + 200)

        # Pre-render button labels
        # self.button_text = self.button_font.render("Start", True, (0, 0, 0))
        # self.setting_text = self.button_font.render("Settings", True, (0, 0, 0))
        # self.quit_text = self.button_font.render("Quit", True, (0, 0, 0))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # Handle mouse clicks on buttons
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.button_rect.collidepoint(event.pos):
                    self.click_sound.play()
                    self.state_machine.change_state("gameplay")
                elif self.quit_button_rect.collidepoint(event.pos):
                    self.click_sound.play()
                    return False

        return True

    def update(self, dt):
        pass

    def render(self, screen):
        screen.fill((20, 20, 20))
        screen.blit(self.background, (0, 0))

        # Tiêu đề
        title_text = "TANK BATTLE: CHAOS MAZE"
        center_position = (screen.get_rect().centerx, screen.get_rect().centery - 150)

        # Vẽ viền tỏa sáng
        outline_color = (255, 255, 255)  # Màu viền trắng
        for i in range(10, 0, -1):  # Vẽ 10 lớp viền
            alpha = int(255 * (i / 10))  # Độ trong suốt giảm dần
            outline_font = pygame.font.Font("assets/fonts/Tricky Jimmy.ttf", 96 + i * 2)  # Font lớn hơn chữ chính
            outline_surface = outline_font.render(title_text, True, outline_color)
            outline_surface.set_alpha(alpha)  # Đặt độ trong suốt
            outline_rect = outline_surface.get_rect(center=center_position)
            screen.blit(outline_surface, outline_rect)

        # Vẽ chữ chính
        title_font = pygame.font.Font("assets/fonts/Tricky Jimmy.ttf", 96)  # Font chữ chính
        title_surface = title_font.render(title_text, True, (255, 182, 193))  # Màu chữ chính (hồng phấn)
        title_rect = title_surface.get_rect(center=center_position)
        screen.blit(title_surface, title_rect)

        # # Vẽ tiêu đề với viền
        # title_text = "TANK BATTLE: CHAOS MAZE"

        # # Vẽ viền trắng bao quanh tiêu đề
        # outline_font = pygame.font.Font("assets/fonts/Tricky Jimmy.ttf", 100)  # Font lớn hơn chữ chính
        # title_outline = outline_font.render(title_text, True, (255, 255, 255))  # Màu viền trắng
        # title_outline_rect = title_outline.get_rect(center=(screen.get_rect().centerx, screen.get_rect().centery - 150))
        # screen.blit(title_outline, title_outline_rect)

        # # Vẽ chữ chính
        # title_font = pygame.font.Font("assets/fonts/Tricky Jimmy.ttf", 96)  # Font chữ chính
        # title_surface = title_font.render(title_text, True, (255, 182, 193))  # Màu chữ chính (hồng phấn)
        # title_rect = title_surface.get_rect(center=(screen.get_rect().centerx, screen.get_rect().centery - 150))
        # screen.blit(title_surface, title_rect)

        # Vẽ viền trắng bao quanh chữ Title
        # outline_font = pygame.font.Font("assets/fonts/Tricky Jimmy.ttf", 98)  # Font lớn hơn chữ chính
        # title_outline = outline_font.render("TANK BATTLE: CHAOS MAZE", True, (255, 255, 255))  # Màu viền trắng
        # title_outline_rect = title_outline.get_rect(center=(screen.get_rect().centerx, screen.get_rect().centery - 150))
        # screen.blit(title_outline, title_outline_rect)

        # # Draw game title
        # title_text = self.title_font.render("TANK BATTLE: CHAOS MAZE", True, (255, 182, 193))
        # title_rect = title_text.get_rect(center=(screen.get_rect().centerx, screen.get_rect().centery - 150))
        # screen.blit(title_text, title_rect)
        # draw_text_with_outline(screen, "TANK BATTLE: CHAOS MAZE", self.title_font, 50, 50, (255,255,255), (0,0,0))

        # # Draw "Press Start" button
        # pygame.draw.rect(screen, (240, 240, 240), self.button_rect)
        # pygame.draw.rect(screen, (255, 255, 255), self.button_rect, 4)
        # button_text_rect = self.button_text.get_rect(center=self.button_rect.center)
        # screen.blit(self.button_text, button_text_rect)

        # # Draw "Quit" button
        # pygame.draw.rect(screen, (220, 80, 80), self.quit_button_rect)
        # pygame.draw.rect(screen, (255, 255, 255), self.quit_button_rect, 4)
        # quit_text_rect = self.quit_text.get_rect(center=self.quit_button_rect.center)
        # screen.blit(self.quit_text, quit_text_rect)

        # # Lấy vị trí chuột
        # mouse_pos = pygame.mouse.get_pos()

        # # Vẽ nút "Press Start"
        # is_hovered_start = self.button_rect.collidepoint(mouse_pos)
        # # if is_hovered_start:
        # #     self.hover_scale = min(self.hover_scale + 0.1, 1.2)
        # # else:
        # #     self.hover_scale = max(self.hover_scale - 0.1, 1.0)
        # # scaled_button_rect = self.button_rect.inflate(
        # #     self.button_rect.width * (self.hover_scale - 1),
        # #     self.button_rect.height * (self.hover_scale - 1),
        # # )
        # # button_color = (200, 200, 200) if is_hovered_start else (240, 240, 240)
        # # pygame.draw.rect(screen, button_color, scaled_button_rect, border_radius=10)
        # # pygame.draw.rect(screen, (255, 255, 255), scaled_button_rect, 4, border_radius=10)
        # # button_color = (200, 200, 200) if is_hovered_start else (240, 240, 240)
        # # pygame.draw.rect(screen, button_color, self.button_rect, border_radius=10)
        # # pygame.draw.rect(screen, (255, 255, 255), self.button_rect, 4, border_radius=10)

        # # Thay đổi font chữ khi di chuột vào
        # button_font = pygame.font.SysFont(None, 54 if is_hovered_start else 48)
        # button_text = button_font.render("Start", True, (177, 212, 243))
        # button_text_rect = button_text.get_rect(center=self.button_rect.center)
        # screen.blit(button_text, button_text_rect)

        # # Thay đổi font chữ khi di chuột vào
        # is_hovered_setting = self.setting_button_rect.collidepoint(mouse_pos)
        # button_font = pygame.font.SysFont(None, 54 if is_hovered_setting else 48)
        # button_text = button_font.render("Settings", True, (177, 212, 243))
        # button_text_rect = button_text.get_rect(center=self.setting_button_rect.center)
        # screen.blit(button_text, button_text_rect)
        
        # # Vẽ nút "Quit"
        # is_hovered_quit = self.quit_button_rect.collidepoint(mouse_pos)
        # # quit_button_color = (200, 50, 50) if is_hovered_quit else (220, 80, 80)
        # # pygame.draw.rect(screen, quit_button_color, self.quit_button_rect, border_radius=10)
        # # pygame.draw.rect(screen, (255, 255, 255), self.quit_button_rect, 4, border_radius=10)

        # # Thay đổi font chữ khi di chuột vào
        # quit_font = pygame.font.SysFont(None, 54 if is_hovered_quit else 48)
        # quit_text = quit_font.render("Quit", True, (177, 212, 243))
        # quit_text_rect = quit_text.get_rect(center=self.quit_button_rect.center)
        # screen.blit(quit_text, quit_text_rect)


        # # Lấy vị trí chuột
        # mouse_pos = pygame.mouse.get_pos()

        # # Vẽ chữ "Start"
        # is_hovered_start = self.button_rect.collidepoint(mouse_pos)
        # button_font = pygame.font.SysFont(None, 54 if is_hovered_start else 48)
        # button_text = button_font.render("Start", True, (177, 212, 243))
        # button_text_rect = button_text.get_rect(center=self.button_rect.center)
        # screen.blit(button_text, button_text_rect)

        # # Vẽ chữ "Settings"
        # is_hovered_setting = self.setting_button_rect.collidepoint(mouse_pos)
        # button_font = pygame.font.SysFont(None, 54 if is_hovered_setting else 48)
        # button_text = button_font.render("Settings", True, (177, 212, 243))
        # button_text_rect = button_text.get_rect(center=self.setting_button_rect.center)
        # screen.blit(button_text, button_text_rect)

        # # Vẽ chữ "Quit"
        # is_hovered_quit = self.quit_button_rect.collidepoint(mouse_pos)
        # quit_font = pygame.font.SysFont(None, 54 if is_hovered_quit else 48)
        # quit_text = quit_font.render("Quit", True, (177, 212, 243))
        # quit_text_rect = quit_text.get_rect(center=self.quit_button_rect.center)
        # screen.blit(quit_text, quit_text_rect)


        # Lấy vị trí chuột
        # mouse_pos = pygame.mouse.get_pos()

        # # Vẽ chữ "Start"
        # is_hovered_start = self.button_rect.collidepoint(mouse_pos)
        # button_font = pygame.font.Font("assets/fonts/NanoPixDEMO-Regular.ttf", 54 if is_hovered_start else 48)
        # # button_font = pygame.font.SysFont(None, 54 if is_hovered_start else 48)

        # # Hiệu ứng chữ nổi: Vẽ bóng (shadow)
        # shadow_color = (100, 100, 100)  # Màu bóng (xám)
        # shadow_offset = (2, 2)  # Độ lệch của bóng
        # button_shadow = button_font.render("Start", True, shadow_color)
        # button_shadow_rect = button_shadow.get_rect(center=(self.button_rect.centerx + shadow_offset[0],
        #                                                     self.button_rect.centery + shadow_offset[1]))
        # screen.blit(button_shadow, button_shadow_rect)

        # # Vẽ chữ chính
        # button_text = button_font.render("Start", True, (177, 212, 243))
        # button_text_rect = button_text.get_rect(center=self.button_rect.center)
        # screen.blit(button_text, button_text_rect)

        # # Vẽ chữ "Settings"
        # is_hovered_setting = self.setting_button_rect.collidepoint(mouse_pos)
        # button_font = pygame.font.Font("assets/fonts/NanoPixDEMO-Regular.ttf", 54 if is_hovered_setting else 48)
        # # button_font = pygame.font.SysFont(None, 54 if is_hovered_setting else 48)

        # # Hiệu ứng chữ nổi: Vẽ bóng (shadow)
        # button_shadow = button_font.render("Settings", True, shadow_color)
        # button_shadow_rect = button_shadow.get_rect(center=(self.setting_button_rect.centerx + shadow_offset[0],
        #                                                     self.setting_button_rect.centery + shadow_offset[1]))
        # screen.blit(button_shadow, button_shadow_rect)

        # # Vẽ chữ chính
        # button_text = button_font.render("Settings", True, (177, 212, 243))
        # button_text_rect = button_text.get_rect(center=self.setting_button_rect.center)
        # screen.blit(button_text, button_text_rect)

        # # Vẽ chữ "Quit"
        # is_hovered_quit = self.quit_button_rect.collidepoint(mouse_pos)
        # quit_font = pygame.font.Font("assets/fonts/NanoPixDEMO-Regular.ttf", 54 if is_hovered_quit else 48)
        # # quit_font = pygame.font.SysFont(None, 54 if is_hovered_quit else 48)

        # # # Vẽ viền trắng bao quanh chữ "Quit"
        # # outline_font = pygame.font.Font("assets/fonts/NanoPixDEMO-Regular.ttf", 56 if is_hovered_quit else 54)  # Font lớn hơn chữ chính
        # # quit_outline = outline_font.render("Quit", True, (255, 255, 255))  # Màu viền trắng
        # # quit_outline_rect = quit_outline.get_rect(center=self.quit_button_rect.center)
        # # screen.blit(quit_outline, quit_outline_rect)

        # # Hiệu ứng chữ nổi: Vẽ bóng (shadow)
        # quit_shadow = quit_font.render("Quit", True, shadow_color)
        # quit_shadow_rect = quit_shadow.get_rect(center=(self.quit_button_rect.centerx + shadow_offset[0],
        #                                                 self.quit_button_rect.centery + shadow_offset[1]))
        # screen.blit(quit_shadow, quit_shadow_rect)

        # # Vẽ chữ chính
        # quit_text = quit_font.render("Quit", True, (177, 212, 243))
        # quit_text_rect = quit_text.get_rect(center=self.quit_button_rect.center)
        # screen.blit(quit_text, quit_text_rect)

        # Lấy vị trí chuột
        mouse_pos = pygame.mouse.get_pos()

        # Hiệu ứng chữ nổi: Vẽ viền và chữ chính cho từng nút
        def draw_button_with_outline(text, font, rect, is_hovered, text_color, shadow_color, shadow_offset):
            # Tăng kích thước font để tạo viền
            outline_font = pygame.font.Font(font, 54 if is_hovered else 48)
            outline_text = outline_font.render(text, True, shadow_color)
            outline_rect = outline_text.get_rect(center=(rect.centerx + shadow_offset[0], rect.centery + shadow_offset[1]))
            screen.blit(outline_text, outline_rect)

            # Vẽ chữ chính
            main_font = pygame.font.Font(font, 54 if is_hovered else 48)
            main_text = main_font.render(text, True, text_color)
            main_rect = main_text.get_rect(center=rect.center)
            screen.blit(main_text, main_rect)

        # Vẽ nút "Start"
        is_hovered_start = self.button_rect.collidepoint(mouse_pos)
        draw_button_with_outline(
            "Start",
            "assets/fonts/NanoPixDEMO-Regular.ttf",
            self.button_rect,
            is_hovered_start,
            (177, 212, 243),  # Màu chữ chính
            (100, 100, 100),  # Màu viền
            (2, 2)  # Độ lệch viền
        )

        # Vẽ nút "Settings"
        is_hovered_setting = self.setting_button_rect.collidepoint(mouse_pos)
        draw_button_with_outline(
            "Settings",
            "assets/fonts/NanoPixDEMO-Regular.ttf",
            self.setting_button_rect,
            is_hovered_setting,
            (177, 212, 243),  # Màu chữ chính
            (100, 100, 100),  # Màu viền
            (2, 2)  # Độ lệch viền
        )

        # Vẽ nút "Quit"
        is_hovered_quit = self.quit_button_rect.collidepoint(mouse_pos)
        draw_button_with_outline(
            "Quit",
            "assets/fonts/NanoPixDEMO-Regular.ttf",
            self.quit_button_rect,
            is_hovered_quit,
            (177, 212, 243),  # Màu chữ chính
            (100, 100, 100),  # Màu viền
            (2, 2)  # Độ lệch viền
        )