from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel
from PySide6.QtCore import Signal

class ControlPanel(QWidget):
    start_clicked = Signal()
    pause_clicked = Signal()
    reset_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Buttons
        self.btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Game")
        self.pause_btn = QPushButton("Pause Game")
        self.reset_btn = QPushButton("Reset Game")
        
        self.start_btn.clicked.connect(self.start_clicked.emit)
        self.pause_btn.clicked.connect(self.pause_clicked.emit)
        self.reset_btn.clicked.connect(self.reset_clicked.emit)
        
        self.btn_layout.addWidget(self.start_btn)
        self.btn_layout.addWidget(self.pause_btn)
        self.btn_layout.addWidget(self.reset_btn)
        
        self.layout.addLayout(self.btn_layout)
        
        # Log Box
        self.log_label = QLabel("Game History:")
        self.layout.addWidget(self.log_label)
        
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.layout.addWidget(self.log_box)

    def append_log(self, text):
        self.log_box.append(text)
        
    def clear_log(self):
        self.log_box.clear()
