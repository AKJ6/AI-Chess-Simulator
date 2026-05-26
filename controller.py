import chess
from PySide6.QtCore import QObject, Signal, QTimer
from state_manager import StateManager
from logger import Logger
from move_validator import MoveValidator
from game_rules import GameRules
from model_loader import ModelLoader
from utils.json_utils import board_to_json

class GameController(QObject):
    state_updated = Signal(object) # sends JSON board
    log_updated = Signal(str)
    game_over = Signal(str)

    def __init__(self, delay_ms=1000):
        super().__init__()
        self.board = chess.Board()
        self.state_manager = StateManager()
        self.logger = Logger()
        self.validator = MoveValidator(self.board)
        self.model_loader = ModelLoader("models/Qwen", "models/Gemma")
        
        self.delay_ms = delay_ms
        self.timer = QTimer()
        self.timer.timeout.connect(self.play_turn)
        
        self.is_playing = False
        self.move_count = 0

    def start_game(self):
        if not self.is_playing:
            self.is_playing = True
            self.timer.start(self.delay_ms)
            self.log_updated.emit("Game started.")

    def pause_game(self):
        self.is_playing = False
        self.timer.stop()
        self.log_updated.emit("Game paused.")

    def reset_game(self):
        self.pause_game()
        self.board.reset()
        self.move_count = 0
        self.logger.clear()
        self._update_state()
        self.log_updated.emit("Game reset.")

    def _update_state(self):
        json_board = board_to_json(self.board)
        self.state_manager.save_state(self.board)
        self.state_updated.emit(json_board)

    def play_turn(self):
        if not self.is_playing:
            return

        status = GameRules.get_game_state(self.board)
        if status != "ongoing":
            self._handle_game_over(status)
            return

        current_color = self.board.turn # True for White, False for Black
        color_str = "white" if current_color else "black"
        
        json_board = board_to_json(self.board)
        
        # Get move from model
        move_json = self.model_loader.generate_move(json_board, color_str, self.board)
        
        if move_json:
            success, result = self.validator.validate_and_apply(move_json, current_color)
            if success:
                move_obj = result
                is_capture = self.board.is_capture(move_obj)
                self.move_count += 1
                
                check_state = "check" if self.board.is_check() else "none"
                
                self.logger.log_move(
                    self.move_count, 
                    color_str, 
                    move_json, 
                    is_capture, 
                    check_state
                )
                
                self.log_updated.emit(f"Move {self.move_count}: {color_str} played {move_obj.uci()}")
                self._update_state()
            else:
                self.log_updated.emit(f"Error: {color_str} attempted illegal move {move_json}. {result}")
                self.pause_game()
        else:
            self.log_updated.emit(f"Error: {color_str} model returned no move.")
            self.pause_game()

    def _handle_game_over(self, status):
        self.pause_game()
        if status == "checkmate":
            winner = "Black" if self.board.turn == chess.WHITE else "White"
            msg = f"Checkmate! {winner} wins."
        elif status == "stalemate":
            winner, w_score, b_score = GameRules.resolve_stalemate(self.board)
            if winner == "draw":
                msg = f"Stalemate draw. Scores: W({w_score}) - B({b_score})"
            else:
                msg = f"Stalemate resolved by points. {winner.capitalize()} wins! W({w_score}) - B({b_score})"
        else:
            msg = f"Game over: {status}"
            
        self.log_updated.emit(msg)
        self.game_over.emit(msg)
