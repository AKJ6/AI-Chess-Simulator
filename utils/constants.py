# utils/constants.py

BOARD_SIZE = 8

PIECE_VALUES = {
    'pawn': 1,
    'knight': 4,
    'bishop': 4.5,
    'rook': 5,
    'queen': 9,
    'king': 11
}

# Mapping python-chess piece types to our JSON names
CHESS_PIECE_MAP = {
    1: 'pawn',
    2: 'knight',
    3: 'bishop',
    4: 'rook',
    5: 'queen',
    6: 'king'
}

# Mapping python-chess colors to strings
COLOR_MAP = {
    True: 'white',
    False: 'black'
}
