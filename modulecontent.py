from PySide2.QtWidgets import (QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel,
                               QLineEdit, QComboBox,
                               QStackedWidget, QTabWidget,
                               QPushButton)
from PySide2.QtCore import Qt, Slot, QSize
from executor import execute


class ModuleContent(QWidget):
    def __init__(self, data, parent=None):
        super(ModuleContent, self).__init__(parent)
        self.setMinimumSize(parent.size() - QSize(100, 100))
        self.layout = QVBoxLayout(self)
        self.variables = []
        self.current_block_number = 0
        self.data = data
        self.init_ui(data)

    def init_ui(self, data):
        if len(data['variables']) > 0:
            self.init_variables_ui(data)
        if len(data['constants']) > 0:
            self.init_constants_ui(data)
        if len(data['blocks']) > 0:
            self.init_blocks_ui(data)

    def init_variables_ui(self, data):
        variables_label = QLabel('Переменные:', self)
        variables_label.setAlignment(Qt.AlignCenter)
        variables_label.setStyleSheet('font-weight: bold;')
        self.layout.addWidget(variables_label)
        for variable in data['variables']:
            if variable['is_entered']:
                variables_widget = QWidget()
                h_layout = QHBoxLayout()
                name_label = QLabel(variable['name'])
                name_label.setAlignment(Qt.AlignCenter)
                name_label.setStyleSheet('font-weight: bold;')
                h_layout.addWidget(name_label)
                value_input = QLineEdit(variable['value'])
                self.variables.append(value_input)
                h_layout.addWidget(value_input)
                variables_widget.setLayout(h_layout)
                self.layout.addWidget(variables_widget)
                description_label = QLabel(variable['description'])
                description_label.setAlignment(Qt.AlignCenter)
                description_label.setStyleSheet('font-style: italic;')
                self.layout.addWidget(description_label)
            else:
                self.variables.append(None)

    def init_constants_ui(self, data):
        constants_label = QLabel('Константы:', self)
        constants_label.setAlignment(Qt.AlignCenter)
        constants_label.setStyleSheet('font-weight: bold;')
        self.layout.addWidget(constants_label)
        for constant in data['constants']:
            constants_widget = QWidget()
            h_layout = QHBoxLayout()
            name_label = QLabel(constant['name'])
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setStyleSheet('font-weight: bold;')
            h_layout.addWidget(name_label)
            value_label = QLabel(constant['value'])
            value_label.setAlignment(Qt.AlignCenter)
            h_layout.addWidget(value_label)
            constants_widget.setLayout(h_layout)
            self.layout.addWidget(constants_widget)
            description_label = QLabel(constant['description'])
            description_label.setAlignment(Qt.AlignCenter)
            description_label.setStyleSheet('font-style: italic;')
            self.layout.addWidget(description_label)

    def init_blocks_ui(self, data):
        blocks_label = QLabel('Блоки:', self)
        blocks_label.setAlignment(Qt.AlignCenter)
        blocks_label.setStyleSheet('font-weight: bold;')
        self.layout.addWidget(blocks_label)
        cb = QComboBox()
        blocks_stacked = QStackedWidget()
        cb.activated.connect(blocks_stacked.setCurrentIndex)
        cb.activated.connect(self.update_current_block_number)
        for block in data['blocks']:
            cb.addItem(block['name'])
            tab_widget = QTabWidget()
            description_label = QLabel(block['description'])
            description_label.setAlignment(Qt.AlignCenter)
            description_label.setStyleSheet('font-style: italic;')
            tab_widget.addTab(description_label, 'Описание')
            commands_label = QLabel('')
            commands_label.setAlignment(Qt.AlignCenter)
            for command in block['commands']:
                c = command['command']
                if command['result_variable'] != '':
                    c = command['result_variable'] + ' = ' + c
                commands_label.setText(commands_label.text() + '\n' + c)
            commands_label.setText(commands_label.text() + '\n')
            commands_label.setAlignment(Qt.AlignCenter)
            tab_widget.addTab(commands_label, 'Команды')
            blocks_stacked.addWidget(tab_widget)
        self.layout.addWidget(cb)
        self.layout.addWidget(blocks_stacked)
        button = QPushButton('Выполнить блок')
        button.clicked.connect(self.start_execute)
        self.layout.addWidget(button)

    @Slot(int)
    def update_current_block_number(self, number):
        self.current_block_number = number

    @Slot()
    def start_execute(self):
        for i in range(0, len(self.variables)):
            if self.variables[i] is not None:
                self.data['variables'][i]['value'] = self.variables[i].text()
        result = execute(self.data, self.current_block_number, self)
