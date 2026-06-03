# AI vs AI Chess Simulator

A local desktop application where **two local LLMs play chess against each other automatically**. One model controls White, the other controls Black. Chess rules are enforced programmatically, the board state is persisted to JSON, every move is logged, and the game is rendered live in a PySide6 GUI.

This document is the final, authoritative description of what the project is, how it is built, how to run it, and where the implementation deviates from the original brief.

---

## 1. What it is

- **AI vs AI only.** There is no human player. The white model and the black model take turns, with a configurable delay between moves, until the game ends.
- **Local, offline inference.** Both players are quantized GGUF LLMs run on CPU via `llama-cpp-python`. No network calls during a game.
- **Rules engine = `python-chess`.** All legality checking, check/checkmate/stalemate detection, castling, en passant, and promotion are delegated to the battle-tested `python-chess` library. The library's `chess.Board` is the in-memory source of truth; the JSON file is a serialized mirror of it.
- **JSON is the persisted state.** The 8×8 board is written to `board_state.json` after every move, and the move history is appended to `history_log.json`.
- **Models never touch the board directly.** A model only *suggests* a move string. The move is parsed, validated, and only then applied. Illegal suggestions are rejected and the model is re-prompted.

---

## 2. Architecture

The codebase keeps game logic, AI, persistence, and UI decoupled. Data flows in one direction per turn:

```
        ┌──────────────┐
        │   main.py    │  starts QApplication, shows MainWindow
        └──────┬───────┘
               │
        ┌──────▼────────────────────────────────────────────┐
        │              ui/main_window.py                     │
        │  wires GUI <-> GameController via Qt signals       │
        └──────┬───────────────────────────┬─────────────────┘
               │ buttons (start/pause/reset)│ state_updated / log / game_over
        ┌──────▼───────────────────────────▼─────────────────┐
        │                 controller.py                       │
        │  QTimer-driven game loop, turn alternation,         │
        │  endgame detection, orchestration                   │
        └───┬─────────┬──────────┬──────────┬─────────┬───────┘
            │         │          │          │         │
   ┌────────▼──┐ ┌────▼─────┐ ┌──▼───────┐ ┌▼───────┐ ┌▼──────────┐
   │model_loader│ │move_     │ │game_rules│ │state_  │ │ logger.py │
   │  (LLMs)    │ │validator │ │(endgame, │ │manager │ │(history_  │
   │            │ │          │ │ scoring) │ │(JSON)  │ │ log.json) │
   └────────────┘ └──────────┘ └──────────┘ └────────┘ └───────────┘
```

### The turn loop (`controller.py::play_turn`)

1. A `QTimer` fires every `delay_ms` (default 1000 ms).
2. `GameRules.get_game_state(board)` checks for checkmate / stalemate / draw. If the game is over, `_handle_game_over` runs and the loop stops.
3. The board is serialized to JSON (`board_to_json`) and handed to the current color's model.
4. `model_loader.generate_move(...)` returns a move as `{"from": [r,c], "to": [r,c], "promotion"?: "q"}`.
5. `MoveValidator.validate_and_apply(...)` confirms the piece belongs to the side to move and that the move is legal, then pushes it onto the board.
6. On success: increment move count, detect capture/check, write `board_state.json`, append to `history_log.json`, emit signals so the GUI redraws.
7. On failure (illegal move or no move): the game is paused and the error is logged.

---

## 3. File-by-file reference

| File | Responsibility |
|------|----------------|
| `main.py` | Entry point. Creates the `QApplication` and `MainWindow`. |
| `controller.py` | `GameController(QObject)` — the orchestrator. Owns the `chess.Board`, the timer-based game loop, turn alternation, endgame handling, and the three Qt signals (`state_updated`, `log_updated`, `game_over`). |
| `model_loader.py` | `ModelLoader` — loads the two GGUF models via `llama_cpp.Llama`, builds the prompt (board JSON + list of legal UCI moves), parses the model's text reply with a regex, validates it, and retries with corrective feedback until a legal move is produced. |
| `move_validator.py` | `MoveValidator` — converts a JSON move to UCI, verifies ownership and legality, and applies it to the board. |
| `game_rules.py` | `GameRules` — endgame state detection and **stalemate-by-material-points** resolution using the project's custom piece values. |
| `state_manager.py` | `StateManager` — reads/writes `board_state.json`. |
| `logger.py` | `Logger` — appends per-move records to `history_log.json` and clears it on reset. |
| `model_downloader.py` | One-off helper to pull a GGUF model from Hugging Face Hub. |
| `generate_svgs.py` | One-off helper that generates the piece SVGs from Unicode chess glyphs into `assets/`. |
| `utils/constants.py` | `BOARD_SIZE`, `PIECE_VALUES`, `CHESS_PIECE_MAP`, `COLOR_MAP`. |
| `utils/json_utils.py` | `board_to_json` — converts a `chess.Board` into the 8×8 JSON matrix. |
| `utils/move_utils.py` | Coordinate conversions (`coords_to_square`, `square_to_coords`) and `json_move_to_uci`. |
| `ui/main_window.py` | `MainWindow` — assembles the board widget + control panel and connects all signals. |
| `ui/chess_board_widget.py` | `ChessBoardWidget` — an 8×8 grid of `QLabel`s that renders the JSON board and piece SVGs. |
| `ui/control_panel.py` | `ControlPanel` — Start/Pause/Reset buttons, model-name labels, and the scrolling game-history log box. |
| `ui/styles.qss` | Dark-theme Qt stylesheet. |
| `board_state.json` | Live 8×8 board snapshot (regenerated each move). |
| `history_log.json` | Append-only move log. |
| `models/` | The GGUF model weights (git-ignored). |
| `assets/white_pieces/`, `assets/black_pieces/` | Per-piece SVG icons. |

---

## 4. Data formats

### Board (`board_state.json`)
An 8×8 array, **row 0 = rank 8 (black's back rank)**, column 0 = file A. Each cell is `null` or a piece object:

```json
{ "type": "knight", "value": 4, "color": "black", "has_moved": false }
```

### Piece values (project-specific, from the brief)

| Piece | Value |
|-------|-------|
| Pawn | 1 |
| Knight | 4 |
| Bishop | 4.5 |
| Rook | 5 |
| Queen | 9 |
| King | 11 |

These values are used **only** for stalemate tie-breaking, not for the AI's own evaluation.

### Move format
Internally moves are passed as JSON and converted to/from UCI:

```json
{ "from": [6, 4], "to": [4, 4] }          // e2e4
{ "from": [1, 0], "to": [0, 0], "promotion": "q" }   // a7a8=Q
```

### History record (`history_log.json`)
```json
{
  "move_number": 1,
  "player": "white",
  "coords": { "from": [6, 4], "to": [4, 4] },
  "capture": false,
  "state": "none",
  "timestamp": "2026-05-29T10:51:44.729560"
}
```

---

## 5. How the AI produces a move

`ModelLoader.generate_move` does **constrained generation with retry**:

1. Build a prompt containing the board JSON **and the explicit list of every legal UCI move** for the position.
2. Ask the model to output exactly one 4–5 character move string.
3. Extract the move from the reply with the regex `\b[a-h][1-8][a-h][1-8][qrbn]?\b`.
4. Confirm it is in `board.legal_moves`.
5. If not, append the error plus the legal-move list to the prompt and try again.

Because the legal moves are given to the model, this is effectively a "pick from this list" task rather than open-ended chess reasoning, which keeps weak/small models playable.

---

## 6. Endgame handling

`GameRules.get_game_state` returns one of `"checkmate"`, `"stalemate"`, or `"ongoing"`.

- **Checkmate** → the side *not* to move wins.
- **Stalemate** (also insufficient material, 75-move rule, fivefold repetition) → resolved by **summing remaining piece values**; the higher total wins, equal totals are a draw. This is the project's custom rule — standard chess would score these as draws.

The result is shown in a popup (`QMessageBox`) and the loop halts until reset.

---

## 7. Running it

### Requirements
- Python 3 (the checked-in venv targets 3.14)
- `PySide6`, `chess`, `llama-cpp-python`, `huggingface_hub` (see `requirements.txt`)
- Two GGUF model files in `models/` — by default:
  - White: `models/Qwen3-8B-Q8_0.gguf`
  - Black: `models/gemma-4-E4B-it-Q8_0.gguf`

> ⚠️ Each Q8 model is ~8 GB. Running **both** simultaneously needs well over 16 GB of free RAM. Substitute smaller quantizations (e.g. Q4) or point both colors at one model to fit smaller machines. Model paths are currently hard-coded in `controller.py`.

### Install
```bash
python -m venv my
source my/bin/activate
pip install -r requirements.txt
```

### Get models (optional helper)
Edit `model_downloader.py` for the repo/filename you want, then:
```bash
python model_downloader.py
```

### Launch
```bash
python main.py
```
Then click **Start Game**. Use **Pause** to halt and **Reset** to start a fresh game.

---

## 8. Deviations from the original brief

These are intentional or pending differences between `instructions.txt` / `implementation_plan.md.txt` and the actual code:

1. **Rules engine.** Open question #3 in the plan (write chess from scratch vs. wrap a library) was resolved in favor of wrapping **`python-chess`**. The hand-written `move_validator.py` / `game_rules.py` are thin adapters over it.
2. **Real LLMs, not a mock.** Open question #1 was resolved in favor of running actual local GGUF models via `llama-cpp-python` (no random/mock AI fallback exists).
3. **`config.json` is not implemented.** Model paths and move delay are hard-coded in `controller.py`/`MainWindow` instead of read from a config file.
4. **`has_moved` is heuristic.** In `board_to_json` it is only inferred for pawns (off their start rank); for kings/rooks it is always `false`. It's informational for the UI/model and not used by the rules engine.
5. **Endgame limits not enforced.** The brief mentions an "illegal move limit" and "max move limit"; these are not implemented. Instead, an illegal/empty model response simply **pauses** the game.
6. **Check pauses the game.** When a move gives check, the loop logs it and pauses (`Check! ... Press Start to resume`) rather than continuing automatically.
7. **Effectively unbounded retries.** `max_retries` in `model_loader.py` is `10000`, so a stuck model can loop for a very long time before giving up.
8. **Minor dead imports.** `COLOR_MAP` / `json_move_to_uci` are imported but unused in `model_loader.py`.

