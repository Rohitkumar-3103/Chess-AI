import pygame

from const import *
from board import Board
from dragger import Dragger
from config import Config
from square import Square

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
        self.ai_difficulty = 3

        # Clock & Time Control
        self.time_control_name = "Untimed"
        self.white_time = None
        self.black_time = None
        self.increment = 0.0
        self.last_tick = None
        self.timeout_winner = None

    def setup(self, config):
        import random
        import time
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

    def update_clock(self):
        import time
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

    # blit methods

    def show_bg(self, surface):
        theme = self.config.theme
        
        for row in range(ROWS):
            for col in range(COLS):

                # color
                color = theme.bg.light if (row + col) % 2 == 0 else theme.bg.dark
                # rect
                rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
                # blit
                pygame.draw.rect(surface, color, rect)

                # row coordinates
                if col == 0:

                    # color
                    color = theme.bg.dark if row % 2 == 0 else theme.bg.light
                    # label
                    lbl = self.config.font.render(str(ROWS-row), 1, color)
                    lbl_pos = (5, 5 + row * SQSIZE)
                    # blit
                    surface.blit(lbl, lbl_pos)

                # col coordinates
                if row == 7:

                    # color
                    color = theme.bg.dark if (row + col) % 2 == 0 else theme.bg.light
                    # label
                    lbl = self.config.font.render(Square.get_alphacol(col), 1, color)
                    lbl_pos = (col * SQSIZE + SQSIZE - 20, HEIGHT - 20)
                    # blit
                    surface.blit(lbl, lbl_pos)

    def format_time(self, seconds):
        if seconds is None:
            return "--:--"
        mins = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{mins:02d}:{secs:02d}"

    def show_status_bar(self, surface):
        # Background
        rect = (0, HEIGHT, WIDTH, 80)
        pygame.draw.rect(surface, (30, 30, 30), rect)
        
        # Divider line
        pygame.draw.line(surface, (60, 60, 60), (0, HEIGHT), (WIDTH, HEIGHT), 2)
        
        # Fonts
        font_status = pygame.font.SysFont('arial', 18, bold=True)
        font_help = pygame.font.SysFont('arial', 14)
        
        # Active Player
        player_text = f"Turn: {self.next_player.upper()}"
        player_color = (240, 240, 240) if self.next_player == 'white' else (180, 180, 180)
        player_surface = font_status.render(player_text, True, player_color)
        surface.blit(player_surface, (15, HEIGHT + 15))
        
        # AI Status & Elo Bands
        elo_names = {
            1: "1 (Beginner ~400)",
            2: "2 (Casual ~800)",
            3: "3 (Intermediate ~1200)",
            4: "4 (Advanced ~1600)",
            5: "5 (Master ~2200)",
            6: "6 (Superhuman GM 3000+)"
        }
        lvl_str = elo_names.get(self.ai_difficulty, str(self.ai_difficulty))
        
        if self.ai_mode and self.auto_mode:
            ai_text = f"AUTO [{lvl_str}]"
            ai_color = (0, 220, 255)
        elif self.ai_mode:
            ai_text = f"AI [{lvl_str}]"
            ai_color = (0, 200, 100)
        else:
            ai_text = "PVP Mode"
            ai_color = (200, 100, 0)
        ai_surface = font_status.render(ai_text, True, ai_color)
        surface.blit(ai_surface, (150, HEIGHT + 15))

        # Clocks
        if self.white_time is not None:
            w_str = f"W: {self.format_time(self.white_time)}"
            b_str = f"B: {self.format_time(self.black_time)}"
            clock_text = f"{w_str} | {b_str}"
            clock_color = (255, 215, 0) if (self.white_time < 30 or self.black_time < 30) else (220, 220, 220)
            clock_surf = font_status.render(clock_text, True, clock_color)
            surface.blit(clock_surf, (410, HEIGHT + 15))
        
        # Check / Checkmate / Stalemate Status
        status_text = ""
        status_color = (255, 255, 255)
        if self.timeout_winner:
            status_text = f"{self.timeout_winner.upper()} WON ON TIME!"
            status_color = (255, 80, 80)
        elif self.checkmate:
            status_text = "CHECKMATE!"
            status_color = (255, 50, 50)
        elif self.stalemate:
            status_text = "STALEMATE!"
            status_color = (150, 150, 150)
        elif self.check:
            status_text = "CHECK!"
            status_color = (255, 150, 50)
        elif self.game_over:
            status_text = "GAME OVER"
            status_color = (150, 150, 150)
            
        if status_text:
            status_surface = font_status.render(status_text, True, status_color)
            surface.blit(status_surface, (580, HEIGHT + 15))
            
        # Help Guide / Controls
        help_text = "Keys: [M] Menu  |  [A] AI Mode  |  [R] Reset  |  [T] Theme  |  [1-6] Elo Levels"
        help_surface = font_help.render(help_text, True, (150, 150, 150))
        surface.blit(help_surface, (15, HEIGHT + 48))

    def show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLS):

                # piece ?
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece
                    
                    # all pieces except dragger piece
                    if piece is not self.dragger.piece:
                        piece.set_texture(size=80)
                        img = pygame.image.load(piece.texture)
                        img_center = col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2
                        piece.texture_rect = img.get_rect(center=img_center)
                        surface.blit(img, piece.texture_rect)

    def show_moves(self, surface):
        theme = self.config.theme

        if self.dragger.dragging:
            piece = self.dragger.piece

            # loop all valid moves
            for move in piece.moves:

                # color
                color = theme.moves.light if (move.final.row + move.final.col) % 2 == 0 else theme.moves.dark
                # rect
                rect = (move.final.col * SQSIZE, move.final.row * SQSIZE, SQSIZE, SQSIZE)
                # blit
                pygame.draw.rect(surface, color, rect)

    def show_last_move(self, surface):
        theme = self.config.theme

        if self.board.last_move:
            initial = self.board.last_move.initial
            final = self.board.last_move.final

            for pos in [initial, final]:

                # color
                color = theme.trace.light if (pos.row + pos.col) % 2 == 0 else theme.trace.dark
                # rect
                rect = (pos.col * SQSIZE, pos.row * SQSIZE, SQSIZE, SQSIZE)
                # blit
                pygame.draw.rect(surface, color, rect)

    def show_hover(self, surface):
        if self.hovered_sqr:
            
            # color
            color = (180, 180, 180)
            # rect
            rect = (self.hovered_sqr.col * SQSIZE, self.hovered_sqr.row * SQSIZE, SQSIZE, SQSIZE)
            # blit
            pygame.draw.rect(surface, color, rect, width=3)

    # other methods

    def next_turn(self):
        import time
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

    def play_sound(self, captured=False):
        if captured:
            self.config.capture_sound.play()
        else:
            self.config.move_sound.play()

    def reset(self):
        self.__init__()

    def update_game_state(self):
        """
        Update the game state (check, checkmate, stalemate)
        """
        # Check if current player is in check
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