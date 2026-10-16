import pygame
import os
import time

from const import *
from board import Board
from dragger import Dragger
from config import Config
from square import Square

def create_reticle_surface(size, color_rgb, alpha=255):
    """
    Renders high-fidelity rounded-corner tactical viewfinder brackets matching
    modern optical reticles and responsive square highlights.
    """
    scale = 4
    S = size * scale
    pad = 5 * scale
    arm = 22 * scale
    rad = 12 * scale
    thick = 5 * scale
    half_th = thick / 2

    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    w = S - 2 * pad
    h = S - 2 * pad
    c = (*color_rgb, alpha)
    pygame.draw.rect(surf, c, (pad, pad, w, h), width=int(thick), border_radius=int(rad))

    eraser = (0, 0, 0, 0)
    surf.fill(eraser, (pad + arm, pad - scale, w - 2 * arm, thick + 2 * scale))
    surf.fill(eraser, (pad + arm, pad + h - thick - scale, w - 2 * arm, thick + 2 * scale))
    surf.fill(eraser, (pad - scale, pad + arm, thick + 2 * scale, h - 2 * arm))
    surf.fill(eraser, (pad + w - thick - scale, pad + arm, thick + 2 * scale, h - 2 * arm))

    for x, y in [
        (pad + arm, pad + half_th), (pad + half_th, pad + arm),
        (pad + w - arm, pad + half_th), (pad + w - half_th, pad + arm),
        (pad + arm, pad + h - half_th), (pad + half_th, pad + h - arm),
        (pad + w - arm, pad + h - half_th), (pad + w - half_th, pad + h - arm)
    ]:
        pygame.draw.circle(surf, c, (x, y), int(half_th))

    return pygame.transform.smoothscale(surf, (size, size))


class Game:

    def __init__(self):
        self.next_player = 'white'
        self.hovered_sqr = None
        self.board = Board()
        self.dragger = Dragger()
        self.config = Config()
        self.game_over = False
        self.check = False
        self.checkmate = False
        self.stalemate = False
        self.ai_mode = True
        self.auto_mode = False
        self.ai_player = 'black'
        self.ai_difficulty = 4

        # Click-to-move and Selection States
        self.selected_piece = None
        self.selected_row = None
        self.selected_col = None

        # Clock & Time Control
        self.time_control_name = "Untimed"
        self.white_time = None
        self.black_time = None
        self.increment = 0.0
        self.last_tick = None
        self.timeout_winner = None

        # UX & Visual Enhancements
        self.image_cache = {}
        self.game_over_dismissed = False
        self.hovered_btn = None
        self.active_config = None

        # Pre-render Tactical Viewfinder Reticle Surfaces
        self.reticle_surfaces = {}
        self.reticle_hover_surfaces = {}
        for c_name, c_rgb in self.config.reticle_colors.items():
            self.reticle_surfaces[c_name] = create_reticle_surface(SQSIZE, c_rgb, 255)
            self.reticle_hover_surfaces[c_name] = create_reticle_surface(SQSIZE, c_rgb, 95)

        # Modern Fonts with Segoe UI / Arial fallbacks
        font_family = "segoeui,segoe ui,helvetica,arial"
        self.font_coords = pygame.font.SysFont(font_family, 16, bold=True)
        self.font_status = pygame.font.SysFont(font_family, 13, bold=True)
        self.font_sub = pygame.font.SysFont(font_family, 11)
        self.font_badge = pygame.font.SysFont(font_family, 10, bold=True)
        self.font_clock = pygame.font.SysFont("segoeui,segoe ui,consolas,monospace", 13, bold=True)
        self.font_btn = pygame.font.SysFont(font_family, 11, bold=True)
        self.font_btn_badge = pygame.font.SysFont(font_family, 9, bold=True)
        self.font_modal_title = pygame.font.SysFont(font_family, 19, bold=True)
        self.font_modal_sub = pygame.font.SysFont(font_family, 12)

        # Toolbar Buttons Rects
        self._init_buttons()

    def _init_buttons(self):
        y = HEIGHT + 48
        h = 32
        self.buttons = {
            'menu': pygame.Rect(8, y, 80, h),
            'reset': pygame.Rect(96, y, 78, h),
            'mode': pygame.Rect(182, y, 112, h),
            'theme': pygame.Rect(302, y, 136, h),
            'reticle': pygame.Rect(446, y, 116, h),
            'level': pygame.Rect(570, y, 142, h)
        }
        # Modal buttons
        self.modal_rematch_rect = pygame.Rect(155, 385, 185, 42)
        self.modal_menu_rect = pygame.Rect(360, 385, 185, 42)
        self.modal_close_rect = pygame.Rect(550, 272, 24, 24)

    def setup(self, config):
        import random
        self.active_config = config
        self.ai_difficulty = config.get("difficulty", 4)
        chosen_color = config.get("color", "White")
        
        if chosen_color == "Random":
            chosen_color = random.choice(["White", "Black"])
            
        if chosen_color.lower() == "white":
            self.ai_player = "black"
        else:
            self.ai_player = "white"
            
        t_ctrl = config.get("time_control", "10 min Rapid")
        self.time_control_name = t_ctrl
        self.increment = 0.0
        
        if t_ctrl == "1 min Bullet":
            self.white_time = 60.0
            self.black_time = 60.0
        elif t_ctrl == "3 min Blitz":
            self.white_time = 180.0
            self.black_time = 180.0
        elif t_ctrl == "5 min Blitz":
            self.white_time = 300.0
            self.black_time = 300.0
        elif t_ctrl == "10 min Rapid":
            self.white_time = 600.0
            self.black_time = 600.0
        elif t_ctrl == "15+10 Rapid":
            self.white_time = 900.0
            self.black_time = 900.0
            self.increment = 10.0
        else: # "Untimed"
            self.white_time = None
            self.black_time = None
            
        self.last_tick = time.time()
        self.game_over_dismissed = False

    def update_clock(self):
        if self.game_over or self.white_time is None:
            return

        now = time.time()
        if self.last_tick is None:
            self.last_tick = now
            return

        dt = now - self.last_tick
        self.last_tick = now

        if self.next_player == 'white':
            self.white_time -= dt
            if self.white_time <= 0:
                self.white_time = 0.0
                self.game_over = True
                self.timeout_winner = 'black'
        else:
            self.black_time -= dt
            if self.black_time <= 0:
                self.black_time = 0.0
                self.game_over = True
                self.timeout_winner = 'white'

    def get_material_imbalance(self):
        val_map = {'pawn': 1, 'knight': 3, 'bishop': 3, 'rook': 5, 'queen': 9}
        w_total = 0
        b_total = 0
        for r in range(ROWS):
            for c in range(COLS):
                sq = self.board.squares[r][c]
                if sq.has_piece() and sq.piece.name in val_map:
                    if sq.piece.color == 'white':
                        w_total += val_map[sq.piece.name]
                    else:
                        b_total += val_map[sq.piece.name]
        return w_total - b_total

    def to_chess_board(self):
        import chess
        board = chess.Board(None) # empty board
        for row in range(ROWS):
            for col in range(COLS):
                sq = self.board.squares[row][col]
                if sq.has_piece():
                    p = sq.piece
                    if p.name == 'pawn':
                        piece_type = chess.PAWN
                    elif p.name == 'knight':
                        piece_type = chess.KNIGHT
                    elif p.name == 'bishop':
                        piece_type = chess.BISHOP
                    elif p.name == 'rook':
                        piece_type = chess.ROOK
                    elif p.name == 'queen':
                        piece_type = chess.QUEEN
                    elif p.name == 'king':
                        piece_type = chess.KING
                    else:
                        continue
                    
                    color = chess.WHITE if p.color == 'white' else chess.BLACK
                    board.set_piece_at(chess.square(col, 7 - row), chess.Piece(piece_type, color))
        
        board.turn = chess.WHITE if self.next_player == 'white' else chess.BLACK
        
        # Castling rights
        castling_rights = 0
        white_king_sq = self.board.squares[7][4]
        if white_king_sq.piece and white_king_sq.piece.name == 'king' and not white_king_sq.piece.moved:
            white_kr_sq = self.board.squares[7][7]
            if white_kr_sq.piece and white_kr_sq.piece.name == 'rook' and not white_kr_sq.piece.moved:
                castling_rights |= chess.BB_H1
            white_qr_sq = self.board.squares[7][0]
            if white_qr_sq.piece and white_qr_sq.piece.name == 'rook' and not white_qr_sq.piece.moved:
                castling_rights |= chess.BB_A1
                
        black_king_sq = self.board.squares[0][4]
        if black_king_sq.piece and black_king_sq.piece.name == 'king' and not black_king_sq.piece.moved:
            black_kr_sq = self.board.squares[0][7]
            if black_kr_sq.piece and black_kr_sq.piece.name == 'rook' and not black_kr_sq.piece.moved:
                castling_rights |= chess.BB_H8
            black_qr_sq = self.board.squares[0][0]
            if black_qr_sq.piece and black_qr_sq.piece.name == 'rook' and not black_qr_sq.piece.moved:
                castling_rights |= chess.BB_A8
                
        board.castling_rights = castling_rights
        
        # En passant
        for row in range(ROWS):
            for col in range(COLS):
                sq = self.board.squares[row][col]
                if sq.piece and sq.piece.name == 'pawn' and getattr(sq.piece, 'en_passant', False):
                    if sq.piece.color == 'white':
                        board.ep_square = chess.square(col, 2)
                    else:
                        board.ep_square = chess.square(col, 5)
                        
        return board

    # -------------------------------------------------------------
    # RENDERING METHODS
    # -------------------------------------------------------------

    def show_bg(self, surface):
        theme = self.config.theme
        
        for row in range(ROWS):
            for col in range(COLS):
                # Square background color
                is_light = (row + col) % 2 == 0
                color = theme.bg.light if is_light else theme.bg.dark
                rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)

                # Row coordinates (Ranks 8 to 1 on col 0)
                if col == 0:
                    text_color = theme.bg.dark if is_light else theme.bg.light
                    lbl = self.font_coords.render(str(ROWS - row), True, text_color)
                    surface.blit(lbl, (col * SQSIZE + 5, row * SQSIZE + 4))

                # Col coordinates (Files a to h on row 7)
                if row == 7:
                    text_color = theme.bg.dark if is_light else theme.bg.light
                    lbl = self.font_coords.render(Square.get_alphacol(col), True, text_color)
                    pos_x = col * SQSIZE + SQSIZE - lbl.get_width() - 5
                    pos_y = row * SQSIZE + SQSIZE - lbl.get_height() - 4
                    surface.blit(lbl, (pos_x, pos_y))

    def show_last_move(self, surface):
        theme = self.config.theme
        if self.board.last_move:
            initial = self.board.last_move.initial
            final = self.board.last_move.final

            hl_surf = pygame.Surface((SQSIZE, SQSIZE), pygame.SRCALPHA)
            for pos in [initial, final]:
                base_color = theme.trace.light if (pos.row + pos.col) % 2 == 0 else theme.trace.dark
                r, g, b = base_color if isinstance(base_color, tuple) else pygame.Color(base_color)[:3]
                hl_surf.fill((r, g, b, 125))
                surface.blit(hl_surf, (pos.col * SQSIZE, pos.row * SQSIZE))

    def show_check(self, surface):
        """Draws a crimson radial alert around the king when in check."""
        if self.check and not self.game_over:
            king = self.board.get_king(self.next_player)
            if king:
                for r in range(ROWS):
                    for c in range(COLS):
                        if self.board.squares[r][c].piece == king:
                            check_surf = pygame.Surface((SQSIZE, SQSIZE), pygame.SRCALPHA)
                            center = (SQSIZE // 2, SQSIZE // 2)
                            for rad, alpha in [(42, 35), (34, 65), (26, 110), (18, 170)]:
                                pygame.draw.circle(check_surf, (225, 45, 45, alpha), center, rad)
                            surface.blit(check_surf, (c * SQSIZE, r * SQSIZE))
                            return

    def show_moves(self, surface):
        """Draws signature modern dots and capture rings for valid moves, framed by tactical rounded reticles."""
        active_piece = None
        sel_row, sel_col = None, None

        if self.dragger.dragging:
            active_piece = self.dragger.piece
            sel_row = self.dragger.initial_row
            sel_col = self.dragger.initial_col
        elif self.selected_piece:
            active_piece = self.selected_piece
            sel_row = self.selected_row
            sel_col = self.selected_col

        if active_piece and sel_row is not None and sel_col is not None:
            ret_col = self.config.reticle_color

            # 1. Soft atmospheric glow behind the selected square
            bg_surf = pygame.Surface((SQSIZE, SQSIZE), pygame.SRCALPHA)
            bg_surf.fill((*ret_col, 28))
            surface.blit(bg_surf, (sel_col * SQSIZE, sel_row * SQSIZE))

            # 2. Modern Rounded Corner Viewfinder Reticle Brackets (Blue/Green/White/Red)
            ret_surf = self.reticle_surfaces.get(self.config.reticle_color_name)
            if ret_surf:
                surface.blit(ret_surf, (sel_col * SQSIZE, sel_row * SQSIZE))

            # 3. Valid move targets
            dot_surf = pygame.Surface((SQSIZE, SQSIZE), pygame.SRCALPHA)
            center = (SQSIZE // 2, SQSIZE // 2)

            for move in active_piece.moves:
                fr = move.final.row
                fc = move.final.col
                dest_sq = self.board.squares[fr][fc]
                
                is_capture = dest_sq.has_piece()
                # Check en-passant capture
                if not is_capture and active_piece.name == 'pawn' and abs(fc - move.initial.col) == 1 and dest_sq.isempty():
                    is_capture = True

                dot_surf.fill((0, 0, 0, 0))
                if is_capture:
                    # Sleek donut ring for capture target matching reticle color
                    pygame.draw.circle(dot_surf, (*ret_col, 200), center, 39, width=5)
                else:
                    # Soft translucent circular dot for empty destination
                    pygame.draw.circle(dot_surf, (*ret_col, 160), center, 14)
                    pygame.draw.circle(dot_surf, (255, 255, 255, 200), center, 6)

                surface.blit(dot_surf, (fc * SQSIZE, fr * SQSIZE))

    def show_hover(self, surface):
        if self.hovered_sqr and not self.dragger.dragging:
            # Avoid duplicate drawing over the currently selected square
            if self.selected_piece and self.hovered_sqr.row == self.selected_row and self.hovered_sqr.col == self.selected_col:
                return

            hover_ret = self.reticle_hover_surfaces.get(self.config.reticle_color_name)
            if hover_ret:
                surface.blit(hover_ret, (self.hovered_sqr.col * SQSIZE, self.hovered_sqr.row * SQSIZE))

    def show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece
                    
                    if piece is not self.dragger.piece:
                        piece.set_texture(size=80)
                        tex_path = piece.texture
                        if tex_path not in self.image_cache:
                            try:
                                self.image_cache[tex_path] = pygame.image.load(tex_path).convert_alpha()
                            except pygame.error:
                                self.image_cache[tex_path] = pygame.image.load(tex_path)
                        
                        img = self.image_cache[tex_path]
                        img_center = (col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2)
                        piece.texture_rect = img.get_rect(center=img_center)
                        surface.blit(img, piece.texture_rect)

    def format_time(self, seconds):
        if seconds is None:
            return "--:--"
        mins = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{mins:02d}:{secs:02d}"

    def draw_side_disc(self, surface, color_name, center_x, center_y, radius=7):
        if color_name == 'white':
            pygame.draw.circle(surface, (180, 178, 172), (center_x, center_y + 1), radius)
            pygame.draw.circle(surface, (245, 245, 240), (center_x, center_y), radius)
            pygame.draw.circle(surface, (255, 255, 255), (center_x - 1, center_y - 1), radius - 2)
        else:
            pygame.draw.circle(surface, (15, 15, 14), (center_x, center_y + 1), radius)
            pygame.draw.circle(surface, (30, 29, 27), (center_x, center_y), radius)
            pygame.draw.circle(surface, (70, 68, 64), (center_x, center_y), radius, width=1)

    def draw_pill(self, surface, text, x, y, bg_col, border_col, txt_col, font=None):
        if font is None:
            font = self.font_badge
        rendered = font.render(text, True, txt_col)
        w = rendered.get_width() + 12
        h = rendered.get_height() + 6
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surface, bg_col, rect, border_radius=6)
        pygame.draw.rect(surface, border_col, rect, width=1, border_radius=6)
        surface.blit(rendered, rendered.get_rect(center=rect.center))
        return rect.right

    def show_status_bar(self, surface):
        """Renders the modernized glassmorphic game control center & dashboard."""
        bar_rect = pygame.Rect(0, HEIGHT, WIDTH, BAR_HEIGHT)
        pygame.draw.rect(surface, (24, 23, 20), bar_rect)
        pygame.draw.line(surface, (45, 42, 36), (0, HEIGHT), (WIDTH, HEIGHT), 2)
        
        # Subtle glass rim highlight
        rim_surf = pygame.Surface((WIDTH, 1), pygame.SRCALPHA)
        rim_surf.fill((255, 255, 255, 20))
        surface.blit(rim_surf, (0, HEIGHT + 2))

        # ---------------------------------------------------------
        # ROW 1: TURN, MATCH STATUS, AND CLOCKS
        # ---------------------------------------------------------
        r1_y = HEIGHT + 12

        # 1. Left: Turn Indicator & Disc
        self.draw_side_disc(surface, self.next_player, 22, r1_y + 10, radius=8)
        turn_str = f"{self.next_player.capitalize()} to move"
        turn_surf = self.font_status.render(turn_str, True, (240, 238, 232))
        surface.blit(turn_surf, (37, r1_y + 1))

        # Turn state pill
        curr_x = 37 + turn_surf.get_width() + 8
        is_ai_thinking = self.ai_mode and (self.auto_mode or self.next_player == self.ai_player) and not self.game_over
        
        if self.game_over:
            curr_x = self.draw_pill(surface, "Finished", curr_x, r1_y, (45, 43, 38), (68, 64, 56), (180, 178, 172))
        elif is_ai_thinking:
            curr_x = self.draw_pill(surface, "Thinking...", curr_x, r1_y, (20, 42, 54), (40, 120, 160), (80, 200, 250))
        else:
            curr_x = self.draw_pill(surface, "Your Turn", curr_x, r1_y, (32, 48, 24), (80, 140, 50), (140, 210, 80))

        # Material imbalance
        imb = self.get_material_imbalance()
        if imb != 0:
            imb_str = f"+{imb}" if imb > 0 else f"+{abs(imb)}"
            self.draw_pill(surface, imb_str, curr_x + 4, r1_y, (36, 34, 30), (58, 55, 48), (210, 208, 200))

        # 2. Right: Digital Clocks
        clock_rx = WIDTH - 12
        if self.white_time is not None:
            # Black Clock
            b_active = (self.next_player == 'black' and not self.game_over)
            b_bg = (38, 54, 28) if b_active else (34, 32, 28)
            b_border = (129, 182, 76) if b_active else (54, 51, 45)
            b_col = (255, 90, 90) if self.black_time < 30 else (240, 238, 232)
            b_rect = pygame.Rect(clock_rx - 90, r1_y - 2, 90, 26)
            pygame.draw.rect(surface, b_bg, b_rect, border_radius=6)
            pygame.draw.rect(surface, b_border, b_rect, width=1, border_radius=6)
            b_txt = self.font_clock.render(f"B {self.format_time(self.black_time)}", True, b_col)
            surface.blit(b_txt, b_txt.get_rect(center=b_rect.center))

            # White Clock
            w_active = (self.next_player == 'white' and not self.game_over)
            w_bg = (38, 54, 28) if w_active else (34, 32, 28)
            w_border = (129, 182, 76) if w_active else (54, 51, 45)
            w_col = (255, 90, 90) if self.white_time < 30 else (240, 238, 232)
            w_rect = pygame.Rect(clock_rx - 188, r1_y - 2, 90, 26)
            pygame.draw.rect(surface, w_bg, w_rect, border_radius=6)
            pygame.draw.rect(surface, w_border, w_rect, width=1, border_radius=6)
            w_txt = self.font_clock.render(f"W {self.format_time(self.white_time)}", True, w_col)
            surface.blit(w_txt, w_txt.get_rect(center=w_rect.center))
        else:
            untimed_rect = pygame.Rect(clock_rx - 96, r1_y - 2, 96, 26)
            pygame.draw.rect(surface, (34, 32, 28), untimed_rect, border_radius=6)
            pygame.draw.rect(surface, (54, 51, 45), untimed_rect, width=1, border_radius=6)
            u_txt = self.font_sub.render("Untimed", True, (160, 157, 149))
            surface.blit(u_txt, u_txt.get_rect(center=untimed_rect.center))

        # ---------------------------------------------------------
        # ROW 2: TACTILE CLICKABLE ACTION TOOLBAR
        # ---------------------------------------------------------
        elo_names = {
            1: "Beginner",
            2: "Casual",
            3: "Intermediate",
            4: "Advanced",
            5: "Master",
            6: "Stockfish GM"
        }
        diff_str = elo_names.get(self.ai_difficulty, f"Lv.{self.ai_difficulty}")

        mode_str = "AI" if self.ai_mode and not self.auto_mode else ("Auto" if self.auto_mode else "PvP")
        theme_name = getattr(self.config.theme, 'name', 'Classic')
        reticle_name = self.config.reticle_color_name.capitalize()

        btn_defs = [
            ('menu', "Menu", "M"),
            ('reset', "Reset", "R"),
            ('mode', f"Mode: {mode_str}", "A"),
            ('theme', f"Theme: {theme_name}", "T"),
            ('reticle', f"Reticle: {reticle_name}", "C"),
            ('level', f"Lv.{self.ai_difficulty} {diff_str}", "1-6")
        ]

        # Icon widths for content centering
        icon_widths = {
            'menu': 10,
            'reset': 12,
            'mode': 11,
            'theme': 12,
            'reticle': 11,
            'level': 9
        }

        for key, label, badge in btn_defs:
            b_rect = self.buttons[key]
            is_hover = (self.hovered_btn == key)
            bg_col = (52, 49, 43) if is_hover else (36, 34, 30)
            border_col = (96, 92, 82) if is_hover else (54, 51, 45)

            pygame.draw.rect(surface, bg_col, b_rect, border_radius=7)
            pygame.draw.rect(surface, border_col, b_rect, width=1, border_radius=7)

            txt_col = (255, 255, 255) if is_hover else (225, 222, 215)
            ic_w = icon_widths.get(key, 12)
            gap_icon = 5
            gap_badge = 3
            badge_pad = 6

            b_txt = self.font_btn.render(label, True, txt_col)
            badge_surf = self.font_btn_badge.render(badge, True, (150, 147, 140))
            badge_w = badge_surf.get_width() + badge_pad

            # Calculate content layout: center icon + text + badge with snug, clean spacing
            total_w = ic_w + gap_icon + b_txt.get_width() + gap_badge + badge_w
            start_x = b_rect.x + max(4, (b_rect.w - total_w) // 2)

            ic_x = start_x
            ic_y = b_rect.centery

            # Draw dedicated sharp vector icons
            if key == 'menu':
                # 3 horizontal menu bars
                for off in [-4, 0, 4]:
                    pygame.draw.line(surface, txt_col, (ic_x, ic_y + off), (ic_x + 9, ic_y + off), 2)
            elif key == 'reset':
                # Reload circular arc with arrow
                arc_rect = pygame.Rect(ic_x, ic_y - 6, 12, 12)
                pygame.draw.arc(surface, txt_col, arc_rect, 0.5, 5.8, 2)
                pygame.draw.polygon(surface, txt_col, [(ic_x + 9, ic_y - 8), (ic_x + 13, ic_y - 4), (ic_x + 7, ic_y - 3)])
            elif key == 'mode':
                # Mini bot icon
                bot_rect = pygame.Rect(ic_x, ic_y - 5, 11, 10)
                pygame.draw.rect(surface, txt_col, bot_rect, border_radius=2)
                pygame.draw.circle(surface, bg_col, (ic_x + 3, ic_y), 1)
                pygame.draw.circle(surface, bg_col, (ic_x + 8, ic_y), 1)
            elif key == 'theme':
                # Theme color swatch (split light/dark squares)
                sw_rect = pygame.Rect(ic_x, ic_y - 6, 12, 12)
                th = self.config.theme
                pygame.draw.rect(surface, th.bg.light, (ic_x, ic_y - 6, 6, 12), border_top_left_radius=2, border_bottom_left_radius=2)
                pygame.draw.rect(surface, th.bg.dark, (ic_x + 6, ic_y - 6, 6, 12), border_top_right_radius=2, border_bottom_right_radius=2)
                pygame.draw.rect(surface, (100, 96, 88), sw_rect, width=1, border_radius=2)
            elif key == 'reticle':
                # Mini 4-corner tactical reticle icon matching active color
                ret_c = self.config.reticle_color
                # Top-Left bracket
                pygame.draw.lines(surface, ret_c, False, [(ic_x, ic_y - 2), (ic_x, ic_y - 5), (ic_x + 3, ic_y - 5)], 2)
                # Top-Right bracket
                pygame.draw.lines(surface, ret_c, False, [(ic_x + 8, ic_y - 5), (ic_x + 11, ic_y - 5), (ic_x + 11, ic_y - 2)], 2)
                # Bottom-Left bracket
                pygame.draw.lines(surface, ret_c, False, [(ic_x, ic_y + 2), (ic_x, ic_y + 5), (ic_x + 3, ic_y + 5)], 2)
                # Bottom-Right bracket
                pygame.draw.lines(surface, ret_c, False, [(ic_x + 8, ic_y + 5), (ic_x + 11, ic_y + 5), (ic_x + 11, ic_y + 2)], 2)
            elif key == 'level':
                # Lightning bolt icon
                pts = [(ic_x + 5, ic_y - 6), (ic_x + 2, ic_y), (ic_x + 6, ic_y), (ic_x + 3, ic_y + 6), (ic_x + 9, ic_y - 1), (ic_x + 6, ic_y - 1)]
                pygame.draw.polygon(surface, (255, 205, 60), pts)

            # Button Text (placed right after icon)
            text_start_x = ic_x + ic_w + gap_icon
            surface.blit(b_txt, (text_start_x, b_rect.centery - b_txt.get_height() // 2))

            # Shortcut Badge Tag (placed directly next to text with a sleek 3px gap)
            badge_x = text_start_x + b_txt.get_width() + gap_badge
            badge_rect = pygame.Rect(badge_x, b_rect.centery - 8, badge_w, 16)
            pygame.draw.rect(surface, (26, 25, 22), badge_rect, border_radius=4)
            surface.blit(badge_surf, badge_surf.get_rect(center=badge_rect.center))

    def show_game_over_banner(self, surface):
        """Displays a polished victory / draw celebration card on game completion."""
        if not self.game_over or self.game_over_dismissed:
            return

        # Modal backdrop
        backdrop = pygame.Surface((WIDTH, HEIGHT + BAR_HEIGHT), pygame.SRCALPHA)
        backdrop.fill((0, 0, 0, 140))
        surface.blit(backdrop, (0, 0))

        # Card Container
        modal_w = 480
        modal_h = 196
        modal_x = (WIDTH - modal_w) // 2
        modal_y = (HEIGHT - modal_h) // 2 - 20
        modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)

        # Drop shadow
        for i in range(12, 0, -2):
            s_rect = pygame.Rect(modal_rect.x - i, modal_rect.y - i + 4, modal_rect.w + i * 2, modal_rect.h + i * 2)
            s_surf = pygame.Surface((s_rect.w, s_rect.h), pygame.SRCALPHA)
            s_surf.fill((0, 0, 0, int(28 * (1.0 - i / 12))))
            surface.blit(s_surf, s_rect)

        pygame.draw.rect(surface, (28, 27, 24), modal_rect, border_radius=18)
        pygame.draw.rect(surface, (60, 56, 50), modal_rect, width=2, border_radius=18)

        # Glass top rim
        rim = pygame.Surface((modal_w - 36, 2), pygame.SRCALPHA)
        rim.fill((255, 255, 255, 30))
        surface.blit(rim, (modal_x + 18, modal_y + 1))

        # Close button in corner
        self.modal_close_rect = pygame.Rect(modal_x + modal_w - 34, modal_y + 12, 22, 22)
        pygame.draw.rect(surface, (42, 40, 36), self.modal_close_rect, border_radius=6)
        cx, cy = self.modal_close_rect.center
        pygame.draw.line(surface, (160, 157, 149), (cx - 4, cy - 4), (cx + 4, cy + 4), 2)
        pygame.draw.line(surface, (160, 157, 149), (cx + 4, cy - 4), (cx - 4, cy + 4), 2)

        # Outcomes Header
        if self.timeout_winner:
            w_str = self.timeout_winner.capitalize()
            title = f"{w_str} Won on Time!"
            sub = "Opponent ran out of time on the chess clock."
            title_col = (255, 120, 120)
        elif self.checkmate:
            winner = 'Black' if self.next_player == 'white' else 'White'
            title = f"{winner} Won by Checkmate!"
            sub = f"Victory by checkmate. Outstanding match."
            title_col = (129, 182, 76)
        elif self.stalemate:
            title = "Drawn by Stalemate"
            sub = "No legal moves remaining with the King safe."
            title_col = (210, 208, 200)
        else:
            title = "Game Over"
            sub = "The match has concluded."
            title_col = (210, 208, 200)

        # Draw victory star badge above title
        badge_center_x = WIDTH // 2
        badge_center_y = modal_y + 30
        pygame.draw.circle(surface, (38, 54, 28) if self.checkmate else (46, 43, 38), (badge_center_x, badge_center_y), 13)
        pygame.draw.circle(surface, (129, 182, 76) if self.checkmate else (90, 86, 78), (badge_center_x, badge_center_y), 13, width=1)
        # 4-point star in center
        p_star = [
            (badge_center_x, badge_center_y - 7),
            (badge_center_x + 2, badge_center_y - 2),
            (badge_center_x + 7, badge_center_y),
            (badge_center_x + 2, badge_center_y + 2),
            (badge_center_x, badge_center_y + 7),
            (badge_center_x - 2, badge_center_y + 2),
            (badge_center_x - 7, badge_center_y),
            (badge_center_x - 2, badge_center_y - 2)
        ]
        pygame.draw.polygon(surface, (140, 210, 80) if self.checkmate else (200, 196, 185), p_star)

        t_surf = self.font_modal_title.render(title, True, title_col)
        surface.blit(t_surf, t_surf.get_rect(center=(WIDTH // 2, modal_y + 58)))

        sub_surf = self.font_modal_sub.render(sub, True, (160, 157, 149))
        surface.blit(sub_surf, sub_surf.get_rect(center=(WIDTH // 2, modal_y + 86)))

        # Action Buttons
        self.modal_rematch_rect = pygame.Rect(modal_x + 36, modal_y + 124, 192, 44)
        self.modal_menu_rect = pygame.Rect(modal_x + 252, modal_y + 124, 192, 44)

        # Rematch button (Green accent)
        pygame.draw.rect(surface, (129, 182, 76), self.modal_rematch_rect, border_radius=10)
        rem_txt = self.font_status.render("Play Again (R)", True, (20, 26, 15))
        surface.blit(rem_txt, rem_txt.get_rect(center=self.modal_rematch_rect.center))

        # Menu button (Dark card)
        pygame.draw.rect(surface, (42, 40, 36), self.modal_menu_rect, border_radius=10)
        pygame.draw.rect(surface, (68, 64, 56), self.modal_menu_rect, width=1, border_radius=10)
        menu_txt = self.font_status.render("Setup Menu (M)", True, (240, 238, 232))
        surface.blit(menu_txt, menu_txt.get_rect(center=self.modal_menu_rect.center))

    # -------------------------------------------------------------
    # EVENT AND INPUT HANDLERS
    # -------------------------------------------------------------

    def handle_mouse_motion(self, pos):
        """Updates hover states and applies modern system cursors."""
        self.hovered_btn = None
        is_hand = False

        # Check toolbar buttons
        if pos[1] >= HEIGHT:
            for key, rect in self.buttons.items():
                if rect.collidepoint(pos):
                    self.hovered_btn = key
                    is_hand = True
                    break
        elif self.game_over and not self.game_over_dismissed:
            if (self.modal_rematch_rect and self.modal_rematch_rect.collidepoint(pos)) or \
               (self.modal_menu_rect and self.modal_menu_rect.collidepoint(pos)) or \
               (self.modal_close_rect and self.modal_close_rect.collidepoint(pos)):
                is_hand = True
        else:
            motion_row = pos[1] // SQSIZE
            motion_col = pos[0] // SQSIZE
            self.set_hover(motion_row, motion_col)

        if is_hand:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def handle_button_click(self, pos):
        """Processes clicks on status bar and modal action buttons."""
        if self.game_over and not self.game_over_dismissed:
            if self.modal_rematch_rect and self.modal_rematch_rect.collidepoint(pos):
                return 'rematch'
            if self.modal_menu_rect and self.modal_menu_rect.collidepoint(pos):
                return 'menu'
            if self.modal_close_rect and self.modal_close_rect.collidepoint(pos):
                self.game_over_dismissed = True
                return 'dismiss'

        if pos[1] >= HEIGHT:
            for key, rect in self.buttons.items():
                if rect.collidepoint(pos):
                    return key

        return None

    def next_turn(self):
        if self.white_time is not None and self.increment > 0:
            if self.next_player == 'white':
                self.white_time += self.increment
            else:
                self.black_time += self.increment

        self.next_player = 'white' if self.next_player == 'black' else 'black'
        self.last_tick = time.time()
        self.update_game_state()

    def set_hover(self, row, col):
        if Square.in_range(row, col):
            self.hovered_sqr = self.board.squares[row][col]
        else:
            self.hovered_sqr = None

    def change_theme(self):
        self.config.change_theme()

    def change_reticle_color(self):
        self.config.change_reticle_color()

    def select(self, piece, row, col):
        self.selected_piece = piece
        self.selected_row = row
        self.selected_col = col

    def deselect(self):
        self.selected_piece = None
        self.selected_row = None
        self.selected_col = None

    def play_sound(self, captured=False):
        if captured:
            self.config.capture_sound.play()
        else:
            self.config.move_sound.play()

    def reset(self):
        saved_config = self.active_config
        saved_reticle = self.config.reticle_idx
        self.__init__()
        self.config.reticle_idx = saved_reticle
        self.config.reticle_color_name = self.config.reticle_color_names[saved_reticle]
        if saved_config:
            self.setup(saved_config)

    def update_game_state(self):
        king = self.board.get_king(self.next_player)
        if king:
            self.check = self.board.is_in_check(king, None)
            self.checkmate = self.board.is_checkmate(self.next_player)
            self.stalemate = self.board.is_stalemate(self.next_player)
        else:
            self.check = False
            self.checkmate = False
            self.stalemate = False

        if self.checkmate or self.stalemate:
            self.game_over = True
            self.game_over_dismissed = False