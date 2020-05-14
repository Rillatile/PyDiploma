from subprocess import check_output, CalledProcessError, STDOUT


def execute(data, block_number):
    block = data['blocks'][block_number]
    result = []
    for i in range(0, len(block['commands'])):
        transformed_command = transform_command(block['commands'][i], data)
        result.append(execute_command(transformed_command, data))
    print(result)


def transform_command(command, data):
    i = 0
    command_str = command['command']
    transformed_command = command
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


def execute_command(command, data):
    try:
        result = check_output(command['command'].split(), stderr=STDOUT)
        result = result.decode('utf-8').strip()
        if command['result_variable'] != '':
            flag = True
            for variable in data['variables']:
                if variable['name'] == command['result_variable']:
                    variable['value'] = result
                    flag = False
                    break
            if flag:
                raise RuntimeError(f"Указана результирующая переменная '{command['result_variable']}', "
                                   + 'но такой переменной не обнаружено. '
                                   + 'Объявите её, используя синтаксис языка описания.')
        return 0, result
    except CalledProcessError as error:
        return error.returncode, error.output.decode('utf-8')


def get_value(name, data):
    for variable in data['variables']:
        if variable['name'] == name:
            return variable['value']
    for constant in data['constants']:
        if constant['name'] == name:
            return constant['value']
    raise RuntimeError(f'Переменной либо константы с именем \'{name}\' не обнаружено.'
                       + ' Объявите её, используя синтаксис языка описания.')
