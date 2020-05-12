from PySide2.QtWidgets import (QMainWindow, QMessageBox, QLabel,
                               QVBoxLayout, QWidget, QFileDialog)
from PySide2.QtCore import Slot, QSysInfo, Qt, QDir
from parser import parse


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('ВКР')
        self.setMinimumSize(480, 360)
        self.init_ui()

    def init_ui(self):
        file_menu = self.menuBar().addMenu('Файл')
        help_menu = self.menuBar().addMenu('Помощь')
        add_module_action = file_menu.addAction('Добавить существующий модуль')
        add_module_action.triggered.connect(self.add_module)
        close_action = file_menu.addAction('Закрыть программу')
        close_action.triggered.connect(self.close_program)
        about_action = help_menu.addAction('О программе')
        about_action.triggered.connect(self.show_about)
        central_widget = QWidget(self)
        layout = QVBoxLayout()
        system_name = QLabel(f'Операционная система: { QSysInfo.prettyProductName() }', central_widget)
        system_name.setAlignment(Qt.AlignRight)
        layout.addWidget(system_name)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    @Slot()
    def show_about(self):
        mb = QMessageBox(self)
        mb.setWindowTitle('О программе')
        mb.setText('Здесь будет краткое описание программы.')
        mb.show()

    @Slot()
    def close_program(self):
        self.close()

    @Slot()
    def add_module(self):
        module_full_name = QFileDialog.getOpenFileName(self, 'Выберите модуль', QDir.homePath(), '*.module')[0]
        if module_full_name != '':
            idx = module_full_name.rfind('/')
            if idx != -1:
                module_short_name = module_full_name[idx + 1:]
                # Дописать отображение и убрать исполнение
                self.execute_module(module_full_name)

    def execute_module(self, module_full_name):
        try:
            with open(module_full_name, 'r', encoding='utf-8') as module:
                content = module.read()
            parsed_data = parse(content)
            a = 'a'
        except IOError as error:
            mb = QMessageBox(self)
            mb.setWindowTitle('Ошибка')
            mb.setText('При открытии файла модуля возникла ошибка.')
            mb.show()
        except SyntaxError as error:
            mb = QMessageBox(self)
            mb.setWindowTitle('Ошибка')
            mb.setText(error.__str__())
            mb.show()
        except RuntimeError as error:
            mb = QMessageBox(self)
            mb.setWindowTitle('Ошибка')
            mb.setText(error.__str__())
            mb.show()
        else:
            mb = QMessageBox(self)
            mb.setWindowTitle('Успешно')
            mb.setText('Модуль успешно добавлен.')
            mb.show()
