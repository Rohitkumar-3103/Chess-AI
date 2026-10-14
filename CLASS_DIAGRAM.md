# Chess-AI Class Diagram & Architecture Overview

This document describes the object-oriented architecture, component relationships, and modernized UI design system for the **Chess-AI** application.

---

## 1. Class Diagram (Mermaid)

```mermaid
classDiagram
    class Main {
        +Surface screen
        +Game game
        +__init__()
        +open_menu(is_initial: bool)
        +show_promotion_dialog(color: str) str
        +mainloop()
    }

    class StartMenu {
        +Surface screen
        +int width
        +int height
        +Surface bg_surface
        +bool can_dismiss
        +str selected_difficulty
        +str selected_color
        +str selected_time
        +int modal_w
        +int modal_h
        +int modal_x
        +int modal_y
        +Font font_title
        +Font font_sub
        +Font font_sec
        +Font font_item
        +Font font_item_sub
        +Font font_badge
        +Font font_btn
        +Font font_hint
        +__init__(screen, width, height, bg_surface, can_dismiss)
        +draw_shadow(surface, rect, radius, blur)
        +draw_robot_icon(surface, center_x, center_y)
        +draw_color_icon(surface, color_type, center_x, center_y, radius)
        +draw_checkmark(surface, center_x, center_y, radius)
        +draw_card(surface, rect, is_selected, is_hover, border_radius)
        +draw_badge(surface, text, x, y, bg_col, txt_col)
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
        +str time_control_name
        +float white_time
        +float black_time
        +float increment
        +float last_tick
        +str timeout_winner
        +Piece selected_piece
        +int selected_row
        +int selected_col
        +dict reticle_surfaces
        +dict reticle_hover_surfaces
        +__init__()
        +setup(config: dict)
        +update_clock()
        +to_chess_board() chess.Board
        +show_bg(surface)
        +show_pieces(surface)
        +show_moves(surface)
        +show_last_move(surface)
        +show_check(surface)
        +show_hover(surface)
        +show_status_bar(surface)
        +show_game_over_banner(surface)
        +handle_mouse_motion(pos)
        +handle_button_click(pos) str
        +get_material_imbalance() int
        +format_time(seconds) str
        +next_turn()
        +set_hover(row, col)
        +select(piece, row, col)
        +deselect()
        +change_theme()
        +change_reticle_color()
        +play_sound(captured: bool)
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
        +dict reticle_colors
        +list reticle_color_names
        +int reticle_idx
        +str reticle_color_name
        +Font font
        +Sound move_sound
        +Sound capture_sound
        +__init__()
        +change_theme()
        +change_reticle_color()
        +_add_themes()
    }

    class Theme {
        +str name
        +Color bg
        +Color moves
        +Color trace
        +Color highlight
        +__init__(bg_light, bg_dark, moves_light, moves_dark, trace_light, trace_dark, name)
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

## 2. Interaction Sequence Diagram (Menu & Match Lifecycle)

```mermaid
sequenceDiagram
    autonumber
    actor Player
    participant Main
    participant StartMenu
    participant Game
    participant Board
    participant ChessAI

    Main->>Game: __init__() (instantiates board, config, dragger)
    Main->>Main: open_menu(is_initial=True)
    Main->>Game: render board & piece snapshot (bg_surface)
    Main->>StartMenu: __init__(screen, W, H, bg_surface, can_dismiss=False)
    Main->>StartMenu: run()
    
    rect rgb(35, 45, 30)
        Note over Player,StartMenu: Interactive Glassmorphic Modal Loop
        StartMenu->>StartMenu: render alpha backdrop + drop shadow
        Player->>StartMenu: Select Difficulty (Basic, Intermediate, Advanced)
        Player->>StartMenu: Select Play As (White, Random, Black)
        Player->>StartMenu: Select Time Control (Untimed to 15+10)
        Player->>StartMenu: Click "Start Game" or press [Enter]
    end

    StartMenu-->>Main: return config dict {difficulty, color, time_control}
    Main->>Game: reset()
    Main->>Game: setup(config)
    
    loop Match Execution (mainloop)
        Game->>Game: update_clock()
        Game->>Main: render board, pieces, status bar
        
        alt Player's Turn
            Player->>Game: Drag & drop piece
            Game->>Board: valid_move(piece, move)
            Game->>Board: move(piece, move)
            Game->>Game: play_sound()
            Game->>Game: next_turn()
        else AI's Turn
            Game->>ChessAI: get_best_move(chess_board, time_limit)
            ChessAI-->>Game: return best_move
            Game->>Board: move(ai_piece, ai_move)
            Game->>Game: play_sound()
            Game->>Game: next_turn()
        end
    end
```

---

## 3. Architecture & Component Descriptions

| Component | Responsibility |
| :--- | :--- |
| **`Main`** | Application entry point and primary Pygame loop manager. Orchestrates initial setup, in-game modal triggers (`M` key), pawn promotion modals, and turn dispatching. |
| **`StartMenu`** | Modern glassmorphic setup modal dialog. Renders a dimmed board backdrop, Gaussian drop shadow, tactile card grids with checkmarks/badges, and configuration summary pills. |
| **`Game`** | High-level match state controller. Manages turn alternations, chess clocks with increment, status bar displays, board themes, sound triggers, and win/draw evaluations. |
| **`Board`** | Core chess rulebook engine. Manages the 8x8 matrix of `Square` objects, valid move calculations, check/checkmate detection, castling, en passant, and promotions. |
| **`ChessAI`** | Dual-engine AI architecture. Blends Minimax search with Alpha-Beta pruning & piece-square tables (Levels 1–3) with the Stockfish 17 AVX2 UCI engine (Levels 4–6). |
| **`Square`** | Represents a single tile on the 8x8 grid with row, column, algebraic notation (`a1`–`h8`), and piece occupancy states. |
| **`Piece` & Subclasses** | Polymorphic piece representations (`Pawn`, `Knight`, `Bishop`, `Rook`, `Queen`, `King`) with values, textures, and move lists. |
| **`Move`** | Data structure representing an initial square, final square, and optional pawn promotion piece designation. |
| **`Dragger`** | Manages real-time mouse drag-and-drop interactions, tracking piece positions and visual offsets. |
| **`Config`, `Theme`, `Color`** | Visual styling subsystem supporting dynamic board color palettes (Green, Brown, Blue, Gray) and sound effects. |

---

## 4. UI Design System & Visual Specification

### Color Tokens

| Token | RGB / Hex | Usage |
| :--- | :--- | :--- |
| `c_overlay` | `(14, 13, 11, 215)` | Semi-transparent frosted backdrop over the chess board |
| `c_modal_bg` | `(28, 27, 24)` | Modal card surface background |
| `c_modal_border`| `(58, 54, 48)` | 2px smooth rounded modal card outline |
| `c_card_bg` | `(36, 34, 30)` | Default interactive card fill |
| `c_card_border`| `(54, 51, 45)` | Default card border |
| `c_card_hover` | `(46, 44, 38)` | Hover card fill |
| `c_card_sel_bg`| `(38, 54, 28)` | Selected card olive-emerald tint |
| `c_card_sel_border`| `(129, 182, 76)` | Selected card highlight border |
| `c_accent_green`| `(129, 182, 76)` | Primary action button and indicator accents |
| `c_accent_dark` | `(92, 138, 50)` | Tactile 3D bottom bevel on action buttons |

### Typography & Iconography Hierarchy

- **Title (`26px Bold`):** High-contrast Segoe UI / Arial header (`Play Against AI`).
- **Section Headers (`12px Bold`):** Uppercase category markers (`1. CHOOSE DIFFICULTY`, etc.).
- **Item Titles (`15px Bold`) & Subtitles (`11px`):** High-contrast active text with secondary descriptions.
- **Pill Badges (`10px Bold`):** Colored tags (`LVL 2`, `LVL 4`, `LVL 6`) indicating exact AI difficulty tiers.
- **Vector Icons:** Fully drawn vector icons (clean geometric robot badge, 3D color discs, checkmarks, play triangle, and vector `✕` close button) ensuring resolution independence across all platforms.
