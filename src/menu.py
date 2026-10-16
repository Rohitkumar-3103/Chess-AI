import pygame
import sys

class StartMenu:
    """
    Modern glassmorphic setup modal for Chess-AI.
    Provides interactive controls for AI difficulty tiers, player side selection,
    and timed chess clocks with tactile hover animations and visual feedback.
    """

    def __init__(self, screen, width, height, bg_surface=None, can_dismiss=True):
        self.screen = screen
        self.width = width
        self.height = height
        self.bg_surface = bg_surface
        self.can_dismiss = can_dismiss

        # Default Selections
        self.selected_difficulty = "Intermediate"  # "Basic", "Intermediate", "Advanced"
        self.selected_color = "White"             # "White", "Random", "Black"
        self.selected_time = "10 min Rapid"       # "Untimed", "1 min Bullet", "3 min Blitz", "5 min Blitz", "10 min Rapid", "15+10 Rapid"

        # Modern Fonts with Segoe UI / Arial fallbacks
        font_family = "segoeui,segoe ui,helvetica,arial"
        self.font_title = pygame.font.SysFont(font_family, 26, bold=True)
        self.font_sub = pygame.font.SysFont(font_family, 12)
        self.font_sec = pygame.font.SysFont(font_family, 12, bold=True)
        self.font_item = pygame.font.SysFont(font_family, 15, bold=True)
        self.font_item_sub = pygame.font.SysFont(font_family, 11)
        self.font_badge = pygame.font.SysFont(font_family, 10, bold=True)
        self.font_btn = pygame.font.SysFont(font_family, 17, bold=True)
        self.font_hint = pygame.font.SysFont(font_family, 12, bold=True)

        # Modal Geometry (Centered inside screen)
        self.modal_w = 630
        self.modal_h = 676
        self.modal_x = (self.width - self.modal_w) // 2
        self.modal_y = (self.height - self.modal_h) // 2

        # Color Palette Tokens
        self.c_overlay = (14, 13, 11, 215)
        self.c_modal_bg = (28, 27, 24)
        self.c_modal_border = (58, 54, 48)
        self.c_card_bg = (36, 34, 30)
        self.c_card_border = (54, 51, 45)
        self.c_card_hover_bg = (46, 44, 38)
        self.c_card_hover_border = (86, 82, 73)
        self.c_card_sel_bg = (38, 54, 28)
        self.c_card_sel_border = (129, 182, 76)
        self.c_accent_green = (129, 182, 76)
        self.c_accent_hover = (145, 204, 86)
        self.c_accent_dark = (92, 138, 50)
        self.c_txt_primary = (255, 255, 255)
        self.c_txt_muted = (160, 157, 149)
        self.c_txt_accent = (140, 198, 84)

    def draw_shadow(self, surface, rect, radius=22, blur=12):
        """Draws a soft multilayered drop shadow behind a rect."""
        shadow_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for i in range(blur, 0, -2):
            alpha = int(35 * (1.0 - i / blur))
            s_rect = pygame.Rect(rect.x - i, rect.y - i + 4, rect.w + i * 2, rect.h + i * 2)
            pygame.draw.rect(shadow_surf, (0, 0, 0, alpha), s_rect, border_radius=radius + i)
        surface.blit(shadow_surf, (0, 0))

    def draw_robot_icon(self, surface, center_x, center_y):
        """Draws a clean, solid robot badge with no highlight clipping or glare artifacts."""
        badge_rect = pygame.Rect(0, 0, 52, 52)
        badge_rect.center = (center_x, center_y)
        pygame.draw.rect(surface, self.c_accent_green, badge_rect, border_radius=14)

        # Bot face frame
        face_rect = pygame.Rect(center_x - 14, center_y - 10, 28, 22)
        pygame.draw.rect(surface, (32, 30, 27), face_rect, border_radius=5)

        # Eyes (clean solid green, no white glare)
        pygame.draw.circle(surface, self.c_accent_green, (center_x - 6, center_y - 1), 3)
        pygame.draw.circle(surface, self.c_accent_green, (center_x + 6, center_y - 1), 3)

        # Mouth bar
        pygame.draw.line(surface, self.c_accent_green, (center_x - 6, center_y + 5), (center_x + 6, center_y + 5), 2)

        # Antenna
        pygame.draw.line(surface, (32, 30, 27), (center_x, center_y - 10), (center_x, center_y - 16), 2)
        pygame.draw.circle(surface, (32, 30, 27), (center_x, center_y - 17), 3)

    def draw_color_icon(self, surface, color_type, center_x, center_y, radius=10):
        """Draws a tactile 3D piece disc for White, Black, or Random side."""
        if color_type == "White":
            # Ivory disc with bevel
            pygame.draw.circle(surface, (180, 178, 172), (center_x, center_y + 1), radius)
            pygame.draw.circle(surface, (245, 245, 240), (center_x, center_y), radius)
            pygame.draw.circle(surface, (255, 255, 255), (center_x - 2, center_y - 2), radius - 3)
            pygame.draw.circle(surface, (180, 178, 172), (center_x, center_y), radius, width=1)
        elif color_type == "Black":
            # Obsidian disc with metallic rim
            pygame.draw.circle(surface, (15, 15, 14), (center_x, center_y + 1), radius)
            pygame.draw.circle(surface, (30, 29, 27), (center_x, center_y), radius)
            pygame.draw.circle(surface, (60, 58, 54), (center_x, center_y), radius, width=1)
            pygame.draw.circle(surface, (50, 48, 45), (center_x - 2, center_y - 2), radius - 4)
        elif color_type == "Random":
            # Yin-yang split disc
            pygame.draw.circle(surface, (150, 148, 142), (center_x, center_y + 1), radius)
            pygame.draw.circle(surface, (245, 245, 240), (center_x, center_y), radius)
            dark_half = pygame.Rect(center_x, center_y - radius, radius, radius * 2)
            pygame.draw.rect(surface, (30, 29, 27), dark_half)
            pygame.draw.circle(surface, (120, 118, 112), (center_x, center_y), radius, width=1)

    def draw_checkmark(self, surface, center_x, center_y, radius=7):
        """Draws a clean active indicator badge with checkmark lines."""
        pygame.draw.circle(surface, self.c_accent_green, (center_x, center_y), radius)
        p1 = (center_x - 3, center_y)
        p2 = (center_x - 1, center_y + 3)
        p3 = (center_x + 3, center_y - 3)
        pygame.draw.lines(surface, (20, 26, 15), False, [p1, p2, p3], 2)

    def draw_card(self, surface, rect, is_selected, is_hover, border_radius=12):
        """Draws a modern interactive card container with tactile states."""
        if is_selected:
            bg_col = self.c_card_sel_bg
            border_col = self.c_card_sel_border
            border_w = 2
        elif is_hover:
            bg_col = self.c_card_hover_bg
            border_col = self.c_card_hover_border
            border_w = 1
        else:
            bg_col = self.c_card_bg
            border_col = self.c_card_border
            border_w = 1

        pygame.draw.rect(surface, bg_col, rect, border_radius=border_radius)
        pygame.draw.rect(surface, border_col, rect, width=border_w, border_radius=border_radius)

    def draw_badge(self, surface, text, x, y, bg_col, txt_col=(255, 255, 255)):
        """Draws a miniature pill badge tag."""
        rendered = self.font_badge.render(text, True, txt_col)
        pw = rendered.get_width() + 10
        ph = 16
        p_rect = pygame.Rect(x, y, pw, ph)
        pygame.draw.rect(surface, bg_col, p_rect, border_radius=8)
        surface.blit(rendered, rendered.get_rect(center=p_rect.center))

    def run(self):
        """Executes the setup menu loop and returns the game configuration dict."""
        running = True
        clock = pygame.time.Clock()
        mouse_down = False

        # Precompute positions inside the modal
        mx = self.modal_x
        my = self.modal_y
        mw = self.modal_w
        mh = self.modal_h

        # Dimensions for card grids (3 columns)
        card_w = 172
        card_gap = 17
        start_x = mx + (mw - (3 * card_w + 2 * card_gap)) // 2

        # Close button rect (top right)
        close_rect = pygame.Rect(mx + mw - 38, my + 16, 24, 24)

        # Start Button Rect
        btn_w = mw - (start_x - mx) * 2
        btn_h = 54
        btn_x = start_x
        btn_y = my + mh - 76
        btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

        while running:
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_down = True
                        mouse_click = True

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        mouse_down = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return self.get_config()
                    elif event.key == pygame.K_ESCAPE:
                        if self.can_dismiss:
                            return None
                        else:
                            return self.get_config()

            # -------------------------------------------------------------
            # BACKDROP & OVERLAY
            # -------------------------------------------------------------
            if self.bg_surface:
                self.screen.blit(self.bg_surface, (0, 0))
            else:
                self.screen.fill((18, 17, 15))

            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill(self.c_overlay)
            self.screen.blit(overlay, (0, 0))

            # -------------------------------------------------------------
            # MAIN MODAL CONTAINER
            # -------------------------------------------------------------
            card_rect = pygame.Rect(mx, my, mw, mh)
            self.draw_shadow(self.screen, card_rect, radius=22, blur=14)

            # Modal background
            pygame.draw.rect(self.screen, self.c_modal_bg, card_rect, border_radius=22)
            pygame.draw.rect(self.screen, self.c_modal_border, card_rect, width=2, border_radius=22)

            # Glassmorphic top rim highlight
            rim_rect = pygame.Rect(mx + 22, my + 1, mw - 44, 2)
            rim_surf = pygame.Surface((rim_rect.w, rim_rect.h), pygame.SRCALPHA)
            rim_surf.fill((255, 255, 255, 30))
            self.screen.blit(rim_surf, rim_rect)

            # Close 'X' button
            if self.can_dismiss:
                close_hover = close_rect.collidepoint(mouse_pos)
                close_bg = (60, 56, 50) if close_hover else (38, 36, 32)
                pygame.draw.rect(self.screen, close_bg, close_rect, border_radius=12)
                x_col = (255, 255, 255) if close_hover else self.c_txt_muted
                # Draw sharp vector X
                cx, cy = close_rect.center
                pygame.draw.line(self.screen, x_col, (cx - 4, cy - 4), (cx + 4, cy + 4), 2)
                pygame.draw.line(self.screen, x_col, (cx + 4, cy - 4), (cx - 4, cy + 4), 2)
                if mouse_click and close_hover:
                    return None

            # -------------------------------------------------------------
            # HEADER AREA
            # -------------------------------------------------------------
            self.draw_robot_icon(self.screen, self.width // 2, my + 44)

            title_surf = self.font_title.render("Play Against AI", True, self.c_txt_primary)
            self.screen.blit(title_surf, title_surf.get_rect(center=(self.width // 2, my + 90)))

            # -------------------------------------------------------------
            # SECTION 1: CHOOSE DIFFICULTY
            # -------------------------------------------------------------
            sec1_y = my + 130
            sec1_lbl = self.font_sec.render("1. CHOOSE DIFFICULTY", True, self.c_txt_muted)
            self.screen.blit(sec1_lbl, (start_x, sec1_y))

            diff_options = [
                ("Basic", "Beginner (~800)", "Basic", "LVL 2", (60, 130, 60)),
                ("Intermediate", "Casual (~1400)", "Intermediate", "LVL 4", (50, 110, 180)),
                ("Advanced", "Master (~2100+)", "Advanced", "LVL 6", (180, 130, 40))
            ]

            diff_h = 76
            diff_y = sec1_y + 22

            for i, (title, sub, key, tag, tag_col) in enumerate(diff_options):
                cx = start_x + i * (card_w + card_gap)
                c_rect = pygame.Rect(cx, diff_y, card_w, diff_h)

                is_selected = (self.selected_difficulty == key)
                is_hover = c_rect.collidepoint(mouse_pos)

                self.draw_card(self.screen, c_rect, is_selected, is_hover, border_radius=12)

                # Badge (LVL)
                self.draw_badge(self.screen, tag, cx + 12, diff_y + 10, tag_col)

                # Selected indicator
                if is_selected:
                    self.draw_checkmark(self.screen, cx + card_w - 18, diff_y + 18, radius=7)

                # Titles
                txt_col = self.c_txt_accent if is_selected else (self.c_txt_primary if is_hover else (225, 222, 215))
                t_s = self.font_item.render(title, True, txt_col)
                s_col = (175, 220, 140) if is_selected else self.c_txt_muted
                s_s = self.font_item_sub.render(sub, True, s_col)

                self.screen.blit(t_s, (cx + 12, diff_y + 32))
                self.screen.blit(s_s, (cx + 12, diff_y + 52))

                if mouse_click and is_hover:
                    self.selected_difficulty = key

            # -------------------------------------------------------------
            # SECTION 2: PLAY AS
            # -------------------------------------------------------------
            sec2_y = my + 238
            sec2_lbl = self.font_sec.render("2. PLAY AS", True, self.c_txt_muted)
            self.screen.blit(sec2_lbl, (start_x, sec2_y))

            color_options = [
                ("White", "First Move", "White"),
                ("Random", "50 / 50 Side", "Random"),
                ("Black", "Second Move", "Black")
            ]

            col_h = 56
            col_y = sec2_y + 22

            for i, (label, sublabel, key) in enumerate(color_options):
                cx = start_x + i * (card_w + card_gap)
                c_rect = pygame.Rect(cx, col_y, card_w, col_h)

                is_selected = (self.selected_color == key)
                is_hover = c_rect.collidepoint(mouse_pos)

                self.draw_card(self.screen, c_rect, is_selected, is_hover, border_radius=12)

                # Color icon
                self.draw_color_icon(self.screen, key, cx + 24, col_y + col_h // 2, radius=10)

                # Text
                txt_col = self.c_txt_accent if is_selected else (self.c_txt_primary if is_hover else (225, 222, 215))
                l_s = self.font_item.render(label, True, txt_col)
                sub_s = self.font_item_sub.render(sublabel, True, (175, 220, 140) if is_selected else self.c_txt_muted)

                self.screen.blit(l_s, (cx + 42, col_y + 11))
                self.screen.blit(sub_s, (cx + 42, col_y + 30))

                if is_selected:
                    self.draw_checkmark(self.screen, cx + card_w - 16, col_y + 16, radius=6)

                if mouse_click and is_hover:
                    self.selected_color = key

            # -------------------------------------------------------------
            # SECTION 3: TIME CONTROL
            # -------------------------------------------------------------
            sec3_y = my + 332
            sec3_lbl = self.font_sec.render("3. TIME CONTROL", True, self.c_txt_muted)
            self.screen.blit(sec3_lbl, (start_x, sec3_y))

            time_rows = [
                [("Untimed", "No Clock"), ("1 min Bullet", "Bullet"), ("3 min Blitz", "Blitz")],
                [("5 min Blitz", "Blitz"), ("10 min Rapid", "Rapid"), ("15+10 Rapid", "Increment")]
            ]

            time_h = 46
            time_gap_y = 10
            base_time_y = sec3_y + 22

            for r_idx, row in enumerate(time_rows):
                for c_idx, (t_label, t_type) in enumerate(row):
                    cx = start_x + c_idx * (card_w + card_gap)
                    cy = base_time_y + r_idx * (time_h + time_gap_y)
                    c_rect = pygame.Rect(cx, cy, card_w, time_h)

                    is_selected = (self.selected_time == t_label)
                    is_hover = c_rect.collidepoint(mouse_pos)

                    self.draw_card(self.screen, c_rect, is_selected, is_hover, border_radius=10)

                    # Text & Tag
                    txt_col = self.c_txt_accent if is_selected else (self.c_txt_primary if is_hover else (225, 222, 215))
                    ts_s = self.font_item.render(t_label, True, txt_col)
                    self.screen.blit(ts_s, ts_s.get_rect(center=(cx + card_w // 2, cy + time_h // 2)))

                    if is_selected:
                        self.draw_checkmark(self.screen, cx + card_w - 14, cy + 13, radius=5)

                    if mouse_click and is_hover:
                        self.selected_time = t_label

            # -------------------------------------------------------------
            # ENGINE & SELECTION SUMMARY PILL
            # -------------------------------------------------------------
            sum_y = base_time_y + 2 * time_h + time_gap_y + 16
            sum_rect = pygame.Rect(start_x, sum_y, btn_w, 36)
            pygame.draw.rect(self.screen, (24, 23, 20), sum_rect, border_radius=10)
            pygame.draw.rect(self.screen, (68, 64, 56), sum_rect, width=1, border_radius=10)

            # High-contrast, clean summary with distinct hierarchy
            diff_level = 2 if self.selected_difficulty == "Basic" else (4 if self.selected_difficulty == "Intermediate" else 6)
            engine_str = "Stockfish 17 UCI" if diff_level >= 4 else "Minimax Positional"

            segments = [
                ("Side: ", (170, 166, 158)),
                (f"{self.selected_color}", (245, 245, 240)),
                ("  •  ", (110, 106, 98)),
                ("AI: ", (170, 166, 158)),
                (f"{self.selected_difficulty} (Lv.{diff_level})", (245, 245, 240)),
                ("  •  ", (110, 106, 98)),
                (f"{self.selected_time}", (245, 245, 240)),
                ("  •  ", (110, 106, 98)),
                (f"{engine_str}", (140, 198, 84))
            ]

            surfs = [self.font_hint.render(text, True, col) for text, col in segments]
            total_text_w = sum(s.get_width() for s in surfs)
            cur_x = sum_rect.centerx - total_text_w // 2
            for s in surfs:
                self.screen.blit(s, (cur_x, sum_rect.centery - s.get_height() // 2))
                cur_x += s.get_width()

            # -------------------------------------------------------------
            # START GAME BUTTON
            # -------------------------------------------------------------
            btn_hover = btn_rect.collidepoint(mouse_pos)
            btn_press = btn_hover and mouse_down

            # Tactile button depth offset
            press_offset = 2 if btn_press else 0
            draw_btn_rect = pygame.Rect(btn_rect.x, btn_rect.y + press_offset, btn_rect.w, btn_rect.h - press_offset)

            # 3D bottom bevel shadow
            if not btn_press:
                bevel_rect = pygame.Rect(btn_rect.x, btn_rect.y + 4, btn_rect.w, btn_rect.h)
                pygame.draw.rect(self.screen, self.c_accent_dark, bevel_rect, border_radius=14)

            btn_bg = self.c_accent_hover if btn_hover else self.c_accent_green
            pygame.draw.rect(self.screen, btn_bg, draw_btn_rect, border_radius=14)

            # Draw vector play triangle & centered label
            btn_text = self.font_btn.render("Start Game", True, (20, 26, 15))
            txt_w = btn_text.get_width()
            txt_h = btn_text.get_height()
            tri_x = btn_rect.centerx - txt_w // 2 - 14
            tri_y = draw_btn_rect.centery
            p1 = (tri_x, tri_y - 7)
            p2 = (tri_x, tri_y + 7)
            p3 = (tri_x + 10, tri_y)
            pygame.draw.polygon(self.screen, (20, 26, 15), [p1, p2, p3])

            self.screen.blit(btn_text, (btn_rect.centerx - txt_w // 2 + 4, draw_btn_rect.centery - txt_h // 2))

            if mouse_click and btn_hover:
                return self.get_config()

            pygame.display.update()
            clock.tick(60)

    def get_config(self):
        """Maps selected UI options to game configuration parameters."""
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
