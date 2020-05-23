from PySide2.QtWidgets import (QMainWindow, QWidget,
                               QLabel, QVBoxLayout)
from PySide2.QtCore import Qt


class ResultModuleViewWidget(QMainWindow):
    def __init__(self, module_name, result, module_success, parent=None):
        super(ResultModuleViewWidget, self).__init__(parent)
        self.setWindowTitle(f'Результаты выполнения модуля \'{module_name}\'')
        self.setWindowModality(Qt.ApplicationModal)
        self.setMinimumWidth(640)
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setAlignment(Qt.AlignTop)
        self.setCentralWidget(self.central_widget)
        self.init_ui(result)

    def init_ui(self, result):
        for i in range(0, len(result)):
            block_widget = QWidget()
            layout = QVBoxLayout(block_widget)
            block_name_label = QLabel(result[i][-1])
            block_name_label.setAlignment(Qt.AlignCenter)
            block_name_label.setStyleSheet('font-weight: bold;')
            layout.addWidget(block_name_label)
            for j in range(0, len(result[i]) - 1):
                command_result_label = QLabel(f'Команда №{j + 1}: \'{result[i][j][1].strip()}\'.')
                command_result_label.setAlignment(Qt.AlignCenter)
                if result[i][j][0] == 0:
                    command_result_label.setStyleSheet('background-color: ForestGreen;')
                else:
                    command_result_label.setStyleSheet('background-color: OrangeRed;')
                layout.addWidget(command_result_label)
            self.layout.addWidget(block_widget)
