import pexpect
from copy import deepcopy
from PySide2.QtWidgets import QInputDialog, QLineEdit


# Функция выполнения блока
def execute(data, block_number, parent):
    block = data['blocks'][block_number]
    result = []
    # Для каждой команды в блоке
    for i in range(0, len(block['commands'])):
        # Получаем значения используемых в команде переменных и констант, если это необходимо
        transformed_command = transform_command(block['commands'][i], data)
        try:
            # Выполняем команду
            result.append(execute_command(transformed_command, data, parent))
        # Если случилась ошибка
        except RuntimeError as error:
            raise error
    return result


# Функция замены переменных / констант в команде на их значения
def transform_command(command, data):
    i = 0
    command_str = command['command'].replace('\\"', '"') \
        .replace('\\[', '[') \
        .replace('\\]', ']') \
        .replace('\\{', '{') \
        .replace('\\}', '}') \
        .replace('\\(', '(') \
        .replace('\\)', ')')
    transformed_command = deepcopy(command)
    transformed_command['command'] = command_str
    # Идём посимвольно по команде
    while i < len(command_str):
        # Если наткнулись на переменную / константу
        if command_str[i] == '$' and i + 1 < len(command_str) and not command_str[i + 1].isnumeric():
            i += 1
            if (i < len(command_str)
                    and (command_str[i].isalpha()
                         or command_str[i] == '_')):
                # Получаем имя
                name = command_str[i]
                i += 1
                while (i < len(command_str)
                       and (command_str[i].isalpha()
                            or command_str[i] == '_'
                            or command_str[i].isnumeric())):
                    name += command_str[i]
                    i += 1
                # Нельзя производить присваивание в обход синтаксиса языка описания
                if i < len(command_str) and command_str[i] == '=':
                    raise RuntimeError('Запрещено производить присваивание значения из bash,'
                                       + f' команда \'{command_str}\'. Используйте синтаксис языка описания.')
                # Если в команде используется переменная, в которую записывается результат выполнения данной команды
                if name == transformed_command['result_variable']:
                    raise RuntimeError(f'Переменная \'{name}\' является результирующей для команды \'{command_str}\'.'
                                       + ' Запрещено использовать в команде результирующую переменную.')
                # Подставляем вместо имени переменной / константы её значение
                value = get_value(name, data)
                transformed_command['command'] = transformed_command['command'].replace('$' + name, value)
            else:
                raise RuntimeError(f'В команде \'{command_str}\''
                                   + f" после символа '$'[{i - 1}] ожидалось имя переменной либо константы.")
        else:
            i += 1
    return transformed_command


# Функция выполнения команды
def execute_command(command, data, parent):
    # Запускаем дочерний процесс с командной оболочкой и передаём в него команду
    p = pexpect.spawn('/bin/bash', ['-c', command['command']])
    # Если требуется ввести пароль для sudo
    if command['command'][:4] == 'sudo':
        p.expect('\[sudo\] ')
        # Запрашиваем пароль
        password, ok = QInputDialog().getText(parent, 'Ввод пароля',
                                              'Введите пароль для sudo:', QLineEdit.Password)
        # Если пользователь подтвердил ввод
        if ok:
            # Передаём дочернему процессу пароль
            p.sendline(password)
        else:
            p.close()
            raise RuntimeError(f"Для выполнения команды '{command['command']}' требуется пароль для sudo.")
    idx = p.expect([pexpect.EOF, '\[sudo\] '])
    if idx == 1:
        p.close()
        raise RuntimeError('Введён неправильный пароль для sudo. Выполнение блока остановлено.')
    result = p.before.decode('utf-8')
    p.close()
    if command['command'][:4] == 'sudo':
        result = result[result.find(':') + 1:]
    if command['result_variable'] != '':
        # Получаем результат выполнения команды
        set_result_variable_value(command, data, result)
    return p.exitstatus, result


# Функция записи результата выполнения команды в результирующую переменную
def set_result_variable_value(command, data, value):
    flag = True
    for variable in data['variables']:
        if variable['name'] == command['result_variable']:
            variable['value'] = value
            flag = False
            break
    # Если результирующая переменная указана, но не объявлена
    if flag:
        raise RuntimeError(f"Указана результирующая переменная '{command['result_variable']}', "
                           + 'но такой переменной не обнаружено. '
                           + 'Объявите её, используя синтаксис языка описания.')


# Функция получения значения переменной / константы
def get_value(name, data):
    value = None
    for variable in data['variables']:
        if variable['name'] == name:
            value = variable['value']
    for constant in data['constants']:
        if constant['name'] == name:
            value = constant['value']
    # Если указанная переменная / константа не объявлена
    if value is None:
        raise RuntimeError(f'Переменной либо константы с именем \'{name}\' не обнаружено.'
                           + ' Объявите её, используя синтаксис языка описания.')
    if value == '' or not value[0].isnumeric():
        value = f'"{value}"'
    return value


# Функция проверки выполнения итогового условия проверки правильности выполнения модуля
def check_module_success(data):
    command = {
        'command': data['check']['if'],
        'result_variable': ''
    }
    condition = transform_command(command, data)['command']
    condition = condition.strip().replace('\r\n', '" \\\n"')
    p = pexpect.spawn('python3')
    p.expect('>>>')
    p.sendline(condition)
    result = ['True', 'False', 'Error']
    idx = p.expect(result)
    p.close()
    return result[idx]
