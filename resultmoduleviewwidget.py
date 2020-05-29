from PySide2.QtWidgets import (QMainWindow, QWidget,
                               QLabel, QVBoxLayout,
                               QPushButton, QScrollArea)
from PySide2.QtCore import Qt, Slot
from reportcreator import generate_report


class ResultModuleViewWidget(QMainWindow):
    def __init__(self, module_name, result, module_success, message, parent=None):
        super(ResultModuleViewWidget, self).__init__(parent)
        self.module_name = module_name
        self.module_success = module_success
        self.result = result
        self.message = message
        self.setWindowTitle(f'Результаты выполнения модуля \'{module_name}\'')
        self.setWindowModality(Qt.ApplicationModal)
        self.setMinimumWidth(640)
        self.central_widget = QWidget()
        self.scroll = QScrollArea()
        self.layout = QVBoxLayout(self.central_widget)
        self.init_ui(result, module_success)

    def init_ui(self, result, module_success):
        self.layout.addWidget(self.scroll)
        self.layout.setAlignment(Qt.AlignTop)
        self.setCentralWidget(self.central_widget)
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
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
            main_layout.addWidget(block_widget)
        module_result_label = QLabel()
        if module_success == 'True':
            module_result_label.setText('Модуль выполнился успешно.')
            module_result_label.setStyleSheet('color: ForestGreen; font-weight: bold;')
        elif module_success == 'False':
            module_result_label.setText('Модуль завершился неудачно.')
            module_result_label.setStyleSheet('color: Red; font-weight: bold;')
        elif module_success == 'Error':
            module_result_label.setText('В проверочном выражении ошибка.')
            module_result_label.setStyleSheet('color: OrangeRed; font-weight: bold;')
        module_result_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(module_result_label)
        button = QPushButton('Сгенерировать отчёт')
        button.clicked.connect(self.start_report_generation)
        main_layout.addWidget(button)
        self.scroll.setAlignment(Qt.AlignCenter)
        self.scroll.setWidget(widget)

    @Slot()
    def start_report_generation(self):
        generate_report(self.module_name, self.module_success, self.result, self.message, self)
