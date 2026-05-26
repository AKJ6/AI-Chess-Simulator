import os
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtCore import Qt, QSize

class ChessBoardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid = QGridLayout(self)
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)
        
        self.squares = {} # (row, col) -> QLabel
        
        self._init_board()

    def _init_board(self):
        for row in range(8):
            for col in range(8):
                label = QLabel(self)
                label.setFixedSize(60, 60)
                label.setAlignment(Qt.AlignCenter)
                
                # Colors: light squares #f0d9b5, dark squares #b58863
                is_light = (row + col) % 2 == 0
                bg_color = "#f0d9b5" if is_light else "#b58863"
                label.setStyleSheet(f"background-color: {bg_color};")
                
                self.grid.addWidget(label, row, col)
                self.squares[(row, col)] = label

    def update_board(self, json_board):
        """
        Updates the board UI based on the 8x8 JSON array.
        """
        for row in range(8):
            for col in range(8):
                piece_obj = json_board[row][col]
                label = self.squares[(row, col)]
                
                if piece_obj:
                    color = piece_obj['color']
                    p_type = piece_obj['type']
                    
                    asset_path = os.path.join(
                        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        'assets',
                        f'{color}_pieces',
                        f'{p_type}.svg'
                    )
                    
                    if os.path.exists(asset_path):
                        pixmap = QPixmap(asset_path)
                        pixmap = pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        label.setPixmap(pixmap)
                    else:
                        label.clear()
                        label.setText(p_type[0].upper())
                else:
                    label.clear()
