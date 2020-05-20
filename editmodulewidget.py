from PySide2.QtWidgets import (QMainWindow, QWidget,
                               QTextEdit, QPushButton,
                               QFileDialog, QVBoxLayout,
                               QMessageBox)
from PySide2.QtCore import Qt, Slot, Signal
from PySide2.QtGui import QTextCursor
from cryptography import aes_encrypt, xor_bytes
from parser import parse


class EditModuleWidget(QMainWindow):
    def __init__(self, module_info, crypto_type, password_hash, text, idx, parent=None):
        super(EditModuleWidget, self).__init__(parent)
        self.setWindowModality(Qt.ApplicationModal)
        self.module_info = module_info
        self.crypto_type = crypto_type
        self.password_hash = password_hash
        self.setWindowTitle(f"Редактирование модуля '{module_info['short_name']}'")
        self.setMinimumSize(720, 540)
        self.central_widget = QWidget(self)
        self.text_editor = QTextEdit()
        self.text_editor.setText(text)
        self.idx = idx
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self.central_widget)
        layout.addWidget(self.text_editor)
        help_button = QPushButton('Помощь по синтаксису')
        help_button.clicked.connect(self.help_syntax)
        layout.addWidget(help_button)
        save_button = QPushButton('Сохранить изменения')
        save_button.setStyleSheet('font-weight: bold;')
        save_button.clicked.connect(self.save_module)
        layout.addWidget(save_button)
        save_as_button = QPushButton('Сохранить как ...')
        save_as_button.setStyleSheet('font-style: italic;')
        save_as_button.clicked.connect(self.save_as_module)
        layout.addWidget(save_as_button)
        cursor = QTextCursor(self.text_editor.document())
        cursor.movePosition(QTextCursor.End)
        self.text_editor.setTextCursor(cursor)
        self.setCentralWidget(self.central_widget)

    edited = Signal(int)

    @Slot()
    def save_module(self):
        try:
            parsed_data = parse(self.text_editor.toPlainText())
            with open(self.module_info['full_name'], 'wb') as file:
                if self.crypto_type == b'xor':
                    file.write(b'xor'
                               + self.password_hash
                               + xor_bytes(self.text_editor.toPlainText()))
                elif self.crypto_type == b'aes':
                    file.write(b'aes'
                               + self.password_hash
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
            self.edited.emit(self.idx)
            self.close()

    @Slot()
    def save_as_module(self):
        try:
            parsed_data = parse(self.text_editor.toPlainText())
            module_full_path = QFileDialog.getSaveFileName(self,
                                                           dir=self.module_info['full_name']
                                                           .replace(self.module_info['short_name'], ''),
                                                           filter='*.module')[0]
            if module_full_path.find('.module') == -1:
                module_full_path += '.module'
            with open(module_full_path, 'wb') as file:
                if self.crypto_type == b'xor':
                    file.write(b'xor'
                               + self.password_hash
                               + xor_bytes(self.text_editor.toPlainText()))
                elif self.crypto_type == b'aes':
                    file.write(b'aes'
                               + self.password_hash
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
            if module_full_path == self.module_info['full_name']:
                self.edited.emit(self.idx)
            self.close()

    @Slot()
    def help_syntax(self):
        mb = QMessageBox(self)
        mb.setWindowTitle('Помощь')
        mb.setText('Бла-бла-бла.')
        mb.show()
