# Chess-AI Class Diagram & Architecture Overview

This document describes the updated object-oriented architecture and class relationships for the **Chess-AI** application.

---

## 1. Class Diagram (Mermaid)

```mermaid
classDiagram
    class Main {
        +Surface screen
        +Game game
        +__init__()
        +open_menu()
        +show_promotion_dialog(color)
        +mainloop()
    }

    class StartMenu {
        +Surface screen
        +int width
        +int height
        +str selected_difficulty
        +str selected_color
        +str selected_time
        +__init__(screen, width, height)
        +draw_robot_icon(surface, x, y)
        +draw_color_icon(surface, type, x, y)
        +run() dict
        +get_config() dict
    }

    class Game {
        +str next_player
        +Square hovered_sqr
        +Board board
        +Dragger dragger
        +Config config
        +bool game_over
        +bool check
        +bool checkmate
        +bool stalemate
        +bool ai_mode
        +bool auto_mode
        +str ai_player
        +int ai_difficulty
        +float white_time
        +float black_time
        +float increment
        +__init__()
        +setup(config)
        +update_clock()
        +to_chess_board() chess.Board
        +show_bg(surface)
        +show_pieces(surface)
        +show_moves(surface)
        +show_last_move(surface)
        +show_hover(surface)
        +show_status_bar(surface)
        +next_turn()
        +set_hover(row, col)
        +change_theme()
        +play_sound(captured)
        +reset()
        +update_game_state()
    }

    class Board {
        +list squares
        +Move last_move
        +__init__()
        +_create()
        +_add_pieces(color)
        +move(piece, move, testing)
        +valid_move(piece, move) bool
        +check_promotion(piece, final, promo_name)
        +castling(initial, final) bool
        +set_true_en_passant(piece)
        +disable_all_en_passant()
        +calc_moves(piece, row, col, bool)
        +is_in_check(king, move) bool
        +is_checkmate(color) bool
        +is_stalemate(color) bool
    }

    class ChessAI {
        +int difficulty
        +Theme theme
        +dict piece_values
        +__init__(difficulty, theme)
        +set_difficulty(level)
        +set_theme(theme)
        +_get_stockfish_move(board, time_limit, elo) chess.Move
        +get_best_move(board, time_limit) chess.Move
        +minimax(board, depth, alpha, beta, maximizing) float
        +evaluate_board(board) float
    }

    class Square {
        +int row
        +int col
        +Piece piece
        +str alphacol
        +__init__(row, col, piece)
        +has_piece() bool
        +isempty() bool
        +has_team_piece(color) bool
        +has_enemy_piece(color) bool
        +isempty_or_enemy(color) bool
        +in_range(*args)$ bool
        +get_alphacol(col)$ str
    }

    class Piece {
        +str name
        +str color
        +float value
        +list moves
        +bool moved
        +str texture
        +Rect texture_rect
        +__init__(name, color, value, texture, texture_rect)
        +set_texture(size)
        +add_move(move)
        +clear_moves()
    }

    class Pawn {
        +int dir
        +bool en_passant
        +__init__(color)
    }

    class Knight {
        +__init__(color)
    }

    class Bishop {
        +__init__(color)
    }

    class Rook {
        +__init__(color)
    }

    class Queen {
        +__init__(color)
    }

    class King {
        +Square left_rook
        +Square right_rook
        +__init__(color)
    }

    class Move {
        +Square initial
        +Square final
        +str promo_piece
        +__init__(initial, final)
        +__eq__(other) bool
    }

    class Dragger {
        +Piece piece
        +bool dragging
        +int mouseX
        +int mouseY
        +int initial_row
        +int initial_col
        +__init__()
        +update_blit(surface)
        +update_mouse(pos)
        +save_initial(pos)
        +drag_piece(piece)
        +undrag_piece()
    }

    class Config {
        +list themes
        +int idx
        +Theme theme
        +Font font
        +Sound move_sound
        +Sound capture_sound
        +__init__()
        +change_theme()
        +_add_themes()
    }

    class Theme {
        +Color bg
        +Color moves
        +Color trace
        +Color highlight
        +__init__(bg_light, bg_dark, moves_light, moves_dark, trace_light, trace_dark)
    }

    class Color {
        +tuple light
        +tuple dark
        +__init__(light, dark)
    }

    class Sound {
        +str path
        +Sound sound
        +__init__(path)
        +play()
    }

    %% Inheritance Relationships
    Piece <|-- Pawn
    Piece <|-- Knight
    Piece <|-- Bishop
    Piece <|-- Rook
    Piece <|-- Queen
    Piece <|-- King

    %% Ownership & Composition Relationships
    Main *-- Game : manages
    Main *-- StartMenu : displays modal
    Game *-- Board : contains
    Game *-- Dragger : handles drag & drop
    Game *-- Config : manages themes & sounds
    Game ..> ChessAI : calculates moves
    Board *-- "64" Square : grid (8x8)
    Square o-- Piece : holds
    Piece o-- Move : calculates
    Move *-- "2" Square : initial & final
    Config *-- Theme : active theme
    Theme *-- Color : light & dark schemes
    Config *-- Sound : move & capture sounds
```

---

## 2. Architecture & Component Descriptions

| Component | Responsibility |
| :--- | :--- |
| **`Main`** | Application entry point and main Pygame loop executor. Coordinates between `StartMenu` and `Game`. |
| **`StartMenu`** | Dark setup modal UI. Configures AI difficulty, player color, and match time control. |
| **`Game`** | High-level match state controller. Handles turn switching, live countdown clocks, rendering, hover states, themes, and sound triggers. |
| **`Board`** | Core chess rulebook engine. Manages 8x8 grid of `Square` objects, valid move calculations, check/checkmate detection, castling, en passant, and promotions. |
| **`ChessAI`** | Dual-engine AI system. Supports 6 Elo rating levels ranging from Minimax lookahead (Levels 1–3) to Stockfish 17 UCI engine (Levels 4–6). |
| **`Square`** | Represents a single tile on the 8x8 grid with row, column, algebraic notation (`a1`-`h8`), and piece occupancy state. |
| **`Piece` & Subclasses** | Polymorphic piece representations (`Pawn`, `Knight`, `Bishop`, `Rook`, `Queen`, `King`) with values, textures, and move lists. |
| **`Move`** | Represents a move from an initial `Square` to a final `Square` with optional promotion piece designation. |
| **`Dragger`** | Manages interactive mouse drag-and-drop mechanics for pieces on screen. |
| **`Config`, `Theme`, `Color`** | Visual styling system supporting multiple board color palettes (Green, Brown, Blue, Gray). |
