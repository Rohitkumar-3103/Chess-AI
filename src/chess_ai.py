import chess
import random
from typing import Optional, Tuple
import time
from color import Color
from theme import Theme

class ChessAI:
    def __init__(self, difficulty: int = 3, theme: Optional[Theme] = None):
        """
        Initialize the Chess AI with a difficulty level and optional theme.
        
        Args:
            difficulty (int): Level of AI strength (1-6, 6 = Stockfish GM)
            theme (Optional[Theme]): Theme for visualization
        """
        self.difficulty = max(1, min(6, difficulty))
        self.theme = theme
        self.piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0  # King value handled separately in evaluation
        }
        
    def set_difficulty(self, level: int):
        """Set the AI difficulty level (1-6)"""
        self.difficulty = max(1, min(6, level))
    
    def set_theme(self, theme: Theme):
        """Set the visual theme for the AI"""
        self.theme = theme
        
    def _get_stockfish_move(self, board: chess.Board, time_limit: float = 0.5, elo: Optional[int] = None) -> Optional[chess.Move]:
        """Query Stockfish engine with optional UCI_Elo rating limit"""
        import os
        import chess.engine
        
        possible_paths = [
            os.path.join(os.path.dirname(__file__), 'stockfish.exe'),
            os.path.abspath('src/stockfish.exe'),
            'stockfish.exe',
            'stockfish'
        ]
        
        sf_path = None
        for p in possible_paths:
            if os.path.isfile(p):
                sf_path = p
                break
                
        if sf_path:
            try:
                engine = chess.engine.SimpleEngine.popen_uci(sf_path)
                if elo is not None:
                    # Stockfish UCI Elo range is 1320-3190
                    target_elo = max(1320, min(3190, elo))
                    engine.configure({"UCI_LimitStrength": True, "UCI_Elo": target_elo})
                result = engine.play(board, chess.engine.Limit(time=min(time_limit, 0.3)))
                engine.quit()
                return result.move
            except Exception as e:
                print(f"Stockfish engine error: {e}")
                return None
        return None
    
    def get_best_move(self, board: chess.Board, time_limit: float = 5.0) -> chess.Move:
        """
        Calculate the best move for the current board position based on selected Elo Level.
        Level 1: Beginner (Elo ~400) - Basic 1-ply + 50% blunders
        Level 2: Casual (Elo ~800) - 1-ply Minimax greedy
        Level 3: Intermediate (Elo ~1200) - 3-ply Minimax with positional evaluation
        Level 4: Advanced (Elo ~1600) - Stockfish @ 1600 ELO (Fallback: 4-ply Minimax)
        Level 5: Master (Elo ~2200) - Stockfish @ 2200 ELO (Fallback: 5-ply Minimax)
        Level 6: Superhuman GM (Elo 3000+) - Stockfish Full Power
        """
        start_time = time.time()
        legal_moves = list(board.legal_moves)
        
        # Early exit if only one move
        if len(legal_moves) == 1:
            return legal_moves[0]
            
        # Level 6: Superhuman GM (Elo 3000+) - Stockfish Full Unrestricted Power
        if self.difficulty == 6:
            sf_move = self._get_stockfish_move(board, time_limit, elo=None)
            if sf_move:
                return sf_move

        # Level 5: Master (Elo 2200) - Stockfish @ 2200 Elo
        elif self.difficulty == 5:
            sf_move = self._get_stockfish_move(board, time_limit, elo=2200)
            if sf_move:
                return sf_move

        # Level 4: Advanced (Elo 1600) - Stockfish @ 1600 Elo
        elif self.difficulty == 4:
            sf_move = self._get_stockfish_move(board, time_limit, elo=1600)
            if sf_move:
                return sf_move

        # Level 1: Beginner (Elo ~400) - 50% intentional blunders/random
        if self.difficulty == 1:
            if random.random() < 0.5:
                return random.choice(legal_moves)
            # Greedy 1-ply best move
            best_move = None
            best_value = -float('inf')
            for move in legal_moves:
                board.push(move)
                value = self.evaluate_board(board)
                board.pop()
                if value > best_value:
                    best_value = value
                    best_move = move
            return best_move or random.choice(legal_moves)

        # Level 2: Casual (Elo ~800) - 1-ply greedy
        if self.difficulty == 2:
            best_move = None
            best_value = -float('inf')
            for move in legal_moves:
                board.push(move)
                value = self.evaluate_board(board)
                board.pop()
                if value > best_value:
                    best_value = value
                    best_move = move
            return best_move or random.choice(legal_moves)
        
        # For Level 3 (Elo ~1200) or Minimax Fallbacks (Levels 4-6 if Stockfish binary missing)
        max_depth = self.difficulty + 1
        best_move = None
        best_value = -float('inf')
        alpha = -float('inf')
        beta = float('inf')
        
        # Iterative deepening
        for depth in range(1, max_depth + 1):
            if time.time() - start_time > time_limit:
                break
                
            current_best = None
            current_value = -float('inf')
            
            for move in legal_moves:
                board.push(move)
                value = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                
                if value > current_value:
                    current_value = value
                    current_best = move
                    
                alpha = max(alpha, value)
                
            if current_best is not None:
                best_move = current_best
                best_value = current_value
        
        return best_move or random.choice(legal_moves)
        for depth in range(1, max_depth + 1):
            if time.time() - start_time > time_limit:
                break
                
            current_best = None
            current_value = -float('inf')
            
            for move in legal_moves:
                board.push(move)
                value = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                
                if value > current_value:
                    current_value = value
                    current_best = move
                    
                # Update alpha for alpha-beta pruning
                alpha = max(alpha, value)
                
            # Only update if we completed the depth search
            if current_best is not None:
                best_move = current_best
                best_value = current_value
        
        return best_move or random.choice(legal_moves)
    
    def minimax(self, board: chess.Board, depth: int, alpha: float, beta: float, 
                maximizing_player: bool) -> float:
        """
        Minimax algorithm with alpha-beta pruning.
        
        Args:
            board: Current board state
            depth: Current search depth
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            maximizing_player: Whether current player is maximizing
            
        Returns:
            Evaluation score for the position
        """
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board)
        
        if maximizing_player:
            max_eval = -float('inf')
            for move in board.legal_moves:
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in board.legal_moves:
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval
    
    def evaluate_board(self, board: chess.Board) -> float:
        """
        Evaluate the current board position.
        
        Args:
            board: Current board state
            
        Returns:
            Evaluation score (positive favors white, negative favors black)
        """
        if board.is_checkmate():
            return -float('inf') if board.turn == chess.WHITE else float('inf')
        
        if board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves():
            return 0
        
        # Material evaluation
        material = 0
        for piece_type in self.piece_values:
            white_pieces = len(board.pieces(piece_type, chess.WHITE))
            black_pieces = len(board.pieces(piece_type, chess.BLACK))
            material += (white_pieces - black_pieces) * self.piece_values[piece_type]
        
        # Piece square tables for positional evaluation
        positional = self.evaluate_positional(board)
        
        # Mobility evaluation
        mobility = self.evaluate_mobility(board)
        
        # King safety evaluation
        king_safety = self.evaluate_king_safety(board)
        
        # Pawn structure evaluation
        pawn_structure = self.evaluate_pawn_structure(board)
        
        # Combine all factors with weights
        total = (
            material * 1.0 + 
            positional * 0.5 + 
            mobility * 0.1 + 
            king_safety * 0.3 + 
            pawn_structure * 0.2
        )
        
        return total
    
    def evaluate_positional(self, board: chess.Board) -> float:
        """Evaluate piece positions using piece-square tables"""
        # Simplified piece-square tables
        pawn_table = [
             0,  0,  0,  0,  0,  0,  0,  0,
             5, 10, 10,-20,-20, 10, 10,  5,
             5, -5,-10,  0,  0,-10, -5,  5,
             0,  0,  0, 20, 20,  0,  0,  0,
             5,  5, 10, 25, 25, 10,  5,  5,
            10, 10, 20, 30, 30, 20, 10, 10,
            50, 50, 50, 50, 50, 50, 50, 50,
             0,  0,  0,  0,  0,  0,  0,  0
        ]
        
        knight_table = [
            -50,-40,-30,-30,-30,-30,-40,-50,
            -40,-20,  0,  5,  5,  0,-20,-40,
            -30,  5, 10, 15, 15, 10,  5,-30,
            -30,  0, 15, 20, 20, 15,  0,-30,
            -30,  5, 15, 20, 20, 15,  5,-30,
            -30,  0, 10, 15, 15, 10,  0,-30,
            -40,-20,  0,  0,  0,  0,-20,-40,
            -50,-40,-30,-30,-30,-30,-40,-50
        ]
        
        bishop_table = [
            -20,-10,-10,-10,-10,-10,-10,-20,
            -10,  5,  0,  0,  0,  0,  5,-10,
            -10, 10, 10, 10, 10, 10, 10,-10,
            -10,  0, 10, 10, 10, 10,  0,-10,
            -10,  5,  5, 10, 10,  5,  5,-10,
            -10,  0,  5, 10, 10,  5,  0,-10,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -20,-10,-10,-10,-10,-10,-10,-20
        ]
        
        rook_table = [
              0,  0,  0,  5,  5,  0,  0,  0,
             -5,  0,  0,  0,  0,  0,  0, -5,
             -5,  0,  0,  0,  0,  0,  0, -5,
             -5,  0,  0,  0,  0,  0,  0, -5,
             -5,  0,  0,  0,  0,  0,  0, -5,
             -5,  0,  0,  0,  0,  0,  0, -5,
              5, 10, 10, 10, 10, 10, 10,  5,
              0,  0,  0,  0,  0,  0,  0,  0
        ]
        
        queen_table = [
            -20,-10,-10, -5, -5,-10,-10,-20,
            -10,  0,  5,  0,  0,  0,  0,-10,
            -10,  5,  5,  5,  5,  5,  0,-10,
              0,  0,  5,  5,  5,  5,  0, -5,
             -5,  0,  5,  5,  5,  5,  0, -5,
            -10,  0,  5,  5,  5,  5,  0,-10,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -20,-10,-10, -5, -5,-10,-10,-20
        ]
        
        king_middle_table = [
             20, 30, 10,  0,  0, 10, 30, 20,
             20, 20,  0,  0,  0,  0, 20, 20,
            -10,-20,-20,-20,-20,-20,-20,-10,
            -20,-30,-30,-40,-40,-30,-30,-20,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30
        ]
        
        king_end_table = [
            -50,-30,-30,-30,-30,-30,-30,-50,
            -30,-30,  0,  0,  0,  0,-30,-30,
            -30,-10, 20, 30, 30, 20,-10,-30,
            -30,-10, 30, 40, 40, 30,-10,-30,
            -30,-10, 30, 40, 40, 30,-10,-30,
            -30,-10, 20, 30, 30, 20,-10,-30,
            -30,-20,-10,  0,  0,-10,-20,-30,
            -50,-40,-30,-20,-20,-30,-40,-50
        ]
        
        # Check if it is endgame (both queens are gone, or one side has queen and <= 1 minor/major piece)
        has_white_queen = bool(board.pieces(chess.QUEEN, chess.WHITE))
        has_black_queen = bool(board.pieces(chess.QUEEN, chess.BLACK))
        
        white_minors_majors = len(board.pieces(chess.KNIGHT, chess.WHITE)) + \
                             len(board.pieces(chess.BISHOP, chess.WHITE)) + \
                             len(board.pieces(chess.ROOK, chess.WHITE))
                             
        black_minors_majors = len(board.pieces(chess.KNIGHT, chess.BLACK)) + \
                             len(board.pieces(chess.BISHOP, chess.BLACK)) + \
                             len(board.pieces(chess.ROOK, chess.BLACK))
                             
        is_endgame = False
        if not has_white_queen and not has_black_queen:
            is_endgame = True
        elif has_white_queen and white_minors_majors <= 1 and not has_black_queen:
            is_endgame = True
        elif has_black_queen and black_minors_majors <= 1 and not has_white_queen:
            is_endgame = True
        elif has_white_queen and white_minors_majors <= 1 and has_black_queen and black_minors_majors <= 1:
            is_endgame = True
        
        positional = 0
        
        # Evaluate piece positions using piece-square tables
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                table = None
                if piece.piece_type == chess.PAWN:
                    table = pawn_table
                elif piece.piece_type == chess.KNIGHT:
                    table = knight_table
                elif piece.piece_type == chess.BISHOP:
                    table = bishop_table
                elif piece.piece_type == chess.ROOK:
                    table = rook_table
                elif piece.piece_type == chess.QUEEN:
                    table = queen_table
                elif piece.piece_type == chess.KING:
                    table = king_end_table if is_endgame else king_middle_table
                
                if table:
                    # Flip square for black pieces
                    eval_square = square if piece.color == chess.WHITE else chess.square_mirror(square)
                    value = table[eval_square]
                    positional += value if piece.color == chess.WHITE else -value
        
        return positional / 100.0
    
    def evaluate_mobility(self, board: chess.Board) -> float:
        """Evaluate mobility (number of legal moves)"""
        if board.is_checkmate():
            return 0
            
        white_moves = len(list(board.legal_moves))
        board.push(chess.Move.null())  # Switch turn
        black_moves = len(list(board.legal_moves))
        board.pop()
        
        return white_moves - black_moves
    
    def evaluate_king_safety(self, board: chess.Board) -> float:
        """Evaluate king safety based on pawn shield and enemy attacks"""
        white_king = board.king(chess.WHITE)
        black_king = board.king(chess.BLACK)
        
        if white_king is None or black_king is None:
            return 0.0
            
        white_safety = 0
        black_safety = 0
        
        # Simple pawn shield evaluation
        # White king safety
        w_file = chess.square_file(white_king)
        w_rank = chess.square_rank(white_king)
        if w_rank < 7:
            for delta_file in [-1, 0, 1]:
                shield_file = w_file + delta_file
                if 0 <= shield_file < 8:
                    shield_square = chess.square(shield_file, w_rank + 1)
                    piece = board.piece_at(shield_square)
                    if piece and piece.piece_type == chess.PAWN and piece.color == chess.WHITE:
                        white_safety += 10
                        
        # Black king safety
        b_file = chess.square_file(black_king)
        b_rank = chess.square_rank(black_king)
        if b_rank > 0:
            for delta_file in [-1, 0, 1]:
                shield_file = b_file + delta_file
                if 0 <= shield_file < 8:
                    shield_square = chess.square(shield_file, b_rank - 1)
                    piece = board.piece_at(shield_square)
                    if piece and piece.piece_type == chess.PAWN and piece.color == chess.BLACK:
                        black_safety += 10
        
        return (white_safety - black_safety) / 100.0
    
    def evaluate_pawn_structure(self, board: chess.Board) -> float:
        """Evaluate pawn structure (doubled, isolated, passed pawns)"""
        white_pawns = board.pieces(chess.PAWN, chess.WHITE)
        black_pawns = board.pieces(chess.PAWN, chess.BLACK)
        
        white_score = 0
        black_score = 0
        
        # Check for doubled pawns
        white_files = set()
        black_files = set()
        
        for pawn in white_pawns:
            file = chess.square_file(pawn)
            if file in white_files:
                white_score -= 5  # Penalty for doubled pawns
            white_files.add(file)
            
        for pawn in black_pawns:
            file = chess.square_file(pawn)
            if file in black_files:
                black_score -= 5  # Penalty for doubled pawns
            black_files.add(file)
        
        # Check for isolated pawns
        for pawn in white_pawns:
            file = chess.square_file(pawn)
            if (file == 0 or (file - 1) not in white_files) and \
               (file == 7 or (file + 1) not in white_files):
                white_score -= 10  # Penalty for isolated pawn
                
        for pawn in black_pawns:
            file = chess.square_file(pawn)
            if (file == 0 or (file - 1) not in black_files) and \
               (file == 7 or (file + 1) not in black_files):
                black_score -= 10  # Penalty for isolated pawn
        
        return (white_score - black_score) / 100.0