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


def create_basic_text():
    return ('Variables {\n\n}\n\n'
            + 'Constants {\n\n}\n\n'
            + 'Blocks {\n [\n  name: "";\n  description: "";\n  commands: (\n\n  )\n ]\n}\n\n'
            + 'Check {\n if: ;\n good_message: "";\n bad_message: "";\n}\n')


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
        mb = QMessageBox(self)
        mb.setWindowTitle('Помощь')
        mb.setText('Бла-бла-бла.')
        mb.show()
