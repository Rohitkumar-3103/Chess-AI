# ♟️ Chess-AI: Intelligent Chess Game with Pygame & Stockfish

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/pygame-2.5+-green.svg)](https://www.pygame.org/)
[![Engine](https://img.shields.io/badge/engine-Stockfish%2017%20AVX2-orange.svg)](https://stockfishchess.org/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)

An intelligent, object-oriented Chess application built with **Python**, **Pygame**, and **Stockfish 17**. Featuring an interactive GUI, customizable time controls, sound effects, board themes, and an AI opponent spanning **6 distinct difficulty levels** — from complete beginner to Grandmaster-tier Stockfish evaluation.

---

## 🌟 Key Features

### 🤖 6-Tier Adaptive AI Opponent
- **Level 1 — Beginner (~400 Elo):** 1-ply search with a 50% blunder rate for beginners.
- **Level 2 — Casual (~800 Elo):** 1-ply greedy evaluation capturing free pieces and avoiding immediate blunders.
- **Level 3 — Intermediate (~1200 Elo):** 3-ply Minimax search with Alpha-Beta pruning and positional piece-square evaluation tables.
- **Level 4 — Advanced (~1600 Elo):** Stockfish engine constrained to 1600 UCI Elo rating (Minimax 4-ply fallback).
- **Level 5 — Master (~2200 Elo):** Stockfish engine constrained to 2200 UCI Elo rating (Minimax 5-ply fallback).
- **Level 6 — Superhuman GM (3000+ Elo):** Full unconstrained Stockfish 17 analysis for grandmaster-level play.

### 🎨 Visual & Audio Experience
- **Modern Glassmorphic Start Menu:** Sleek dark-mode dialog with translucent board backdrop, tactile 3D cards, AI difficulty badges (LVL 2/4/6), side selectors, customizable time controls, and live selection summary pill.
- **Interactive In-Game Dashboard & HUD:** Real-time turn pill (`Your Turn`, `Thinking...`, `Finished`), material advantage indicator (`+N`), digital clocks, and a tactile toolbar featuring clickable buttons (`Menu`, `Reset`, `Mode`, `Theme`, `Level`) with custom vector graphics and keyboard shortcut tags.
- **Signature Move Indicators:** Semi-transparent dots for empty destination squares and circular target rings for captures, matching top modern platforms (Chess.com / Lichess).
- **Subtle Highlights & Check Danger Halo:** Soft translucent warm overlay for previous moves, hover feedback, lifted piece source square tint, and radial crimson danger glow on kings in check.
- **5 Curated Color Themes:** Dynamic live cycling between **Emerald**, **Walnut**, **Ocean**, **Slate**, and **Charcoal** with live split-color swatches in the toolbar.
- **Victory & Game Over Modal:** Celebration overlay card featuring outcome badge, result description, and 1-click Rematch (`R`) and Setup Menu (`M`) actions.
- **Pawn Promotion Modal:** Graphical floating glassmorphic dialog for Queen, Rook, Bishop, or Knight selection.
- **Custom Sound Effects:** High-quality audio feedback for legal moves and piece captures.

---

## 📐 Architecture & Class Design

The project is structured with clean Object-Oriented Principles (OOP). Full architectural specifications and high-resolution diagrams are provided:

- 📄 Detailed specification: [CLASS_DIAGRAM.md](CLASS_DIAGRAM.md)
- 🖼️ Complete UML Diagram (with Legend): [Chess-AI UML Class Diagram.png](Chess-AI%20UML%20Class%20Diagram.png)
- 🖼️ Blueprint Architecture Diagram: [Chess-AI Class Diagram.png](Chess-AI%20Class%20Diagram.png)

![Chess-AI UML Class Diagram](Chess-AI%20UML%20Class%20Diagram.png)

```
                    ┌─────────────┐
                    │    Main     │
                    └──────┬──────┘
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
       ┌───────────┐ ┌───────────┐ ┌───────────┐
       │ StartMenu │ │   Game    │ │  ChessAI  │
       └───────────┘ └─────┬─────┘ └───────────┘
                     ┌─────┴─────┐
                     ▼           ▼
               ┌───────────┐ ┌───────────┐
               │   Board   │ │  Config   │
               └─────┬─────┘ └───────────┘
               ┌─────┴─────┐
               ▼           ▼
         ┌───────────┐ ┌───────────┐
         │  Square   │ │   Piece   │
         └───────────┘ └───────────┘
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.10, 3.12, and 3.14)
- Git

### 2. Clone the Repository
```bash
git clone https://github.com/Rohitkumar-3103/Chess-AI.git
cd Chess-AI
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Game
On **Windows**, double-click:
```bat
run.bat
```

Or run via Python terminal:
```bash
python main.py
```
*(or `python src/main.py`)*

---

## 🎮 In-Game Controls & Hotkeys

| Key | Action |
|:---:|:---|
| **`T`** | Cycle Board Themes (Emerald → Walnut → Ocean → Slate → Charcoal) |
| **`C`** | Cycle Tactical Viewfinder Reticles (Blue → Green → White → Red) |
| **`R`** | Reset / Restart Game |
| **`A`** | Toggle Game Mode (Human vs AI → Auto-Play AI vs AI → PvP) |
| **`M`** | Open Glassmorphic Setup Menu |
| **`1` – `6`** | Switch AI Difficulty level on the fly |
| **Left Click** | Select piece (Click-to-Move) / Confirm destination |
| **Left Click + Drag** | Pick up and move piece (Drag-and-Drop) |
| **Release** | Drop piece onto target square |

---

## 📁 Project Structure

```
Chess-AI/
├── assets/
│   ├── images/
│   │   ├── imgs-80px/        # 80x80 chess piece sprites
│   │   ├── imgs-128px/       # 128x128 high-res piece sprites
│   │   └── reticles/         # Tactical corner reticle overlays (Blue, Green, White, Red)
│   └── sounds/
│       ├── move.wav          # Piece move audio
│       └── capture.wav       # Piece capture audio
├── src/
│   ├── board.py              # 8x8 Board state, move validation & check detection
│   ├── chess_ai.py           # Minimax algorithm & Stockfish UCI engine interface
│   ├── color.py              # Board color definition helper
│   ├── config.py             # Themes, reticle color palettes, sounds, and visual settings
│   ├── const.py              # Screen dimensions and board constants
│   ├── download_stockfish.py # Automated Stockfish 17 download script
│   ├── dragger.py            # Drag-and-drop & click piece interaction logic
│   ├── game.py               # Game state, clocks, reticle rendering, and HUD toolbar
│   ├── main.py               # Main Pygame event loop & interactive controls
│   ├── menu.py               # Glassmorphic setup menu modal & difficulty tiers
│   ├── move.py               # Move data structure
│   ├── piece.py              # Piece class hierarchy (Pawn, Knight, Bishop, Rook, Queen, King)
│   ├── sound.py              # Pygame audio player wrapper
│   ├── square.py             # Board square representation
│   ├── stockfish.exe         # Stockfish 17 AVX2 engine binary
│   └── theme.py              # Board theme color definitions
├── CLASS_DIAGRAM.md          # Architecture & UML class specifications
├── Chess-AI UML Class Diagram.png # Comprehensive UML diagram with Legend
├── Chess-AI Class Diagram.png # Blueprint architecture diagram
├── LICENSE                   # MIT License
├── main.py                   # Root launcher entry point
├── requirements.txt          # Python library dependencies
├── run.bat                   # 1-click Windows launcher
└── README.md                 # Project documentation
```

---

## ⚙️ Stockfish Engine Setup

`src/stockfish.exe` (Stockfish 17 AVX2 for Windows) is included in the repository. 

If running on macOS or Linux, or if you need to re-download the engine:
1. Run the built-in downloader:
   ```bash
   python src/download_stockfish.py
   ```
2. Or place your system's `stockfish` binary in the `src/` directory. If the executable is absent, the game automatically falls back to the integrated **Minimax Alpha-Beta** algorithm.

---

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).
