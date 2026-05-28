import os
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QMessageBox
from ui.chess_board_widget import ChessBoardWidget
from ui.control_panel import ControlPanel
from controller import GameController

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI vs AI Chess Simulator")
        self.resize(1000, 600)
        
        self.controller = GameController(delay_ms=1000)
        
        self._init_ui()
        self._load_styles()
        self._connect_signals()
        
        # Initial state push
        self.controller._update_state()

    def _init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        
        from PySide6.QtCore import Qt
        
        self.board_widget = ChessBoardWidget(self)
        self.board_widget.setFixedSize(480, 480)
        
        board_container = QWidget(self)
        board_layout = QHBoxLayout(board_container)
        board_layout.addWidget(self.board_widget)
        board_layout.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(board_container, stretch=2)
        
        self.control_panel = ControlPanel(self)
        layout.addWidget(self.control_panel, stretch=1)
        
        white_path = os.path.basename(self.controller.model_loader.model_path_white) if self.controller.model_loader.model_path_white else "None"
        black_path = os.path.basename(self.controller.model_loader.model_path_black) if self.controller.model_loader.model_path_black else "None"
        self.control_panel.set_model_names(white_path, black_path)

    def _load_styles(self):
        style_path = os.path.join(os.path.dirname(__file__), 'styles.qss')
        if os.path.exists(style_path):
            with open(style_path, 'r') as f:
                self.setStyleSheet(f.read())

    def _connect_signals(self):
        # Controller signals
        self.controller.state_updated.connect(self.board_widget.update_board)
        self.controller.log_updated.connect(self.control_panel.append_log)
        self.controller.game_over.connect(self.show_game_over_popup)
        
        # UI signals
        self.control_panel.start_clicked.connect(self.controller.start_game)
        self.control_panel.pause_clicked.connect(self.controller.pause_game)
        self.control_panel.reset_clicked.connect(self.handle_reset)

    def handle_reset(self):
        self.control_panel.clear_log()
        self.controller.reset_game()

    def show_game_over_popup(self, msg):
        QMessageBox.information(self, "Game Over", msg)
