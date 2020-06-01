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
from sys import argv


# Класс, описывающий главное окно программы
class MainWindow(QMainWindow):
    # Конструктор
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

    # Метод инициализации UI
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
        self.setCentralWidget(self.central_widget)
        self.load_modules()
        if self.scroll.widget() is None:
            self.modules_cb.setVisible(False)
            self.buttons_widget.setVisible(False)
        self.scroll.setAlignment(Qt.AlignCenter)

    # Слот, обрабатывающий запрос пользователя на создание нового модуля (нажатие соответствующей кнопки)
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

    # Слот, обрабатывающий событие изменения модуля
    @Slot(int)
    def update_edited_module(self, idx):
        self.show_module(self.modules[idx])

    # Слот, обрабатывающий запрос пользователя на изменение модуля (нажатие соответствующей кнопки)
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

    # Слот, обрабатывающий запрос пользователя на удаление модуля (нажатие соответствующей кнопки)
    @Slot()
    def delete_module(self):
        try:
            with open(argv[0].replace('main.py', 'data'), 'rb') as file:
                data = file.read()
            data_list = data.decode('utf-8').split('\n')[:-1]
            for i in range(0, len(data_list)):
                if data_list[i].find(self.modules[self.modules_cb.currentIndex()]['full_name']) > -1:
                    data_list[i] = ''.encode('utf-8')
                else:
                    data_list[i] = (data_list[i] + '\n').encode('utf-8')
            with open(argv[0].replace('main.py', 'data'), 'wb') as file:
                file.writelines(data_list)
        except IOError:
            mb = QMessageBox(self)
            mb.setWindowTitle('Ошибка')
            mb.setText('Не удалось удалить данные о модуле.')
            mb.show()
        del self.modules[self.modules_cb.currentIndex()]
        self.modules_cb.removeItem(self.modules_cb.currentIndex())

    # Слот, обрабатывающий изменение выбранного модуля
    @Slot(int)
    def set_module(self, index):
        if index > -1:
            self.show_module(self.modules[index])
        else:
            self.scroll.widget().setParent(None)
            self.modules_cb.setVisible(False)
            self.buttons_widget.setVisible(False)

    # Слот, обрабатывающий запрос пользователя на показ информации о программе (нажатие соответствующей кнопки)
    @Slot()
    def show_about(self):
        mb = QMessageBox(self)
        mb.setWindowTitle('О программе')
        mb.setText('Данная программа предназначена для создания, редактирования и исполнения модулей, '
                   + 'взаимодействующих с операционной системой.')
        mb.show()

    # Слот, обрабатывающий запрос пользователя на закрытие программы (выбора соответствующего пункта меню)
    @Slot()
    def close_program(self):
        self.close()

    # Слот, обрабатывающий запрос пользователя на добавление существующего модуля (выбора соответствующего пункта меню)
    @Slot()
    def add_module(self):
        module_full_name = QFileDialog.getOpenFileName(self, 'Выберите модуль', QDir.homePath(), '*.module')[0]
        if module_full_name != '':
            idx = module_full_name.rfind('/')
            if idx != -1:
                module_short_name = module_full_name[idx + 1:]
                self.check_module(module_full_name, module_short_name)

    # Метод для проверки модуля на корректность перед добавлением
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
            self.save_module_data(module_full_name, module_short_name)
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
            self.save_module_data(module_full_name, module_short_name)

    # Метод сохранения данных о добавленных модулях
    def save_module_data(self, module_full_name, module_short_name):
        try:
            with open(argv[0].replace('main.py', 'data'), 'ab') as file:
                file.write((module_full_name + '|').encode('utf-8'))
                file.write((module_short_name + '\n').encode('utf-8'))
        except IOError:
            mb = QMessageBox(self)
            mb.setWindowTitle('Ошибка')
            mb.setText('Не удалось сохранить информацию о добавленном модуле.')
            mb.show()

    # Метод отображения модуля
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

    # Метод загрузки данных о добавленных ранее модулях
    def load_modules(self):
        try:
            with open(argv[0].replace('main.py', 'data'), 'rb') as file:
                data = file.read()
                str_data_list = data.decode('utf-8').split('\n')[:-1]
                for m in str_data_list:
                    self.modules.append({
                        'full_name': m.split('|')[0],
                        'short_name': m.split('|')[1]
                    })
                    self.modules_cb.addItem(self.modules[-1]['short_name'])
        except IOError:
            mb = QMessageBox(self)
            mb.setWindowTitle('Ошибка')
            mb.setText('Не удалось получить информацию о добавленных ранее модулях.')
            mb.show()
