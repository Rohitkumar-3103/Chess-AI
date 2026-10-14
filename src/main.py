import pygame
import sys

from const import *
from game import Game
from square import Square
from move import Move
from chess_ai import ChessAI
from menu import StartMenu

class Main:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, TOTAL_HEIGHT))
        pygame.display.set_caption('Chess AI')
        self.game = Game()
        self.open_menu(is_initial=True)

    def open_menu(self, is_initial=False):
        # Render board visuals under the modal backdrop
        self.game.show_bg(self.screen)
        self.game.show_last_move(self.screen)
        self.game.show_check(self.screen)
        self.game.show_moves(self.screen)
        self.game.show_pieces(self.screen)
        self.game.show_status_bar(self.screen)
        bg_snapshot = self.screen.copy()

        menu = StartMenu(self.screen, WIDTH, TOTAL_HEIGHT, bg_surface=bg_snapshot, can_dismiss=not is_initial)
        config = menu.run()
        if config is not None:
            self.game.reset()
            self.game.setup(config)

    def show_promotion_dialog(self, color):
        dialog_width = 390
        dialog_height = 140
        dialog_x = (WIDTH - dialog_width) // 2
        dialog_y = (HEIGHT - dialog_height) // 2
        
        options = ['queen', 'rook', 'bishop', 'knight']
        names = ['Queen', 'Rook', 'Bishop', 'Knight']
        rects = []
        for i in range(4):
            rect = pygame.Rect(dialog_x + 18 + i * 90, dialog_y + 44, 76, 80)
            rects.append(rect)
            
        from piece import Queen, Rook, Bishop, Knight
        pieces = [Queen(color), Rook(color), Bishop(color), Knight(color)]
        for p in pieces:
            p.set_texture(size=80)
            
        font_title = pygame.font.SysFont("segoeui,segoe ui,helvetica,arial", 13, bold=True)
        font_name = pygame.font.SysFont("segoeui,segoe ui,helvetica,arial", 10, bold=True)
        waiting = True
        choice = 'queen'
        
        while waiting:
            overlay = pygame.Surface((WIDTH, TOTAL_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))
            
            # Modal container
            modal_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
            pygame.draw.rect(self.screen, (28, 27, 24), modal_rect, border_radius=14)
            pygame.draw.rect(self.screen, (58, 54, 48), modal_rect, width=2, border_radius=14)

            # Top rim
            rim = pygame.Surface((dialog_width - 24, 2), pygame.SRCALPHA)
            rim.fill((255, 255, 255, 30))
            self.screen.blit(rim, (dialog_x + 12, dialog_y + 1))
            
            # Header
            t_surf = font_title.render("SELECT PROMOTION PIECE", True, (240, 238, 232))
            self.screen.blit(t_surf, t_surf.get_rect(center=(WIDTH // 2, dialog_y + 22)))
            
            mouse_pos = pygame.mouse.get_pos()
            any_hover = False
            
            for i, rect in enumerate(rects):
                is_hover = rect.collidepoint(mouse_pos)
                if is_hover:
                    any_hover = True
                bg_color = (48, 45, 39) if is_hover else (36, 34, 30)
                border_color = (129, 182, 76) if is_hover else (54, 51, 45)
                
                pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
                pygame.draw.rect(self.screen, border_color, rect, width=1, border_radius=8)
                
                img = pygame.image.load(pieces[i].texture)
                img_scaled = pygame.transform.smoothscale(img, (52, 52))
                self.screen.blit(img_scaled, img_scaled.get_rect(center=(rect.centerx, rect.y + 32)))

                n_surf = font_name.render(names[i], True, (200, 198, 190) if is_hover else (150, 147, 140))
                self.screen.blit(n_surf, n_surf.get_rect(center=(rect.centerx, rect.bottom - 12)))

            if any_hover:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                
            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for i, rect in enumerate(rects):
                        if rect.collidepoint(event.pos):
                            choice = options[i]
                            waiting = False
                            break
                            
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        return choice

    def mainloop(self):
        screen = self.screen
        game = self.game

        while True:
            board = self.game.board
            dragger = self.game.dragger

            # Update clock time
            self.game.update_clock()

            # Render visuals
            game.show_bg(screen)
            game.show_last_move(screen)
            game.show_check(screen)
            game.show_moves(screen)
            game.show_pieces(screen)
            game.show_hover(screen)
            game.show_status_bar(screen)
            game.show_game_over_banner(screen)

            if dragger.dragging:
                dragger.update_blit(screen)

            # AI Move execution
            if game.ai_mode and (game.auto_mode or game.next_player == game.ai_player) and not game.game_over:
                pygame.display.update()
                if game.auto_mode:
                    pygame.time.wait(200)
                ai = ChessAI(difficulty=game.ai_difficulty)
                chess_board = game.to_chess_board()
                best_move = ai.get_best_move(chess_board, time_limit=0.5)
                
                if best_move and not game.game_over:
                    initial_row = 7 - (best_move.from_square // 8)
                    initial_col = best_move.from_square % 8
                    final_row = 7 - (best_move.to_square // 8)
                    final_col = best_move.to_square % 8
                    
                    piece = board.squares[initial_row][initial_col].piece
                    if piece:
                        board.calc_moves(piece, initial_row, initial_col, bool=True)
                        
                        ai_move = None
                        for m in piece.moves:
                            if m.initial.row == initial_row and m.initial.col == initial_col and \
                               m.final.row == final_row and m.final.col == final_col:
                                ai_move = m
                                break
                                
                        if not ai_move:
                            initial_sq = Square(initial_row, initial_col)
                            final_sq = Square(final_row, final_col)
                            ai_move = Move(initial_sq, final_sq)
                            
                        # Handle AI promotion choice
                        if best_move.promotion:
                            import chess
                            if best_move.promotion == chess.QUEEN:
                                ai_move.promo_piece = 'queen'
                            elif best_move.promotion == chess.ROOK:
                                ai_move.promo_piece = 'rook'
                            elif best_move.promotion == chess.BISHOP:
                                ai_move.promo_piece = 'bishop'
                            elif best_move.promotion == chess.KNIGHT:
                                ai_move.promo_piece = 'knight'
                                
                        captured = board.squares[final_row][final_col].has_piece()
                        board.move(piece, ai_move)
                        board.set_true_en_passant(piece)
                        game.play_sound(captured)
                        
                        game.next_turn()

            for event in pygame.event.get():

                # Mouse Click
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    btn_action = game.handle_button_click(event.pos)
                    if btn_action:
                        if btn_action == 'menu':
                            self.open_menu()
                        elif btn_action in ('reset', 'rematch'):
                            game.reset()
                        elif btn_action == 'mode':
                            if not game.ai_mode:
                                game.ai_mode = True
                                game.auto_mode = False
                            elif game.ai_mode and not game.auto_mode:
                                game.auto_mode = True
                            else:
                                game.ai_mode = False
                                game.auto_mode = False
                        elif btn_action == 'theme':
                            game.change_theme()
                        elif btn_action == 'reticle':
                            game.change_reticle_color()
                        elif btn_action == 'level':
                            game.ai_difficulty = (game.ai_difficulty % 6) + 1
                        # Click handled
                        continue

                    # If not clicked on UI button, check board piece interaction
                    if not game.game_over:
                        dragger.update_mouse(event.pos)

                        clicked_row = dragger.mouseY // SQSIZE
                        clicked_col = dragger.mouseX // SQSIZE

                        if Square.in_range(clicked_row, clicked_col):
                            # Check click-to-move destination if piece already selected
                            if game.selected_piece and not dragger.dragging:
                                initial = Square(game.selected_row, game.selected_col)
                                final = Square(clicked_row, clicked_col)
                                move = Move(initial, final)

                                if board.valid_move(game.selected_piece, move):
                                    from piece import Pawn
                                    if isinstance(game.selected_piece, Pawn) and (clicked_row == 0 or clicked_row == 7):
                                        promo_choice = self.show_promotion_dialog(game.selected_piece.color)
                                        move.promo_piece = promo_choice

                                    captured = board.squares[clicked_row][clicked_col].has_piece()
                                    board.move(game.selected_piece, move)
                                    board.set_true_en_passant(game.selected_piece)

                                    game.play_sound(captured)
                                    game.next_turn()
                                    game.deselect()
                                    continue
                                elif board.squares[clicked_row][clicked_col].has_piece() and board.squares[clicked_row][clicked_col].piece.color == game.next_player:
                                    # Switch selection to another piece of current player
                                    piece = board.squares[clicked_row][clicked_col].piece
                                    board.calc_moves(piece, clicked_row, clicked_col, bool=True)
                                    game.select(piece, clicked_row, clicked_col)
                                    dragger.save_initial(event.pos)
                                    dragger.drag_piece(piece)
                                    continue
                                else:
                                    game.deselect()
                                    continue

                            if board.squares[clicked_row][clicked_col].has_piece():
                                piece = board.squares[clicked_row][clicked_col].piece

                                if piece.color == game.next_player:
                                    board.calc_moves(piece, clicked_row, clicked_col, bool=True)
                                    game.select(piece, clicked_row, clicked_col)
                                    dragger.save_initial(event.pos)
                                    dragger.drag_piece(piece)
                
                # Mouse Motion
                elif event.type == pygame.MOUSEMOTION:
                    game.handle_mouse_motion(event.pos)

                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                
                # Mouse Click Release
                elif event.type == pygame.MOUSEBUTTONUP and not game.game_over:
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)

                        released_row = dragger.mouseY // SQSIZE
                        released_col = dragger.mouseX // SQSIZE

                        if Square.in_range(released_row, released_col):
                            # If released on same square, leave piece selected (for click-to-move)
                            if released_row == dragger.initial_row and released_col == dragger.initial_col:
                                dragger.undrag_piece()
                                continue

                            initial = Square(dragger.initial_row, dragger.initial_col)
                            final = Square(released_row, released_col)
                            move = Move(initial, final)

                            if board.valid_move(dragger.piece, move):
                                from piece import Pawn
                                if isinstance(dragger.piece, Pawn) and (released_row == 0 or released_row == 7):
                                    promo_choice = self.show_promotion_dialog(dragger.piece.color)
                                    move.promo_piece = promo_choice

                                captured = board.squares[released_row][released_col].has_piece()
                                board.move(dragger.piece, move)
                                board.set_true_en_passant(dragger.piece)                            

                                game.play_sound(captured)
                                game.next_turn()
                                game.deselect()
                            else:
                                game.deselect()
                    
                    dragger.undrag_piece()
                
                # Keyboard Shortcuts
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        self.open_menu()

                    elif event.key == pygame.K_t:
                        game.change_theme()

                    elif event.key == pygame.K_c:
                        game.change_reticle_color()

                    elif event.key == pygame.K_r:
                        game.reset()
                        
                    elif event.key == pygame.K_a:
                        if not game.ai_mode:
                            game.ai_mode = True
                            game.auto_mode = False
                        elif game.ai_mode and not game.auto_mode:
                            game.auto_mode = True
                        else:
                            game.ai_mode = False
                            game.auto_mode = False

                    elif event.key == pygame.K_1:
                        game.ai_difficulty = 1
                    elif event.key == pygame.K_2:
                        game.ai_difficulty = 2
                    elif event.key == pygame.K_3:
                        game.ai_difficulty = 3
                    elif event.key == pygame.K_4:
                        game.ai_difficulty = 4
                    elif event.key == pygame.K_5:
                        game.ai_difficulty = 5
                    elif event.key == pygame.K_6:
                        game.ai_difficulty = 6

                # Quit Application
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            pygame.display.update()


if __name__ == '__main__':
    main = Main()
    main.mainloop()