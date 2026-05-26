import random
import json
import chess
from utils.move_utils import square_to_coords

class ModelLoader:
    def __init__(self, model_path_white=None, model_path_black=None):
        """
        Initializes the AI models. 
        For now, this is a placeholder where you can plug in your quantized LLM 
        using e.g., llama_cpp or transformers.
        """
        self.model_path_white = model_path_white
        self.model_path_black = model_path_black
        print(f"Initialized models. White: {model_path_white}, Black: {model_path_black}")

    def generate_move(self, board_state_json, current_turn_color_str, board_obj: chess.Board):
        """
        Generates a move given the current board state.
        board_obj is passed here to easily generate a valid mock move.
        In a real LLM, you would serialize the board_state_json into a prompt,
        ask the LLM for a move, parse its JSON response, and return it.
        """
        # --- MOCK IMPLEMENTATION ---
        # Selects a random legal move
        legal_moves = list(board_obj.legal_moves)
        if not legal_moves:
            return None
            
        move = random.choice(legal_moves)
        
        # Convert to our JSON format
        from_sq = move.from_square
        to_sq = move.to_square
        
        from_coords = square_to_coords(from_sq)
        to_coords = square_to_coords(to_sq)
        
        result = {
            "from": from_coords,
            "to": to_coords
        }
        
        if move.promotion:
            promo_map = {chess.QUEEN: 'q', chess.ROOK: 'r', chess.BISHOP: 'b', chess.KNIGHT: 'n'}
            result["promotion"] = promo_map.get(move.promotion, 'q')
            
        return result
