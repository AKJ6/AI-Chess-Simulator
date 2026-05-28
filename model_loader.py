import json
import chess
import re
from llama_cpp import Llama
from utils.move_utils import json_move_to_uci
from utils.constants import COLOR_MAP

class ModelLoader:
    def __init__(self, model_path_white=None, model_path_black=None):
        """
        Initializes the AI models using llama-cpp-python.
        """
        self.model_path_white = model_path_white
        self.model_path_black = model_path_black
        
        print(f"Loading White model from: {self.model_path_white}")
        self.model_white = Llama(model_path=self.model_path_white, n_ctx=2048, verbose=False) if self.model_path_white else None
        
        print(f"Loading Black model from: {self.model_path_black}")
        self.model_black = Llama(model_path=self.model_path_black, n_ctx=2048, verbose=False) if self.model_path_black else None
        
        print("Models initialized successfully.")

    def generate_move(self, board_state_json, current_turn_color_str, board_obj: chess.Board):
        """
        Generates a move using the LLMs with a retry loop for invalid moves.
        """
        model = self.model_white if current_turn_color_str == "white" else self.model_black
        if not model:
            print(f"Error: Model for {current_turn_color_str} not loaded.")
            return None

        base_prompt = (
            f"You are playing chess as {current_turn_color_str}. "
            "Below is the current board state in JSON format:\n"
            f"{json.dumps(board_state_json)}\n\n"
            f"Here are all the possible valid moves you can play:\n"
            f"{[move.uci() for move in board_obj.legal_moves]}\n\n"
            "Choose exactly ONE move from the list above.\n"
            "Output ONLY the 4-character or 5-character move string (for example: e2e4 or g8f6).\n"
            "Move:\n"
        )

        max_retries = 10000
        current_prompt = base_prompt

        for attempt in range(max_retries):
            print(f"[{current_turn_color_str}] Generating move... (Attempt {attempt + 1})")
            
            response = model(
                current_prompt,
                max_tokens=10,
                stop=["\n"],
                echo=False
            )
            
            output_text = response['choices'][0]['text'].strip()
            
            try:
                # Find the first sequence of word characters that might be a move
                match = re.search(r'\b[a-h][1-8][a-h][1-8][qrbn]?\b', output_text.lower())
                if match:
                    uci_str = match.group(0)
                else:
                    # Fallback to the whole text if regex didn't catch it
                    uci_str = output_text.lower().strip()
                
                # Verify if it's a valid legal move
                move = None
                try:
                    move = chess.Move.from_uci(uci_str)
                except ValueError:
                    raise ValueError(f"'{uci_str}' is not a valid chess move format.")
                    
                if move in board_obj.legal_moves:
                    print(f"[{current_turn_color_str}] Valid move generated: {uci_str}")
                    
                    # Convert to JSON format for the controller
                    from utils.move_utils import square_to_coords
                    from_coords = square_to_coords(move.from_square)
                    to_coords = square_to_coords(move.to_square)
                    
                    move_json = {"from": from_coords, "to": to_coords}
                    if move.promotion:
                        promo_map = {chess.QUEEN: 'q', chess.ROOK: 'r', chess.BISHOP: 'b', chess.KNIGHT: 'n'}
                        move_json["promotion"] = promo_map.get(move.promotion, 'q')
                        
                    return move_json
                else:
                    error_msg = f"'{uci_str}' is not in the list of valid moves."
            except Exception as e:
                error_msg = str(e)
            
            print(f"[{current_turn_color_str}] Attempt {attempt + 1} failed: {error_msg}. Retrying...")
            current_prompt += f"{output_text}\n\nInvalid move! Error: {error_msg}\nYou MUST pick a move exactly from this list: {[m.uci() for m in board_obj.legal_moves]}\nOutput ONLY the move string:\n"
            
        print(f"Error: {current_turn_color_str} failed to produce a valid move after {max_retries} retries.")
        return None
