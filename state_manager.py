import json
import os
import chess
from utils.json_utils import board_to_json

class StateManager:
    def __init__(self, filepath="board_state.json"):
        self.filepath = filepath

    def save_state(self, board: chess.Board):
        json_board = board_to_json(board)
        with open(self.filepath, 'w') as f:
            json.dump(json_board, f, indent=2)

    def load_state(self):
        # We don't really load state into python-chess easily from our custom JSON,
        # but we can read it if needed. Usually, python-chess board is the source of truth,
        # and we sync it to JSON.
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r') as f:
                return json.load(f)
        return None
