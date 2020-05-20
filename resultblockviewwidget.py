from PySide2.QtWidgets import (QMainWindow, QWidget,
                               QVBoxLayout, QLabel)
from PySide2.QtCore import Qt


class ResultBlockViewWidget(QMainWindow):
    def __init__(self, block_name, result, parent=None):
        super(ResultBlockViewWidget, self).__init__(parent)
        self.setWindowTitle(f'Результаты выполнения блока \'{block_name}\'')
        self.setWindowModality(Qt.ApplicationModal)
        self.setMinimumWidth(640)
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setAlignment(Qt.AlignTop)
        self.setCentralWidget(self.central_widget)
        self.init_ui(result)

    def init_ui(self, result):
        for i in range(0, len(result)):
            result_label = QLabel(f'Команда №{i + 1}: \'{result[i][1].strip()}\'.')
            result_label.setAlignment(Qt.AlignCenter)
            if result[i][0] == 0:
                result_label.setStyleSheet('background-color: ForestGreen;')
            else:
                result_label.setStyleSheet('background-color: OrangeRed;')
            self.layout.addWidget(result_label)
