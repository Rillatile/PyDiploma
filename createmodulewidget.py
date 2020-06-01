from PySide2.QtWidgets import (QMainWindow, QWidget,
                               QTextEdit, QPushButton,
                               QFileDialog, QVBoxLayout,
                               QComboBox, QLabel,
                               QMessageBox, QInputDialog,
                               QLineEdit)
from PySide2.QtCore import Qt, Slot, Signal
from PySide2.QtGui import QTextCursor
from cryptography import aes_encrypt, xor_bytes
from hashlib import md5
from parser import parse
from scrollmessagebox import ScrollMessageBox


def create_basic_text():
    return ('Variables {\n\n}\n\n'
            + 'Constants {\n\n}\n\n'
            + 'Blocks {\n [\n  name: "";\n  description: "";\n  commands: (\n\n  )\n ]\n}\n\n'
            + 'Check {\n if: ;\n good_message: "";\n bad_message: "";\n}\n')


def get_help_text():
    return ('Каждая строка с кодом должна оканчиваться символом «точка с запятой».\n\n'
            + 'Имеются блоки, описывающие аспекты исполнения. Есть четыре вида блоков: блок переменных, '
            + 'блок констант, блок операций и итоговый блок проверки. Блок переменных содержит объявления '
            + 'переменных, используемых во время исполнения модуля. При этом есть несколько вариантов объявления '
            + 'переменной:\n- без указания её описания и значения по умолчанию;\n- с указанием её описания, '
            + 'но без указания значения по умолчанию;\n- без указания её описания, но с указанием значения '
            + 'по умолчанию;\n- с указанием и её описания, и значения по умолчанию.\n\nНиже приведён '
            + 'пример блока переменных.\n\nVariables {\n  a; /* Простое объявление переменной. */\n'
            + '  b: "Просто переменная"; /* Объявление переменной с указанием её описания. */\n'
            + '  str = "Строка"; /* Объявление переменной с присвоением ей значения по умолчанию. */\n'
            + '  !counter:  "Переменная-счётчик"  =  0;  /* Объявление  переменной  с указанием её описания '
            + 'и присвоением значения по умолчанию. При этом префикс  «!»  означает,  что  для  данной  переменной '
            + 'не требуется ввод значения через GUI. */\n}\n\nБлок констант аналогичен блоку переменных за исключением'
            + ' того, что константам обязательно должно присваиваться значение. Для них оно будет не значением по '
            + 'умолчанию, а постоянным значением. Ниже показан пример блока констант.\n\n'
            + 'Constants {\n  PI: "Число Пи" = 3.1415926; /* Объявление константы. Константы обязаны объявляться '
            + 'с присвоением значения. */\n}\n\nВсе переменные и константы, использующиеся в командах, должны быть'
            + ' предварительно объявлены в соответствующих блоках.\n\nБлок операций содержит в себе блоки, '
            + 'производящие какие-либо действия. Данные блоки выделяются квадратными скобками и содержат в себе'
            + ' следующие поля:\n- name – название блока;\n- description – описание блока;\n'
            + '- commands – исполняемые команды.\n\nПример блока операций представлен ниже.\n\n'
            + 'Blocks {\n  [\n    name: "Демонстрационный блок №1"; /* Название блока. */\n    description: "Блок, '
            + 'предназначенный для демонстрации базовых примеров."; /* Описание блока . */\n'
            + '    commands: ( /* Исполняемые команды.*/\n      a = "ls/"; /* Данная запись означает, что результат '
            + 'выполнения команды (записана в двойных ковычках) будет записан в переменную "a". */\n'
            + '      "echo $a";\n    )\n  ],\n  [\n    name: "Блок №2";\n    description: "Тестовый блок №2.";\n'
            + '    commands: (\n      "echo \'Число Пи равно $PI.\'";\n    )\n  ]\n}\n\n'
            + 'Итоговый блок проверки содержит следующие поля:\n- if – условие, которое проверяется после выполнения '
            + 'модуля и проверяет правильность его выполнения;\n- good_message – сообщение, которое показывается '
            + 'пользователю в случае успешного выполнения модуля;\n- bad_message – сообщение, которое показывается'
            + ' пользователю в случае неудачного выполнения модуля.\n\n'
            + 'Ниже показан пример итогового блока проверки.\n\n'
            + 'Check {\n  if: $result > 0 and $result < 10;\n  good_message: "Модуль выполнился успешно!";\n  '
            + 'bad_message: "Выполнение модуля завершилось неудачей.";\n}\n\n'
            + 'Стоит отметить, что обязательным полем является только «if», «good_message» и «bad_message» указывать'
            + ' необязательно. В этом случае для них будут установлены значения по умолчанию.')


class CreateModuleWidget(QMainWindow):
    def __init__(self, parent=None):
        super(CreateModuleWidget, self).__init__(parent)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle('Создание нового модуля')
        self.setMinimumSize(720, 540)
        self.central_widget = QWidget(self)
        self.text_editor = QTextEdit()
        self.type_of_crypto = QComboBox()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self.central_widget)
        layout.addWidget(self.text_editor)
        help_button = QPushButton('Помощь по синтаксису')
        help_button.clicked.connect(self.help_syntax)
        layout.addWidget(help_button)
        crypto_label = QLabel('Алгоритм шифрования')
        crypto_label.setStyleSheet('font-style: italic;')
        crypto_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(crypto_label)
        self.type_of_crypto.addItem('XOR')
        self.type_of_crypto.addItem('AES-256')
        layout.addWidget(self.type_of_crypto)
        create_button = QPushButton('Сохранить модуль')
        create_button.setStyleSheet('font-weight: bold;')
        create_button.clicked.connect(self.save_module)
        layout.addWidget(create_button)
        self.text_editor.setText(create_basic_text())
        cursor = QTextCursor(self.text_editor.document())
        cursor.movePosition(QTextCursor.End)
        self.text_editor.setTextCursor(cursor)
        self.setCentralWidget(self.central_widget)

    module_created = Signal(str)

    @Slot()
    def save_module(self):
        password, ok = QInputDialog().getText(self, 'Ввод пароля',
                                              'Введите пароль для редактирования модуля:', QLineEdit.Password)
        if ok:
            try:
                parsed_data = parse(self.text_editor.toPlainText())
                module_full_path = QFileDialog.getSaveFileName(self, filter='*.module')[0]
                if module_full_path.find('.module') == -1:
                    module_full_path += '.module'
                with open(module_full_path, 'wb') as file:
                    if self.type_of_crypto.currentIndex() == 0:
                        file.write(b'xor'
                                   + md5(password.encode('utf-8')).digest()
                                   + xor_bytes(self.text_editor.toPlainText()))
                    else:
                        file.write(b'aes'
                                   + md5(password.encode('utf-8')).digest()
                                   + aes_encrypt(self.text_editor.toPlainText()))
            except IOError:
                mb = QMessageBox(self)
                mb.setWindowTitle('Ошибка')
                mb.setText('При сохранении файла модуля возникла ошибка.')
                mb.show()
            except (SyntaxError, RuntimeError) as error:
                mb = QMessageBox(self)
                mb.setWindowTitle('Ошибка')
                mb.setText(str(error))
                mb.show()
            else:
                self.module_created.emit(module_full_path)
                self.close()

    @Slot()
    def help_syntax(self):
        smb = ScrollMessageBox('Помощь', get_help_text(), parent=self)
        smb.show()
