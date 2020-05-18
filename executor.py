import pexpect
from copy import deepcopy
from PySide2.QtWidgets import QInputDialog, QLineEdit, QMessageBox


def execute(data, block_number, parent):
    block = data['blocks'][block_number]
    result = []
    for i in range(0, len(block['commands'])):
        transformed_command = transform_command(block['commands'][i], data)
        try:
            result.append(execute_command(transformed_command, data, parent))
        except RuntimeError as error:
            mb = QMessageBox(parent)
            mb.setWindowTitle('Ошибка')
            mb.setText(str(error))
            mb.show()
    return result


def transform_command(command, data):
    i = 0
    command_str = command['command']
    transformed_command = deepcopy(command)
    while i < len(command_str):
        if command_str[i] == '$':
            i += 1
            if (i < len(command_str)
                    and (command_str[i].isalpha()
                         or command_str[i] == '_')):
                name = command_str[i]
                i += 1
                while (i < len(command_str)
                       and (command_str[i].isalpha()
                            or command_str[i] == '_'
                            or command_str[i].isnumeric())):
                    name += command_str[i]
                    i += 1
                if i < len(command_str) and command_str[i] == '=':
                    raise RuntimeError('Запрещено производить присваивание значения из bash,'
                                       + f' команда \'{command_str}\'. Используйте синтаксис языка описания.')
                if name == transformed_command['result_variable']:
                    raise RuntimeError(f'Переменная \'{name}\' является результирующей для команды \'{command_str}\'.'
                                       + ' Запрещено использовать в команде результирующую переменную.')
                transformed_command['command'] = transformed_command['command'].replace('$' + name,
                                                                                        get_value(name, data))
            else:
                raise RuntimeError(f'В команде \'{command_str}\''
                                   + f" после символа '$'[{i - 1}] ожидалось имя переменной либо константы.")
        else:
            i += 1
    return transformed_command


def execute_command(command, data, parent):
    p = pexpect.spawn(command['command'])
    if command['command'][:4] == 'sudo':
        p.expect('\[sudo\] ')
        password, ok = QInputDialog().getText(parent, 'Ввод пароля',
                                              'Введите пароль для sudo:', QLineEdit.Password)
        if ok:
            p.sendline(password)
        else:
            p.close()
            raise RuntimeError(f"Для выполнения команды '{command['command']}' требуется пароль для sudo.")
    idx = p.expect([pexpect.EOF, '\[sudo\] '])
    if idx == 1:
        mb = QMessageBox(parent)
        mb.setWindowTitle('Ошибка')
        mb.setText('Введён неправильный пароль для sudo. Выполнение блока остановлено.')
        mb.show()
        p.close()
        return p.exitstatus, 'Введён неправильный пароль для sudo. Выполнение блока остановлено.'
    result = p.before.decode('utf-8')
    p.close()
    if command['command'][:4] == 'sudo':
        result = result[result.find(':') + 1:]
    if command['result_variable'] != '':
        set_result_variable_value(command, data, result)
    return p.exitstatus, result


def set_result_variable_value(command, data, value):
    flag = True
    for variable in data['variables']:
        if variable['name'] == command['result_variable']:
            variable['value'] = value
            flag = False
            break
    if flag:
        raise RuntimeError(f"Указана результирующая переменная '{command['result_variable']}', "
                           + 'но такой переменной не обнаружено. '
                           + 'Объявите её, используя синтаксис языка описания.')


def get_value(name, data):
    for variable in data['variables']:
        if variable['name'] == name:
            return variable['value']
    for constant in data['constants']:
        if constant['name'] == name:
            return constant['value']
    raise RuntimeError(f'Переменной либо константы с именем \'{name}\' не обнаружено.'
                       + ' Объявите её, используя синтаксис языка описания.')
