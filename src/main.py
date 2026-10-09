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
        self.screen = pygame.display.set_mode( (WIDTH, HEIGHT + 80) )
        pygame.display.set_caption('Chess AI')
        self.game = Game()
        self.open_menu()

    def open_menu(self):
        menu = StartMenu(self.screen, WIDTH, HEIGHT + 80)
        config = menu.run()
        self.game.reset()
        self.game.setup(config)

    def show_promotion_dialog(self, color):
        dialog_width = 360
        dialog_height = 100
        dialog_x = (WIDTH - dialog_width) // 2
        dialog_y = (HEIGHT - dialog_height) // 2
        
        options = ['queen', 'rook', 'bishop', 'knight']
        rects = []
        for i in range(4):
            rect = pygame.Rect(dialog_x + 10 + i * 85, dialog_y + 10, 80, 80)
            rects.append(rect)
            
        from piece import Queen, Rook, Bishop, Knight
        pieces = [Queen(color), Rook(color), Bishop(color), Knight(color)]
        for p in pieces:
            p.set_texture(size=80)
            
        waiting = True
        choice = 'queen'
        
        while waiting:
            overlay = pygame.Surface((WIDTH, HEIGHT + 80))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(150)
            self.screen.blit(overlay, (0, 0))
            
            pygame.draw.rect(self.screen, (40, 40, 40), (dialog_x, dialog_y, dialog_width, dialog_height), border_radius=10)
            pygame.draw.rect(self.screen, (80, 80, 80), (dialog_x, dialog_y, dialog_width, dialog_height), width=3, border_radius=10)
            
            mouse_pos = pygame.mouse.get_pos()
            
            for i, rect in enumerate(rects):
                bg_color = (60, 60, 60) if rect.collidepoint(mouse_pos) else (45, 45, 45)
                pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
                pygame.draw.rect(self.screen, (120, 120, 120), rect, width=2, border_radius=8)
                
                img = pygame.image.load(pieces[i].texture)
                img_rect = img.get_rect(center=rect.center)
                self.screen.blit(img, img_rect)
                
            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for i, rect in enumerate(rects):
                            if rect.collidepoint(event.pos):
                                choice = options[i]
                                waiting = False
                                break
                                
        return choice

    def mainloop(self):
        
        screen = self.screen
        game = self.game

        while True:
            board = self.game.board
            dragger = self.game.dragger

            # Update clock time
            self.game.update_clock()

            # show methods
            game.show_bg(screen)
            game.show_last_move(screen)
            game.show_moves(screen)
            game.show_pieces(screen)
            game.show_hover(screen)
            game.show_status_bar(screen)

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

                # click
                if event.type == pygame.MOUSEBUTTONDOWN and not game.game_over:
                    dragger.update_mouse(event.pos)

                    clicked_row = dragger.mouseY // SQSIZE
                    clicked_col = dragger.mouseX // SQSIZE

                    # if clicked square is inside board range and has a piece ?
                    if Square.in_range(clicked_row, clicked_col):
                        if board.squares[clicked_row][clicked_col].has_piece():
                            piece = board.squares[clicked_row][clicked_col].piece

                            # valid piece (color) ?
                            if piece.color == game.next_player:
                                board.calc_moves(piece, clicked_row, clicked_col, bool=True)
                                dragger.save_initial(event.pos)
                                dragger.drag_piece(piece)

                                # show methods 
                                game.show_bg(screen)
                                game.show_last_move(screen)
                                game.show_moves(screen)
                                game.show_pieces(screen)
                
                # mouse motion
                elif event.type == pygame.MOUSEMOTION:
                    motion_row = event.pos[1] // SQSIZE
                    motion_col = event.pos[0] // SQSIZE

                    game.set_hover(motion_row, motion_col)

                    if dragger.dragging:
                        dragger.update_mouse(event.pos)

                        # show methods
                        game.show_bg(screen)
                        game.show_last_move(screen)
                        game.show_moves(screen)
                        game.show_pieces(screen)
                        game.show_hover(screen)
                        dragger.update_blit(screen)
                
                # click release
                elif event.type == pygame.MOUSEBUTTONUP and not game.game_over:
                    
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)

                        released_row = dragger.mouseY // SQSIZE
                        released_col = dragger.mouseX // SQSIZE

                        if Square.in_range(released_row, released_col):
                            # create possible move
                            initial = Square(dragger.initial_row, dragger.initial_col)
                            final = Square(released_row, released_col)
                            move = Move(initial, final)

                            # valid move ?
                            if board.valid_move(dragger.piece, move):
                                from piece import Pawn
                                if isinstance(dragger.piece, Pawn) and (released_row == 0 or released_row == 7):
                                    promo_choice = self.show_promotion_dialog(dragger.piece.color)
                                    move.promo_piece = promo_choice

                                # normal capture
                                captured = board.squares[released_row][released_col].has_piece()
                                board.move(dragger.piece, move)

                                board.set_true_en_passant(dragger.piece)                            

                                # sounds
                                game.play_sound(captured)

                                # show methods
                                game.show_bg(screen)
                                game.show_last_move(screen)
                                game.show_pieces(screen)
                                
                                # next turn
                                game.next_turn()
                    
                    dragger.undrag_piece()
                
                # key press
                elif event.type == pygame.KEYDOWN:
                    
                    # Open Menu Modal
                    if event.key == pygame.K_m:
                        self.open_menu()

                    # changing themes
                    elif event.key == pygame.K_t:
                        game.change_theme()

                    # resetting game
                    elif event.key == pygame.K_r:
                        game.reset()
                        
                    # toggling AI modes (Human vs AI -> AUTO AI vs AI -> PVP)
                    elif event.key == pygame.K_a:
                        if not game.ai_mode:
                            game.ai_mode = True
                            game.auto_mode = False
                        elif game.ai_mode and not game.auto_mode:
                            game.auto_mode = True
                        else:
                            game.ai_mode = False
                            game.auto_mode = False

                    # changing AI difficulty
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

                # quit application
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            pygame.display.update()


if __name__ == '__main__':
    main = Main()
    main.mainloop()