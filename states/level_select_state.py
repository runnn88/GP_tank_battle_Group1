import os
import re
import math
import pygame

from states.base_state import BaseState
from game.settings_manager import settings


class LevelSelectState(BaseState):
    def __init__(self, state_machine, previous_state=None):
        super().__init__(state_machine)
        self.previous_state = previous_state

        self.title_font = pygame.font.Font("assets/fonts/Star Crush.ttf", 52)
        self.text_font = pygame.font.Font("assets/fonts/NanoPixDEMO-Regular.ttf", 26)
        self.small_font = pygame.font.Font("assets/fonts/NanoPixDEMO-Regular.ttf", 20)

        self.level_entries = self._load_levels()
        self.selected_index = 0
        self.hover_index = None

        self.columns = 1
        self.content_rects = []
        self.viewport_rect = pygame.Rect(0, 0, 1, 1)
        self.scroll_y = 0
        self.max_scroll = 0

        self.on_resize(self.state_machine.screen)

    def _load_levels(self):
        maps_dir = os.path.join("data", "maps")
        entries = []
        if not os.path.isdir(maps_dir):
            return entries

        level_files = []
        for name in os.listdir(maps_dir):
            if name.lower().endswith(".txt"):
                full = os.path.join(maps_dir, name)
                if os.path.isfile(full):
                    level_files.append(full)

        def sort_key(path):
            name = os.path.basename(path).lower()
            m = re.search(r"(\d+)", name)
            num = int(m.group(1)) if m else 10_000
            return (num, name)

        level_files.sort(key=sort_key)

        for path in level_files:
            rows = self._read_rows(path)
            preview = self._build_preview(rows)
            label = os.path.splitext(os.path.basename(path))[0].upper()
            entries.append({"path": path, "label": label, "preview": preview})

        for i, entry in enumerate(entries):
            if os.path.normpath(entry["path"]) == os.path.normpath(settings.selected_level_path):
                self.selected_index = i
                break

        return entries

    def _read_rows(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return [line.rstrip("\n") for line in f]

    def _build_preview(self, rows):
        if not rows:
            surf = pygame.Surface((120, 80), pygame.SRCALPHA)
            surf.fill((30, 40, 25))
            return surf

        width_units = max(len(r) for r in rows)
        height_units = len(rows)
        if width_units <= 0 or height_units <= 0:
            surf = pygame.Surface((120, 80), pygame.SRCALPHA)
            surf.fill((30, 40, 25))
            return surf

        cell = 6
        surf = pygame.Surface((width_units * cell, height_units * cell), pygame.SRCALPHA)
        surf.fill((76, 120, 66))

        for row_idx, row in enumerate(rows):
            col = 0
            while col < len(row):
                token = row[col : col + 2]
                x = col * cell
                y = row_idx * cell
                rect = pygame.Rect(x, y, cell, cell)

                if token == "P1":
                    pygame.draw.circle(surf, (140, 220, 255), rect.center, max(2, cell // 2))
                    col += 2
                    continue

                if token == "P2":
                    pygame.draw.circle(surf, (255, 140, 180), rect.center, max(2, cell // 2))
                    col += 2
                    continue

                if row[col] == "W":
                    pygame.draw.rect(surf, (95, 95, 95), rect)
                elif row[col] == "D":
                    pygame.draw.rect(surf, (160, 120, 85), rect)
                else:
                    pygame.draw.rect(surf, (90, 140, 80), rect)
                col += 1

        return surf

    def on_resize(self, screen):
        w = screen.get_width()
        h = screen.get_height()

        margin_x = 24
        top = 108
        bottom = 72
        gap = 16

        self.viewport_rect = pygame.Rect(
            margin_x,
            top,
            max(1, w - margin_x * 2),
            max(1, h - top - bottom),
        )

        # Pick columns by width so each card remains readable.
        if self.viewport_rect.width >= 980:
            self.columns = 4
        elif self.viewport_rect.width >= 760:
            self.columns = 3
        elif self.viewport_rect.width >= 520:
            self.columns = 2
        else:
            self.columns = 1

        count = max(1, len(self.level_entries))
        rows = math.ceil(count / self.columns)

        card_w = (self.viewport_rect.width - gap * (self.columns - 1)) // self.columns
        card_w = max(180, card_w)
        card_h = 168

        self.content_rects = []
        for idx in range(count):
            r = idx // self.columns
            c = idx % self.columns
            x = c * (card_w + gap)
            y = r * (card_h + gap)
            self.content_rects.append(pygame.Rect(x, y, card_w, card_h))

        content_h = rows * card_h + max(0, rows - 1) * gap
        self.max_scroll = max(0, content_h - self.viewport_rect.height)
        self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))
        self._ensure_selected_visible()

    def _scroll_by(self, dy):
        self.scroll_y = max(0, min(self.max_scroll, self.scroll_y + dy))

    def _ensure_selected_visible(self):
        if not self.content_rects or self.selected_index >= len(self.content_rects):
            return

        rect = self.content_rects[self.selected_index]
        top_visible = self.scroll_y
        bottom_visible = self.scroll_y + self.viewport_rect.height

        pad = 8
        if rect.top - pad < top_visible:
            self.scroll_y = max(0, rect.top - pad)
        elif rect.bottom + pad > bottom_visible:
            self.scroll_y = min(self.max_scroll, rect.bottom + pad - self.viewport_rect.height)

    def _screen_to_content(self, pos):
        sx, sy = pos
        if not self.viewport_rect.collidepoint(pos):
            return None
        return (sx - self.viewport_rect.x, sy - self.viewport_rect.y + self.scroll_y)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.previous_state and hasattr(self.previous_state, "on_resume"):
                        self.previous_state.on_resume()
                    if self.previous_state:
                        self.state_machine.current_state = self.previous_state
                    else:
                        self.state_machine.change_state("start")

                elif event.key == pygame.K_LEFT:
                    self.selected_index = max(0, self.selected_index - 1)
                    self._ensure_selected_visible()

                elif event.key == pygame.K_RIGHT:
                    self.selected_index = min(len(self.level_entries) - 1, self.selected_index + 1)
                    self._ensure_selected_visible()

                elif event.key == pygame.K_UP:
                    self.selected_index = max(0, self.selected_index - self.columns)
                    self._ensure_selected_visible()

                elif event.key == pygame.K_DOWN:
                    self.selected_index = min(len(self.level_entries) - 1, self.selected_index + self.columns)
                    self._ensure_selected_visible()

                elif event.key == pygame.K_PAGEUP:
                    self._scroll_by(-self.viewport_rect.height // 2)

                elif event.key == pygame.K_PAGEDOWN:
                    self._scroll_by(self.viewport_rect.height // 2)

                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self._confirm_selection()

            if event.type == pygame.MOUSEWHEEL:
                self._scroll_by(-event.y * 48)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self._scroll_by(-48)
                elif event.button == 5:
                    self._scroll_by(48)
                elif event.button == 1:
                    content_pos = self._screen_to_content(event.pos)
                    if content_pos is not None:
                        self.hover_index = None
                        for i, rect in enumerate(self.content_rects):
                            if rect.collidepoint(content_pos):
                                self.selected_index = i
                                self._confirm_selection()
                                break

            if event.type == pygame.MOUSEMOTION:
                self.hover_index = None
                content_pos = self._screen_to_content(event.pos)
                if content_pos is not None:
                    for i, rect in enumerate(self.content_rects):
                        if rect.collidepoint(content_pos):
                            self.hover_index = i
                            self.selected_index = i
                            break

        return True

    def _confirm_selection(self):
        if not self.level_entries:
            return
        entry = self.level_entries[self.selected_index]
        settings.selected_level_path = entry["path"]
        self.state_machine.change_state("gameplay", level_path=entry["path"])

    def update(self, dt):
        pass

    def render(self, screen):
        screen.fill((20, 24, 30))

        title = self.title_font.render("SELECT LEVEL", True, (235, 200, 255))
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 42)))

        hint = self.small_font.render(
            "Mouse: click / wheel    Keys: arrows + enter    PgUp/PgDn scroll    ESC back",
            True,
            (210, 220, 235),
        )
        screen.blit(hint, hint.get_rect(center=(screen.get_width() // 2, 78)))

        if not self.level_entries:
            no_maps = self.text_font.render("No level files found in data/maps", True, (255, 180, 180))
            screen.blit(no_maps, no_maps.get_rect(center=screen.get_rect().center))
            return

        # Viewport frame
        pygame.draw.rect(screen, (45, 55, 74), self.viewport_rect, border_radius=10)
        pygame.draw.rect(screen, (110, 140, 170), self.viewport_rect, 2, border_radius=10)

        prev_clip = screen.get_clip()
        screen.set_clip(self.viewport_rect)

        for i, entry in enumerate(self.level_entries):
            if i >= len(self.content_rects):
                break

            src = self.content_rects[i]
            rect = src.move(self.viewport_rect.x, self.viewport_rect.y - self.scroll_y)

            if rect.bottom < self.viewport_rect.top or rect.top > self.viewport_rect.bottom:
                continue

            selected = i == self.selected_index
            hovered = i == self.hover_index

            fill = (42, 48, 58)
            border = (120, 140, 175)
            if hovered:
                fill = (52, 60, 74)
            if selected:
                border = (255, 210, 150)

            pygame.draw.rect(screen, fill, rect, border_radius=14)
            pygame.draw.rect(screen, border, rect, 3, border_radius=14)

            preview_area = pygame.Rect(rect.x + 12, rect.y + 12, rect.width - 24, rect.height - 52)
            preview = entry["preview"]
            if preview.get_width() > 0 and preview.get_height() > 0:
                scale = min(preview_area.width / preview.get_width(), preview_area.height / preview.get_height())
                w = max(1, int(preview.get_width() * scale))
                h = max(1, int(preview.get_height() * scale))
                scaled = pygame.transform.scale(preview, (w, h))
                dst = scaled.get_rect(center=preview_area.center)
                screen.blit(scaled, dst)

            label = self.text_font.render(entry["label"], True, (235, 235, 245))
            screen.blit(label, label.get_rect(center=(rect.centerx, rect.bottom - 20)))

        screen.set_clip(prev_clip)

        # Scrollbar
        if self.max_scroll > 0:
            bar_w = 8
            bar_h = self.viewport_rect.height
            bar_x = self.viewport_rect.right - bar_w - 4
            bar_y = self.viewport_rect.y + 2
            track = pygame.Rect(bar_x, bar_y, bar_w, bar_h - 4)
            pygame.draw.rect(screen, (70, 80, 95), track, border_radius=4)

            thumb_h = max(26, int(track.height * (self.viewport_rect.height / (self.viewport_rect.height + self.max_scroll))))
            thumb_y = track.y + int((track.height - thumb_h) * (self.scroll_y / self.max_scroll))
            thumb = pygame.Rect(track.x, thumb_y, track.width, thumb_h)
            pygame.draw.rect(screen, (180, 200, 225), thumb, border_radius=4)