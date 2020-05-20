from PySide2.QtWidgets import (QMainWindow, QMessageBox,
                               QLabel, QVBoxLayout,
                               QWidget, QFileDialog,
                               QComboBox, QScrollArea,
                               QHBoxLayout, QPushButton,
                               QInputDialog, QLineEdit)
from PySide2.QtCore import Slot, QSysInfo, Qt, QDir
from parser import parse
from modulecontentwidget import ModuleContentWidget
from createmodulewidget import CreateModuleWidget
from cryptography import aes_decrypt, xor_str
from hashlib import md5
from editmodulewidget import EditModuleWidget


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('ВКР')
        self.setMinimumSize(800, 600)
        self.central_widget = QWidget(self)
        self.layout = QVBoxLayout(self.central_widget)
        self.modules_cb = QComboBox()
        self.modules_cb.currentIndexChanged.connect(self.set_module)
        self.buttons_widget = QWidget()
        self.scroll = QScrollArea()
        self.modules = []
        self.init_ui()

    def init_ui(self):
        file_menu = self.menuBar().addMenu('Файл')
        help_menu = self.menuBar().addMenu('Помощь')
        create_module_action = file_menu.addAction('Создать новый модуль')
        create_module_action.triggered.connect(self.create_module)
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
        bw_layout = QHBoxLayout(self.buttons_widget)
        edit_button = QPushButton('Редактировать модуль')
        edit_button.clicked.connect(self.edit_module)
        bw_layout.addWidget(edit_button)
        delete_button = QPushButton('Удалить модуль')
        delete_button.clicked.connect(self.delete_module)
        bw_layout.addWidget(delete_button)
        self.layout.addWidget(self.buttons_widget)
        self.layout.addWidget(self.scroll)
        if self.scroll.widget() is None:
            self.modules_cb.setVisible(False)
            self.buttons_widget.setVisible(False)
        self.setCentralWidget(self.central_widget)
        self.scroll.setAlignment(Qt.AlignCenter)

    @Slot()
    def create_module(self):
        cmw = CreateModuleWidget(self)
        cmw.module_created.connect(self.add_created_module)
        cmw.show()

    @Slot(str)
    def add_created_module(self, module_full_name):
        if module_full_name != '':
            idx = module_full_name.rfind('/')
            if idx != -1:
                module_short_name = module_full_name[idx + 1:]
                self.check_module(module_full_name, module_short_name)

    @Slot(int)
    def update_edited_module(self, idx):
        self.show_module(self.modules[idx])

    @Slot()
    def edit_module(self):
        password, ok = QInputDialog().getText(self, 'Ввод пароля',
                                              'Введите пароль для редактирования модуля:', QLineEdit.Password)
        if ok:
            module = self.modules[self.modules_cb.currentIndex()]
            try:
                with open(module['full_name'], 'rb') as module_file:
                    crypto_type = module_file.read(3)
                    password_hash = module_file.read(md5().digest_size)
                    if password_hash != md5(password.encode('utf-8')).digest():
                        raise RuntimeError('Введён неправильный пароль.')
                    if crypto_type == b'aes':
                        content = aes_decrypt(module_file.read())
                    elif crypto_type == b'xor':
                        content = xor_str(module_file.read())
                    else:
                        raise RuntimeError('Неизвестный тип шифрования файла модуля.')
                emw = EditModuleWidget(module, crypto_type, password_hash,
                                       content, self.modules_cb.currentIndex(), self)
                emw.edited.connect(self.update_edited_module)
                emw.show()
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

    @Slot()
    def delete_module(self):
        del self.modules[self.modules_cb.currentIndex()]
        self.modules_cb.removeItem(self.modules_cb.currentIndex())

    @Slot(int)
    def set_module(self, index):
        if index > -1:
            self.show_module(self.modules[index])
        else:
            self.scroll.widget().setParent(None)
            self.modules_cb.setVisible(False)
            self.buttons_widget.setVisible(False)

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
        if len(self.modules) == 0:
            self.modules.append({
                'full_name': module_full_name,
                'short_name': module_short_name
            })
            self.modules_cb.setVisible(True)
            self.buttons_widget.setVisible(True)
            self.modules_cb.addItem(module_short_name)
            mb = QMessageBox(self)
            mb.setWindowTitle('Успешно')
            mb.setText('Модуль успешно добавлен.')
            mb.show()
        else:
            for m in self.modules:
                if m['full_name'] == module_full_name:
                    mb = QMessageBox(self)
                    mb.setWindowTitle('Ошибка')
                    mb.setText(f"Модуль '{module_short_name}' уже добавлен.")
                    mb.show()
                    return
            self.modules.append({
                'full_name': module_full_name,
                'short_name': module_short_name
            })
            self.modules_cb.addItem(module_short_name)
            mb = QMessageBox(self)
            mb.setWindowTitle('Успешно')
            mb.setText('Модуль успешно добавлен.')
            mb.show()

    def show_module(self, module):
        try:
            with open(module['full_name'], 'rb') as module_file:
                crypto_type = module_file.read(3)
                password_hash = module_file.read(md5().digest_size)
                if crypto_type == b'aes':
                    content = aes_decrypt(module_file.read())
                elif crypto_type == b'xor':
                    content = xor_str(module_file.read())
                else:
                    raise RuntimeError('Неизвестный тип шифрования файла модуля.')
            parsed_data = parse(content)
            parsed_data['module_name'] = module['short_name']
            w = self.scroll.widget()
            if w is not None:
                w.setParent(None)
            mc = ModuleContentWidget(parsed_data, self.scroll)
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
