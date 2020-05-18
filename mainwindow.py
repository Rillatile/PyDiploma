from PySide2.QtWidgets import (QMainWindow, QMessageBox,
                               QLabel, QVBoxLayout,
                               QWidget, QFileDialog,
                               QComboBox, QScrollArea)
from PySide2.QtCore import Slot, QSysInfo, Qt, QDir
from parser import parse
from modulecontent import ModuleContent


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('ВКР')
        self.setMinimumSize(800, 600)
        self.central_widget = QWidget(self)
        self.layout = QVBoxLayout()
        self.modules_cb = QComboBox()
        self.modules_cb.currentIndexChanged.connect(self.set_module)
        self.scroll = QScrollArea()
        self.modules = []
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
        system_name = QLabel(f'Операционная система: {QSysInfo.prettyProductName()}', self.central_widget)
        system_name.setMaximumHeight(self.central_widget.height() * 0.7)
        system_name.setAlignment(Qt.AlignRight)
        self.layout.addWidget(system_name)
        self.layout.addWidget(self.modules_cb)
        self.layout.addWidget(self.scroll)
        if self.scroll.widget() is None:
            self.modules_cb.setVisible(False)
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)
        self.scroll.setAlignment(Qt.AlignCenter)

    @Slot(int)
    def set_module(self, index):
        self.show_module(self.modules[index])

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
                self.check_module(module_full_name, module_short_name)

    def check_module(self, module_full_name, module_short_name):
        for m in self.modules:
            if m['full_name'] == module_full_name:
                mb = QMessageBox(self)
                mb.setWindowTitle('Ошибка')
                mb.setText(f"Модуль '{module_short_name}' уже добавлен.")
                mb.show()
                return
        try:
            with open(module_full_name, 'r', encoding='utf-8') as module_file:
                content = module_file.read()
            parsed_data = parse(content)
        except IOError:
            mb = QMessageBox(self)
            mb.setWindowTitle('Ошибка')
            mb.setText('При открытии файла модуля возникла ошибка.')
            mb.show()
        except (SyntaxError, RuntimeError) as error:
            mb = QMessageBox(self)
            mb.setWindowTitle('Ошибка')
            mb.setText(str(error))
            mb.show()
        else:
            self.modules.append({
                'full_name': module_full_name,
                'short_name': module_short_name
            })
            self.modules_cb.setVisible(True)
            self.modules_cb.addItem(module_short_name)
            mb = QMessageBox(self)
            mb.setWindowTitle('Успешно')
            mb.setText('Модуль успешно добавлен.')
            mb.show()

    def show_module(self, module):
        try:
            with open(module['full_name'], 'r', encoding='utf-8') as module_file:
                content = module_file.read()
            parsed_data = parse(content)
            parsed_data['module_name'] = module['short_name']
            mc = ModuleContent(parsed_data, self.scroll)
            self.scroll.setWidget(mc)
        except IOError:
            mb = QMessageBox(self)
            mb.setWindowTitle('Ошибка')
            mb.setText('При открытии файла модуля возникла ошибка.')
            mb.show()
        except (SyntaxError, RuntimeError) as error:
            mb = QMessageBox(self)
            mb.setWindowTitle('Ошибка')
            mb.setText(str(error))
            mb.show()
