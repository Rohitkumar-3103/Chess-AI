import pygame
import sys

class StartMenu:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height

        # Default Selections
        self.selected_difficulty = "Intermediate"  # "Basic", "Intermediate", "Advanced"
        self.selected_color = "White"             # "White", "Random", "Black"
        self.selected_time = "10 min Rapid"       # "Untimed", "1 min Bullet", "3 min Blitz", "5 min Blitz", "10 min Rapid", "15+10 Rapid"

        # Fonts
        self.title_font = pygame.font.SysFont("arial", 28, bold=True)
        self.sec_font = pygame.font.SysFont("arial", 13, bold=True)
        self.item_font = pygame.font.SysFont("arial", 15, bold=True)
        self.item_sub_font = pygame.font.SysFont("arial", 12)

    def draw_robot_icon(self, surface, center_x, center_y):
        rect = pygame.Rect(0, 0, 52, 52)
        rect.center = (center_x, center_y)
        pygame.draw.rect(surface, (129, 182, 76), rect, border_radius=14)

        # Draw clean bot face
        head_rect = pygame.Rect(center_x - 14, center_y - 10, 28, 22)
        pygame.draw.rect(surface, (32, 30, 27), head_rect, border_radius=5)

        # Eyes
        pygame.draw.circle(surface, (129, 182, 76), (center_x - 6, center_y - 1), 3)
        pygame.draw.circle(surface, (129, 182, 76), (center_x + 6, center_y - 1), 3)

        # Mouth
        pygame.draw.line(surface, (129, 182, 76), (center_x - 6, center_y + 5), (center_x + 6, center_y + 5), 2)

        # Antenna
        pygame.draw.line(surface, (32, 30, 27), (center_x, center_y - 10), (center_x, center_y - 16), 2)
        pygame.draw.circle(surface, (32, 30, 27), (center_x, center_y - 17), 3)

    def draw_color_icon(self, surface, color_type, center_x, center_y, radius=8):
        if color_type == "White":
            pygame.draw.circle(surface, (240, 240, 240), (center_x, center_y), radius)
            pygame.draw.circle(surface, (180, 180, 180), (center_x, center_y), radius, width=1)
        elif color_type == "Black":
            pygame.draw.circle(surface, (20, 20, 20), (center_x, center_y), radius)
            pygame.draw.circle(surface, (140, 140, 140), (center_x, center_y), radius, width=1)
        elif color_type == "Random":
            # Half white / half black circle
            pygame.draw.circle(surface, (240, 240, 240), (center_x, center_y), radius)
            rect = pygame.Rect(center_x, center_y - radius, radius, radius * 2)
            pygame.draw.rect(surface, (40, 40, 40), rect)
            pygame.draw.circle(surface, (180, 180, 180), (center_x, center_y), radius, width=1)

    def run(self):
        """Displays the setup menu loop and returns selected configuration upon clicking Start Game"""
        running = True
        clock = pygame.time.Clock()

        # Modal layout dimensions (640x670 centered)
        modal_w = 640
        modal_h = 670
        modal_x = (self.width - modal_w) // 2
        modal_y = (self.height - modal_h) // 2

        while running:
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_click = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return self.get_config()

            # Dark overlay background
            overlay = pygame.Surface((self.width, self.height))
            overlay.fill((18, 17, 15))
            self.screen.blit(overlay, (0, 0))

            # Main Modal Container Card
            card_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)
            pygame.draw.rect(self.screen, (34, 32, 29), card_rect, border_radius=20)
            pygame.draw.rect(self.screen, (55, 52, 47), card_rect, width=2, border_radius=20)

            # -------------------------------------------------------------
            # HEADER AREA
            # -------------------------------------------------------------
            self.draw_robot_icon(self.screen, self.width // 2, modal_y + 40)

            title_surf = self.title_font.render("Play Against AI", True, (255, 255, 255))
            title_rect = title_surf.get_rect(center=(self.width // 2, modal_y + 88))
            self.screen.blit(title_surf, title_rect)

            # -------------------------------------------------------------
            # SECTION 1: CHOOSE DIFFICULTY
            # -------------------------------------------------------------
            sec1_y = modal_y + 125
            sec1_lbl = self.sec_font.render("1. CHOOSE DIFFICULTY", True, (160, 158, 150))
            self.screen.blit(sec1_lbl, (modal_x + 35, sec1_y))

            diff_options = [
                ("Basic", "Beginner (~800)", "Basic"),
                ("Intermediate", "Casual (~1400)", "Intermediate"),
                ("Advanced", "Master (~2100+)", "Advanced")
            ]

            diff_card_w = 175
            diff_card_h = 75
            diff_gap = 22
            start_diff_x = modal_x + 35

            for i, (title, sub, key) in enumerate(diff_options):
                cx = start_diff_x + i * (diff_card_w + diff_gap)
                cy = sec1_y + 25
                c_rect = pygame.Rect(cx, cy, diff_card_w, diff_card_h)

                is_selected = (self.selected_difficulty == key)
                is_hover = c_rect.collidepoint(mouse_pos)

                if is_selected:
                    bg_col = (45, 60, 32)
                    border_col = (129, 182, 76)
                    txt_col = (129, 182, 76)
                elif is_hover:
                    bg_col = (50, 48, 43)
                    border_col = (90, 87, 80)
                    txt_col = (255, 255, 255)
                else:
                    bg_col = (42, 40, 36)
                    border_col = (60, 57, 50)
                    txt_col = (230, 228, 220)

                pygame.draw.rect(self.screen, bg_col, c_rect, border_radius=12)
                pygame.draw.rect(self.screen, border_col, c_rect, width=2 if is_selected else 1, border_radius=12)

                t_s = self.item_font.render(title, True, txt_col)
                s_s = self.item_sub_font.render(sub, True, (160, 158, 150) if not is_selected else (170, 215, 130))
                self.screen.blit(t_s, t_s.get_rect(center=(cx + diff_card_w // 2, cy + 28)))
                self.screen.blit(s_s, s_s.get_rect(center=(cx + diff_card_w // 2, cy + 50)))

                if mouse_click and is_hover:
                    self.selected_difficulty = key

            # -------------------------------------------------------------
            # SECTION 2: PLAY AS
            # -------------------------------------------------------------
            sec2_y = modal_y + 235
            sec2_lbl = self.sec_font.render("2. PLAY AS", True, (160, 158, 150))
            self.screen.blit(sec2_lbl, (modal_x + 35, sec2_y))

            color_options = [
                ("White", "White"),
                ("Random", "Random"),
                ("Black", "Black")
            ]

            col_card_w = 175
            col_card_h = 50
            start_col_x = modal_x + 35

            for i, (key, label) in enumerate(color_options):
                cx = start_col_x + i * (col_card_w + diff_gap)
                cy = sec2_y + 25
                c_rect = pygame.Rect(cx, cy, col_card_w, col_card_h)

                is_selected = (self.selected_color == key)
                is_hover = c_rect.collidepoint(mouse_pos)

                if is_selected:
                    bg_col = (45, 60, 32)
                    border_col = (129, 182, 76)
                    txt_col = (129, 182, 76)
                elif is_hover:
                    bg_col = (50, 48, 43)
                    border_col = (90, 87, 80)
                    txt_col = (255, 255, 255)
                else:
                    bg_col = (42, 40, 36)
                    border_col = (60, 57, 50)
                    txt_col = (230, 228, 220)

                pygame.draw.rect(self.screen, bg_col, c_rect, border_radius=12)
                pygame.draw.rect(self.screen, border_col, c_rect, width=2 if is_selected else 1, border_radius=12)

                # Draw custom circle icon + label
                lbl_s = self.item_font.render(label, True, txt_col)
                total_w = 18 + lbl_s.get_width()
                start_x = cx + (col_card_w - total_w) // 2
                self.draw_color_icon(self.screen, key, start_x + 8, cy + 25, radius=7)
                self.screen.blit(lbl_s, (start_x + 22, cy + 14))

                if mouse_click and is_hover:
                    self.selected_color = key

            # -------------------------------------------------------------
            # SECTION 3: TIME CONTROL
            # -------------------------------------------------------------
            sec3_y = modal_y + 330
            sec3_lbl = self.sec_font.render("3. TIME CONTROL", True, (160, 158, 150))
            self.screen.blit(sec3_lbl, (modal_x + 35, sec3_y))

            time_options = [
                ["Untimed", "1 min Bullet", "3 min Blitz"],
                ["5 min Blitz", "10 min Rapid", "15+10 Rapid"]
            ]

            time_card_w = 175
            time_card_h = 45

            for row_idx, row in enumerate(time_options):
                for col_idx, t_label in enumerate(row):
                    cx = start_col_x + col_idx * (time_card_w + diff_gap)
                    cy = sec3_y + 25 + row_idx * 55
                    c_rect = pygame.Rect(cx, cy, time_card_w, time_card_h)

                    is_selected = (self.selected_time == t_label)
                    is_hover = c_rect.collidepoint(mouse_pos)

                    if is_selected:
                        bg_col = (45, 60, 32)
                        border_col = (129, 182, 76)
                        txt_col = (129, 182, 76)
                    elif is_hover:
                        bg_col = (50, 48, 43)
                        border_col = (90, 87, 80)
                        txt_col = (255, 255, 255)
                    else:
                        bg_col = (42, 40, 36)
                        border_col = (60, 57, 50)
                        txt_col = (230, 228, 220)

                    pygame.draw.rect(self.screen, bg_col, c_rect, border_radius=10)
                    pygame.draw.rect(self.screen, border_col, c_rect, width=2 if is_selected else 1, border_radius=10)

                    ts_s = self.item_font.render(t_label, True, txt_col)
                    self.screen.blit(ts_s, ts_s.get_rect(center=c_rect.center))

                    if mouse_click and is_hover:
                        self.selected_time = t_label

            # -------------------------------------------------------------
            # START GAME BUTTON
            # -------------------------------------------------------------
            btn_w = 570
            btn_h = 55
            btn_x = modal_x + 35
            btn_y = modal_y + 570
            btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

            btn_hover = btn_rect.collidepoint(mouse_pos)
            btn_bg = (145, 200, 85) if btn_hover else (129, 182, 76)

            pygame.draw.rect(self.screen, btn_bg, btn_rect, border_radius=14)

            btn_font = pygame.font.SysFont("arial", 18, bold=True)
            btn_text = btn_font.render("Start Game", True, (20, 20, 20))
            self.screen.blit(btn_text, btn_text.get_rect(center=btn_rect.center))

            if mouse_click and btn_hover:
                return self.get_config()

            pygame.display.update()
            clock.tick(60)

    def get_config(self):
        # Map selected difficulty to numerical level (1-6)
        if self.selected_difficulty == "Basic":
            level = 2
        elif self.selected_difficulty == "Intermediate":
            level = 4
        else:  # "Advanced"
            level = 6

        return {
            "difficulty": level,
            "color": self.selected_color,
            "time_control": self.selected_time
        }
