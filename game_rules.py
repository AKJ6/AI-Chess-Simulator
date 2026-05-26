import chess
from utils.constants import CHESS_PIECE_MAP, PIECE_VALUES

class GameRules:
    @staticmethod
    def get_game_state(board: chess.Board):
        if board.is_checkmate():
            return "checkmate"
        if board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves() or board.is_fivefold_repetition():
            return "stalemate"
        if board.is_check():
            return "check"
        return "ongoing"

    @staticmethod
    def calculate_score(board: chess.Board, color: chess.Color):
        """
        Calculates the material score for a given color.
        """
        score = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.color == color:
                piece_name = CHESS_PIECE_MAP[piece.piece_type]
                score += PIECE_VALUES[piece_name]
        return score

    @staticmethod
    def resolve_stalemate(board: chess.Board):
        """
        Resolves a stalemate by comparing remaining piece values.
        Returns the winning color string ('white' or 'black'), or 'draw' if equal.
        """
        white_score = GameRules.calculate_score(board, chess.WHITE)
        black_score = GameRules.calculate_score(board, chess.BLACK)
        
        if white_score > black_score:
            return "white", white_score, black_score
        elif black_score > white_score:
            return "black", white_score, black_score
        else:
            return "draw", white_score, black_score
