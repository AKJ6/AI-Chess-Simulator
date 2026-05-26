import chess

def coords_to_square(r, c):
    """
    Convert matrix coords [row, col] to python-chess square index.
    row 0 is rank 8. col 0 is file A.
    """
    rank = 7 - r
    file = c
    return chess.square(file, rank)

def square_to_coords(square):
    """
    Convert python-chess square index to [row, col].
    """
    rank = chess.square_rank(square)
    file = chess.square_file(square)
    return [7 - rank, file]

def json_move_to_uci(json_move, board):
    """
    Convert JSON move {"from": [r, c], "to": [r, c]} to UCI string e.g. "e2e4".
    Handles promotion by defaulting to queen if pawn reaches end rank.
    """
    from_sq = coords_to_square(json_move['from'][0], json_move['from'][1])
    to_sq = coords_to_square(json_move['to'][0], json_move['to'][1])
    
    move = chess.Move(from_sq, to_sq)
    
    # Check for promotion
    piece = board.piece_at(from_sq)
    if piece and piece.piece_type == chess.PAWN:
        to_rank = chess.square_rank(to_sq)
        if to_rank == 0 or to_rank == 7:
            # Check if there is a 'promotion' field in json_move
            promotion_str = json_move.get('promotion', 'q').lower()
            promo_map = {'q': chess.QUEEN, 'r': chess.ROOK, 'b': chess.BISHOP, 'n': chess.KNIGHT}
            move.promotion = promo_map.get(promotion_str, chess.QUEEN)
            
    return move.uci()
