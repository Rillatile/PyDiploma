def is_keyword(word):
    keywords = [
        'Variables',
        'Constants',
        'Blocks'
    ]
    for keyword in keywords:
        if keyword == word:
            return True
    return False


def skip_spaces(source, position, line_number):
    while position < len(source) and source[position].isspace():
        if source[position] == '\n':
            line_number += 1
        position += 1
    return position, line_number


def parse_variable(unparsed_variable, line_number, is_entered):
    variable = {
        'name': '',
        'description': 'Описание отсутствует.',
        'value': '',
        'is_entered': is_entered
    }
    i = 0
    while (i < len(unparsed_variable)
           and (unparsed_variable[i].isalpha()
                or unparsed_variable[i] == '_'
                or unparsed_variable[i].isnumeric())):
        variable['name'] += unparsed_variable[i]
        i += 1
    i, line_number = skip_spaces(unparsed_variable, i, line_number)
    if i < len(unparsed_variable) and unparsed_variable[i] == ':':
        description = ''
        i += 1
        i, line_number = skip_spaces(unparsed_variable, i, line_number)
        check_expected_symbol('"', unparsed_variable, i, line_number)
        i += 1
        while i < len(unparsed_variable) and unparsed_variable[i] != '"':
            description += unparsed_variable[i]
            i += 1
        check_expected_symbol('"', unparsed_variable, i, line_number)
        i += 1
        i, line_number = skip_spaces(unparsed_variable, i, line_number)
        if description != '':
            variable['description'] = description.strip()
    if i < len(unparsed_variable) and unparsed_variable[i] == '=':
        i += 1
        i, line_number = skip_spaces(unparsed_variable, i, line_number)
        if i >= len(unparsed_variable):
            raise SyntaxError(f"Ожидалось значение переменной '{variable['name']}', строка {line_number}.")
        if unparsed_variable[i] == '-' or unparsed_variable[i].isnumeric():
            variable['value'] += unparsed_variable[i]
            i += 1
            while i < len(unparsed_variable) and unparsed_variable[i].isnumeric():
                variable['value'] += unparsed_variable[i]
                i += 1
            if (i < len(unparsed_variable)
                    and (unparsed_variable[i] == '.'
                         or unparsed_variable[i] == ',')):
                variable['value'] += '.'
                i += 1
                while i < len(unparsed_variable) and unparsed_variable[i].isnumeric():
                    variable['value'] += unparsed_variable[i]
                    i += 1
            if variable['value'][-1] == '.':
                variable['value'] = variable['value'][:-1]
        elif unparsed_variable[i] == '"':
            i += 1
            while i < len(unparsed_variable) and unparsed_variable[i] != '"':
                variable['value'] += unparsed_variable[i]
                i += 1
            check_expected_symbol('"', unparsed_variable, i, line_number)
            i += 1
        else:
            raise_incorrect_symbol(unparsed_variable[i], line_number)
    i, line_number = skip_spaces(unparsed_variable, i, line_number)
    if i < len(unparsed_variable):
        raise_incorrect_symbol(unparsed_variable[i], line_number)
    return variable


def parse_constant(unparsed_constant, line_number):
    constant = {
        'name': '',
        'description': 'Описание отсутствует.',
        'value': ''
    }
    i = 0
    start_line_number = line_number
    while (i < len(unparsed_constant)
           and (unparsed_constant[i].isalpha()
                or unparsed_constant[i] == '_'
                or unparsed_constant[i].isnumeric())):
        constant['name'] += unparsed_constant[i]
        i += 1
    i, line_number = skip_spaces(unparsed_constant, i, line_number)
    if i < len(unparsed_constant) and unparsed_constant[i] == ':':
        description = ''
        i += 1
        i, line_number = skip_spaces(unparsed_constant, i, line_number)
        check_expected_symbol('"', unparsed_constant, i, line_number)
        i += 1
        while i < len(unparsed_constant) and unparsed_constant[i] != '"':
            description += unparsed_constant[i]
            i += 1
        check_expected_symbol('"', unparsed_constant, i, line_number)
        i += 1
        i, line_number = skip_spaces(unparsed_constant, i, line_number)
        if description != '':
            constant['description'] = description.strip()
    if i < len(unparsed_constant) and unparsed_constant[i] == '=':
        i += 1
        i, line_number = skip_spaces(unparsed_constant, i, line_number)
        if i >= len(unparsed_constant):
            raise SyntaxError(f"Ожидалось значение константы '{constant['name']}', строка {line_number}.")
        if unparsed_constant[i] == '-' or unparsed_constant[i].isnumeric():
            constant['value'] += unparsed_constant[i]
            i += 1
            while i < len(unparsed_constant) and unparsed_constant[i].isnumeric():
                constant['value'] += unparsed_constant[i]
                i += 1
            if (i < len(unparsed_constant)
                    and (unparsed_constant[i] == '.'
                         or unparsed_constant[i] == ',')):
                constant['value'] += '.'
                i += 1
                while i < len(unparsed_constant) and unparsed_constant[i].isnumeric():
                    constant['value'] += unparsed_constant[i]
                    i += 1
            if constant['value'][-1] == '.':
                constant['value'] = constant['value'][:-1]
        elif unparsed_constant[i] == '"':
            i += 1
            while i < len(unparsed_constant) and unparsed_constant[i] != '"':
                constant['value'] += unparsed_constant[i]
                i += 1
            check_expected_symbol('"', unparsed_constant, i, line_number)
            i += 1
        else:
            raise_incorrect_symbol(unparsed_constant[i], line_number)
    i, line_number = skip_spaces(unparsed_constant, i, line_number)
    if i < len(unparsed_constant):
        raise_incorrect_symbol(unparsed_constant[i], line_number)
    if constant['value'] == '':
        raise RuntimeError(f"Константа не может быть объявлена без значения, строка {start_line_number}: "
                           + f"\'{constant['name']}\'.")
    return constant


def get_name_or_description(unparsed_block, position, line_number):
    check_expected_symbol('"', unparsed_block, position, line_number)
    if position < len(unparsed_block) and unparsed_block[position] == '"':
        position += 1
        unparsed_name = ''
        while position < len(unparsed_block) and unparsed_block[position] != '"':
            unparsed_name += unparsed_block[position]
            position += 1
        check_expected_symbol('"', unparsed_block, position, line_number)
        position += 1
        position, line_number = skip_spaces(unparsed_block, position, line_number)
        check_expected_symbol(';', unparsed_block, position, line_number)
    return unparsed_name.strip(), position, line_number


def parse_block(unparsed_block, line_number):
    block = {
        'name': '',
        'description': 'Описание отсутствует.',
        'commands': []
    }
    i = 0
    while i < len(unparsed_block):
        if unparsed_block[i].isspace():
            if unparsed_block[i] == '\n':
                line_number += 1
            i += 1
        elif unparsed_block[i].isalpha():
            word = unparsed_block[i]
            i += 1
            while i < len(unparsed_block) and unparsed_block[i].isalpha():
                word += unparsed_block[i]
                i += 1
            i, line_number = skip_spaces(unparsed_block, i, line_number)
            check_expected_symbol(':', unparsed_block, i, line_number)
            i += 1
            i, line_number = skip_spaces(unparsed_block, i, line_number)
            if word == 'name':
                block['name'], i, line_number = get_name_or_description(unparsed_block, i, line_number)
            elif word == 'description':
                description, i, line_number = get_name_or_description(unparsed_block, i, line_number)
                if description != '':
                    block['description'] = description
            elif word == 'commands':
                check_expected_symbol('(', unparsed_block, i, line_number)
                i += 1
                while i < len(unparsed_block) and unparsed_block[i] != ')':
                    if unparsed_block[i].isspace():
                        if unparsed_block[i] == '\n':
                            line_number += 1
                        i += 1
                    elif (unparsed_block[i].isalpha()
                          or unparsed_block[i] == '_'
                          or unparsed_block[i] == '"'):
                        command = {
                            'result_variable': '',
                            'command': '',
                            'description': 'Описание отсутствует.'
                        }
                        if unparsed_block[i].isalpha() or unparsed_block[i] == '_':
                            name = unparsed_block[i]
                            i += 1
                            while (i < len(unparsed_block) and (unparsed_block[i].isalpha()
                                                                or unparsed_block[i].isnumeric()
                                                                or unparsed_block[i] == '_')):
                                name += unparsed_block[i]
                                i += 1
                            command['result_variable'] = name
                            i, line_number = skip_spaces(unparsed_block, i, line_number)
                            check_expected_symbol('=', unparsed_block, i, line_number)
                            i += 1
                            i, line_number = skip_spaces(unparsed_block, i, line_number)
                            check_expected_symbol('"', unparsed_block, i, line_number)
                        i += 1
                        while i < len(unparsed_block) and unparsed_block[i] != '"':
                            command['command'] += unparsed_block[i]
                            i += 1
                        check_expected_symbol('"', unparsed_block, i, line_number)
                        i += 1
                        i, line_number = skip_spaces(unparsed_block, i, line_number)
                        if i < len(unparsed_block) and unparsed_block[i] == ':':
                            i += 1
                            i, line_number = skip_spaces(unparsed_block, i, line_number)
                            check_expected_symbol('"', unparsed_block, i, line_number)
                            i += 1
                            command_description = ''
                            while i < len(unparsed_block) and unparsed_block[i] != '"':
                                command_description += unparsed_block[i]
                                i += 1
                            check_expected_symbol('"', unparsed_block, i, line_number)
                            i += 1
                            if command_description != '':
                                command['description'] = command_description
                        check_expected_symbol(';', unparsed_block, i, line_number)
                        i += 1
                        block['commands'].append(command)
                    else:
                        raise_incorrect_symbol(unparsed_block[i], line_number)
            else:
                raise SyntaxError(f'Некорректное поле блока, строка {line_number}: \'{word}\'.')
            i += 1
        else:
            raise_incorrect_symbol(unparsed_block[i], line_number)
    return block


def parse_variables_block(source, line_number, parsed_data):
    i = 0
    is_entered = True
    while i < len(source):
        if source[i].isspace():
            if source[i] == '\n':
                line_number += 1
            i += 1
        elif source[i] == '!':
            is_entered = False
            i += 1
        elif source[i].isalpha() or source[i] == '_':
            start_line_number = line_number
            unparsed_variable = source[i]
            i += 1
            while i < len(source) and source[i] != ';':
                unparsed_variable += source[i]
                if source[i] == '\n':
                    line_number += 1
                i += 1
            check_expected_symbol(';', source, i, line_number)
            variable = parse_variable(unparsed_variable, start_line_number, is_entered)
            i += 1
            is_entered = True
            parsed_data['variables'].append(variable)
        else:
            raise_incorrect_symbol(source[i], line_number)


def parse_constants_block(source, line_number, parsed_data):
    i = 0
    while i < len(source):
        if source[i].isspace():
            if source[i] == '\n':
                line_number += 1
            i += 1
        elif source[i].isalpha() or source[i] == '_':
            start_line_number = line_number
            unparsed_constant = source[i]
            i += 1
            while i < len(source) and source[i] != ';':
                unparsed_constant += source[i]
                if source[i] == '\n':
                    line_number += 1
                i += 1
            check_expected_symbol(';', source, i, line_number)
            constant = parse_constant(unparsed_constant, start_line_number)
            i += 1
            parsed_data['constants'].append(constant)
        else:
            raise_incorrect_symbol(source[i], line_number)


def parse_blocks_block(source, line_number, parsed_data):
    is_block_expected = False
    i = 0
    while i < len(source):
        if source[i].isspace():
            if source[i] == '\n':
                line_number += 1
            i += 1
        elif source[i] == '[':
            start_line_number = line_number
            is_block_expected = False
            i += 1
            unparsed_block = ''
            while i < len(source) and source[i] != ']':
                unparsed_block += source[i]
                if source[i] == '\n':
                    line_number += 1
                i += 1
            check_expected_symbol(']', source, i, line_number)
            i += 1
            block = parse_block(unparsed_block, start_line_number)
            parsed_data['blocks'].append(block)
        elif source[i] == ',':
            is_block_expected = True
            i += 1
        else:
            raise_incorrect_symbol(source[i], line_number)
    if is_block_expected:
        raise RuntimeError(f'Ожидался исполняемый блок, строка {line_number}.')


def parse_keyword_block(keyword, source, line_number, parsed_data):
    if keyword == 'Variables':
        parse_variables_block(source, line_number, parsed_data)
    elif keyword == 'Constants':
        parse_constants_block(source, line_number, parsed_data)
    elif keyword == 'Blocks':
        parse_blocks_block(source, line_number, parsed_data)


def check_expected_symbol(symbol, source, position, line_number):
    if position >= len(source):
        raise RuntimeError('Ожидался символ \'' + symbol + f'\', строка {line_number}.')
    elif source[position] != symbol:
        raise SyntaxError(f'Некорректный символ, строка {line_number}: \'{source[position]}\'.'
                          + ' Ожидался символ \'' + symbol + '\'.')


def raise_incorrect_symbol(symbol, line_number):
    raise SyntaxError(f'Некорректный символ, строка {line_number}: \'{symbol}\'.')


def parse(source):
    line_number = 1
    i = 0
    parsed_data = {
        'variables': [],
        'constants': [],
        'blocks': []
    }
    while i < len(source):
        if source[i].isspace():
            if source[i] == '\n':
                line_number += 1
            i += 1
        elif source[i].isalpha():
            word = source[i]
            i += 1
            while i < len(source) and source[i].isalpha():
                word += source[i]
                i += 1
            if is_keyword(word):
                i, line_number = skip_spaces(source, i, line_number)
                check_expected_symbol('{', source, i, line_number)
                start_line_number = line_number
                keyword_block = source[i]
                i += 1
                while i < len(source) and source[i] != '}':
                    if source[i] == '{':
                        raise_incorrect_symbol(source[i], line_number)
                    keyword_block += source[i]
                    if source[i] == '\n':
                        line_number += 1
                    i += 1
                check_expected_symbol('}', source, i, line_number)
                keyword_block += source[i]
                i += 1
                parse_keyword_block(word, keyword_block[1:-1], start_line_number, parsed_data)
            else:
                raise SyntaxError(f'Обнаружено неключевое слово, строка {line_number}: \'{word}\'.')
        else:
            raise_incorrect_symbol(source[i], line_number)
    return parsed_data
