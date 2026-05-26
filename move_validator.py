import chess
from utils.move_utils import json_move_to_uci

class MoveValidator:
    def __init__(self, board: chess.Board):
        self.board = board

    def validate_and_apply(self, move_json, turn_color: chess.Color):
        """
        Validates if move_json is a legal move for the current board state and turn.
        If valid, it applies the move to self.board and returns True, None.
        If invalid, returns False, error_message.
        """
        try:
            uci_str = json_move_to_uci(move_json, self.board)
            move = chess.Move.from_uci(uci_str)
            
            # Check turn color
            piece = self.board.piece_at(move.from_square)
            if piece is None:
                return False, "No piece at the source square."
            if piece.color != turn_color:
                return False, "Cannot move opponent's piece."
                
            if move in self.board.legal_moves:
                self.board.push(move)
                return True, move
            else:
                return False, f"Illegal move: {uci_str}"
        except Exception as e:
            return False, f"Invalid move format: {str(e)}"
