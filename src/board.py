from const import *
from square import Square
from piece import *
from move import Move
from sound import Sound
import copy
import os

class Board:

    def __init__(self):
        self.squares = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(COLS)]
        self.last_move = None
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')

    def move(self, piece, move, testing=False):
        # Store the current state before making the move
        initial = move.initial
        final = move.final
        en_passant_empty = self.squares[final.row][final.col].isempty()

        # console board move update
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

        if isinstance(piece, Pawn):
            # en passant capture
            diff = final.col - initial.col
            if diff != 0 and en_passant_empty:
                # console board move update
                self.squares[initial.row][initial.col + diff].piece = None
                self.squares[final.row][final.col].piece = piece

                if not testing:
                    sound = Sound(
                        os.path.join('assets/sounds/capture.wav'))
                    sound.play()
            
            # pawn promotion
            else:
                promo_piece = getattr(move, 'promo_piece', 'queen')
                self.check_promotion(piece, final, promo_piece)

        # king castling
        if isinstance(piece, King):
            if self.castling(initial, final):
                diff = final.col - initial.col
                # Find the rook on the board
                rook_col = 0 if diff < 0 else 7
                rook = self.squares[initial.row][rook_col].piece
                if isinstance(rook, Rook):
                    rook_initial = Square(initial.row, rook_col)
                    rook_final = Square(initial.row, 3 if diff < 0 else 5)
                    rook_move = Move(rook_initial, rook_final)
                    self.move(rook, rook_move, testing=testing)

        # move
        piece.moved = True

        # clear valid moves
        piece.clear_moves()

        # set last move
        self.last_move = move

        # en passant state management
        if isinstance(piece, Pawn) and abs(final.row - initial.row) == 2:
            self.set_true_en_passant(piece)
        else:
            self.disable_all_en_passant()

    def disable_all_en_passant(self):
        for row in range(ROWS):
            for col in range(COLS):
                if isinstance(self.squares[row][col].piece, Pawn):
                    self.squares[row][col].piece.en_passant = False

    def valid_move(self, piece, move):
        return move in piece.moves

    def check_promotion(self, piece, final, promo_name='queen'):
        if final.row == 0 or final.row == 7:
            if promo_name == 'queen':
                self.squares[final.row][final.col].piece = Queen(piece.color)
            elif promo_name == 'rook':
                self.squares[final.row][final.col].piece = Rook(piece.color)
            elif promo_name == 'bishop':
                self.squares[final.row][final.col].piece = Bishop(piece.color)
            elif promo_name == 'knight':
                self.squares[final.row][final.col].piece = Knight(piece.color)

    def castling(self, initial, final):
        return abs(initial.col - final.col) == 2

    def set_true_en_passant(self, piece):
        if not isinstance(piece, Pawn):
            return
        self.disable_all_en_passant()
        piece.en_passant = True

    def in_check(self, piece, move):
        return self.is_in_check(piece, move)

    def calc_moves(self, piece, row, col, bool=True):
        '''
            Calculate all the possible (valid) moves of an specific piece on a specific position
        '''
        piece.clear_moves()
        
        def pawn_moves():

            # steps
            steps = 1 if piece.moved else 2

            # vertical moves
            start = row + piece.dir
            end = row + (piece.dir * (1 + steps))
            for possible_move_row in range(start, end, piece.dir):
                if Square.in_range(possible_move_row):
                    if self.squares[possible_move_row][col].isempty():

                        # create initial and final move squares
                        initial = Square(row, col)
                        final = Square(possible_move_row, col)

                        # create a new move
                        move = Move(initial, final)

                        # check potencial checks
                        if bool:
                            if not self.in_check(piece, move):
                                # append new move
                                piece.add_move(move)
                        else:
                            # append new move
                            piece.add_move(move)

                    # blocked
                    else: break

                # not in range
                else: break

            # diagonal moves
            possible_move_row = row + piece.dir
            possible_move_cols = [col-1, col+1]

            for possible_move_col in possible_move_cols:
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):

                        # create initial and final move squares
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)

                        # create a new move
                        move = Move(initial, final)
                        
                        # check potencial checks
                        if bool:
                            if not isinstance(final_piece, King) and not self.in_check(piece, move):
                                # append new move
                                piece.add_move(move)
                        else:
                            # append new move
                            piece.add_move(move)

            # en passant moves
            r = 3 if piece.color == 'white' else 4
            fr = 2 if piece.color == 'white' else 5

            # left en pessant
            if Square.in_range(col-1) and row == r:
                if self.squares[row][col-1].has_enemy_piece(piece.color):
                    p = self.squares[row][col-1].piece

                    if isinstance(p, Pawn):
                        if p.en_passant:

                            # create initial and final move squares
                            initial = Square(row, col)
                            final = Square(fr, col-1, p)

                            # create a new move
                            move = Move(initial, final)
                            
                            # check potencial checks
                            if bool:
                                if not self.in_check(piece, move):
                                    # append new move
                                    piece.add_move(move)
                            else:
                                # append new move
                                piece.add_move(move)
            
            # right en pessant
            if Square.in_range(col+1) and row == r:
                if self.squares[row][col+1].has_enemy_piece(piece.color):
                    p = self.squares[row][col+1].piece

                    if isinstance(p, Pawn):
                        if p.en_passant:

                            # create initial and final move squares
                            initial = Square(row, col)
                            final = Square(fr, col+1, p)

                            # create a new move
                            move = Move(initial, final)
                            
                            # check potencial checks
                            if bool:
                                if not self.in_check(piece, move):
                                    # append new move
                                    piece.add_move(move)
                            else:
                                # append new move
                                piece.add_move(move)


        def knight_moves():

            # 8 possible moves
            possible_moves = [
                (row-2, col+1),
                (row-1, col+2),
                (row+1, col+2),
                (row+2, col+1),
                (row+2, col-1),
                (row+1, col-2),
                (row-1, col-2),
                (row-2, col-1),
            ]

            for possible_move in possible_moves:
                possible_move_row, possible_move_col = possible_move

                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.color):

                        # create squares of the new move
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)

                        # create new move
                        move = Move(initial, final)
                        
                        # check potencial checks
                        if bool:
                            if not isinstance(final_piece, King) and not self.in_check(piece, move):
                                # append new move
                                piece.add_move(move)
                        else:
                            # append new move
                            piece.add_move(move)

        def straightline_moves(incrs):
            for incr in incrs:
                row_incr, col_incr = incr

                possible_move_row = row + row_incr
                possible_move_col = col + col_incr

                while True:
                    if Square.in_range(possible_move_row, possible_move_col):

                        # create squares of the possible new move
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)

                        # create a possible new move
                        move = Move(initial, final)

                        # empty = continue looping
                        if self.squares[possible_move_row][possible_move_col].isempty():

                            # check potencial checks
                            if bool:
                                if not self.in_check(piece, move):
                                    # append new move
                                    piece.add_move(move)
                            else:
                                # append new move
                                piece.add_move(move)

                        # has enemy piece = add move + break
                        elif self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):

                            # check potencial checks
                            if bool:
                                if not isinstance(final_piece, King) and not self.in_check(piece, move):
                                    # append new move
                                    piece.add_move(move)
                            else:
                                # append new move
                                piece.add_move(move)
                            break

                        # has team piece = break
                        elif self.squares[possible_move_row][possible_move_col].has_team_piece(piece.color):
                            break
                    
                    # not in range
                    else: break

                    # incrementing incrs
                    possible_move_row = possible_move_row + row_incr
                    possible_move_col = possible_move_col + col_incr

        def king_moves():
            adjs = [
                (row-1, col+0),  # up
                (row-1, col+1),  # up-right
                (row+0, col+1),  # right
                (row+1, col+1),  # down-right
                (row+1, col+0),  # down
                (row+1, col-1),  # down-left
                (row+0, col-1),  # left
                (row-1, col-1),  # up-left
            ]

            # normal moves
            for possible_move in adjs:
                possible_move_row, possible_move_col = possible_move

                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.color):

                        # create squares of the new move
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)

                        # create new move
                        move = Move(initial, final)

                        # check potencial checks
                        if bool:
                            if not isinstance(final_piece, King) and not self.in_check(piece, move):
                                # append new move
                                piece.add_move(move)
                        else:
                            # append new move
                            piece.add_move(move)

            # castling moves
            if bool and not piece.moved:
                # King must not be currently in check
                if not self.is_in_check(piece, None):
                    # queen castling
                    left_rook = self.squares[row][0].piece
                    if isinstance(left_rook, Rook) and not left_rook.moved:
                        # check if squares between king and rook are empty
                        empty = True
                        for c in range(1, 4):
                            if self.squares[row][c].has_piece():
                                empty = False
                                break
                        if empty:
                            # King passes through col 3 and lands on col 2
                            # Both must not be under attack
                            moveK_step = Move(Square(row, col), Square(row, 3))
                            moveK_final = Move(Square(row, col), Square(row, 2))
                            
                            if not self.in_check(piece, moveK_step) and not self.in_check(piece, moveK_final):
                                # append new move to king
                                piece.add_move(moveK_final)

                    # king castling
                    right_rook = self.squares[row][7].piece
                    if isinstance(right_rook, Rook) and not right_rook.moved:
                        # check if squares between king and rook are empty
                        empty = True
                        for c in range(5, 7):
                            if self.squares[row][c].has_piece():
                                empty = False
                                break
                        if empty:
                            # King passes through col 5 and lands on col 6
                            moveK_step = Move(Square(row, col), Square(row, 5))
                            moveK_final = Move(Square(row, col), Square(row, 6))
                            
                            if not self.in_check(piece, moveK_step) and not self.in_check(piece, moveK_final):
                                # append new move to king
                                piece.add_move(moveK_final)

        if isinstance(piece, Pawn): 
            pawn_moves()

        elif isinstance(piece, Knight): 
            knight_moves()

        elif isinstance(piece, Bishop): 
            straightline_moves([
                (-1, 1),    # up-right
                (-1, -1),   # up-left
                (1, 1),     # down-right
                (1, -1),    # down-left
            ])

        elif isinstance(piece, Rook): 
            straightline_moves([
                (-1, 0),    # up
                (0, 1),     # right
                (1, 0),     # down
                (0, -1),    # left
            ])

        elif isinstance(piece, Queen): 
            straightline_moves([
                (-1, 1),    # up-right
                (-1, -1),   # up-left
                (1, 1),     # down-right
                (1, -1),    # down-left
                (-1, 0),    # up
                (0, 1),     # right
                (1, 0),     # down
                (0, -1)     # left
            ])

        elif isinstance(piece, King): 
            king_moves()

    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

    def is_in_check(self, piece, move):
        """
        Check if the king is in check after making a move (or in current position if move is None)
        """
        temp_board = copy.deepcopy(self)
        if move is not None:
            temp_piece = copy.deepcopy(piece)
            temp_board.move(temp_piece, move, testing=True)
        
        for row in range(ROWS):
            for col in range(COLS):
                if temp_board.squares[row][col].has_enemy_piece(piece.color):
                    p = temp_board.squares[row][col].piece
                    temp_board.calc_moves(p, row, col, bool=False)
                    for m in p.moves:
                        attacked_piece = temp_board.squares[m.final.row][m.final.col].piece
                        if isinstance(attacked_piece, King) and attacked_piece.color == piece.color:
                            return True
        return False

    def is_checkmate(self, color):
        """
        Check if the current player is in checkmate
        """
        king = self.get_king(color)
        if not king or not self.is_in_check(king, None):
            return False
            
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.squares[row][col].piece
                if piece and piece.color == color:
                    self.calc_moves(piece, row, col, bool=True)
                    if len(piece.moves) > 0:
                        return False
        return True

    def is_stalemate(self, color):
        """
        Check if the current player is in stalemate (no legal moves and not in check)
        """
        king = self.get_king(color)
        if not king or self.is_in_check(king, None):
            return False
            
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.squares[row][col].piece
                if piece and piece.color == color:
                    self.calc_moves(piece, row, col, bool=True)
                    if len(piece.moves) > 0:
                        return False
        return True

    def get_king(self, color):
        """
        Get the king piece of the specified color
        """
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.squares[row][col].piece
                if piece and isinstance(piece, King) and piece.color == color:
                    return piece
        return None

    def _add_pieces(self, color):
        row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)

        # pawns
        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))

        # knights
        self.squares[row_other][1] = Square(row_other, 1, Knight(color))
        self.squares[row_other][6] = Square(row_other, 6, Knight(color))

        # bishops
        self.squares[row_other][2] = Square(row_other, 2, Bishop(color))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(color))

        # rooks
        self.squares[row_other][0] = Square(row_other, 0, Rook(color))
        self.squares[row_other][7] = Square(row_other, 7, Rook(color))

        # queen
        self.squares[row_other][3] = Square(row_other, 3, Queen(color))

        # king
        self.squares[row_other][4] = Square(row_other, 4, King(color))