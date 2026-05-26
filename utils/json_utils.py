import chess
from .constants import CHESS_PIECE_MAP, COLOR_MAP, PIECE_VALUES

def board_to_json(board: chess.Board):
    """
    Convert python-chess board to 8x8 JSON format as required.
    """
    json_board = []
    for row in range(8):
        rank = 7 - row
        row_arr = []
        for col in range(8):
            file = col
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            
            if piece is None:
                row_arr.append(None)
            else:
                piece_type_str = CHESS_PIECE_MAP[piece.piece_type]
                color_str = COLOR_MAP[piece.color]
                # has_moved might not be perfectly accurate just from piece_at, 
                # but we can infer for pawns and kings/rooks based on starting positions if needed.
                # However, python-chess handles all that internally, so this json is mostly for UI and Models.
                
                # Check has_moved heuristically for basic pieces
                has_moved = False
                if piece.piece_type == chess.PAWN:
                    if (piece.color == chess.WHITE and rank != 1) or \
                       (piece.color == chess.BLACK and rank != 6):
                        has_moved = True
                
                piece_obj = {
                    "type": piece_type_str,
                    "value": PIECE_VALUES[piece_type_str],
                    "color": color_str,
                    "has_moved": has_moved
                }
                row_arr.append(piece_obj)
        json_board.append(row_arr)
    return json_board
