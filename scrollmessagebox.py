from PySide2.QtWidgets import (QMainWindow, QLabel,
                               QVBoxLayout, QScrollArea,
                               QWidget)


class ScrollMessageBox(QMainWindow):
    def __init__(self, title: str = 'Сообщение', text: str = '', parent=None):
        super(ScrollMessageBox, self).__init__(parent)
        self.setWindowTitle(title)
        self.central_widget = QWidget()
        layout = QVBoxLayout(self.central_widget)
        self.scroll = QScrollArea()
        label = QLabel(text=text)
        label.setContentsMargins(5, 5, 5, 5)
        label.setWordWrap(True)
        self.scroll.setWidget(label)
        layout.addWidget(self.scroll)
        self.central_widget.setMinimumWidth(self.central_widget.width() + 115)
        self.setCentralWidget(self.central_widget)
