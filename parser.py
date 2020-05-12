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
        if unparsed_variable[i] != '"':
            raise SyntaxError(f'Некорректный символ, строка {line_number}: {unparsed_variable[i]}.'
                              + 'Ожидался символ \'"\'.')
        i += 1
        while i < len(unparsed_variable) and unparsed_variable[i] != '"':
            description += unparsed_variable[i]
            i += 1
        if i >= len(unparsed_variable) or unparsed_variable[i] != '"':
            raise SyntaxError(f'Некорректный символ, строка {line_number}: {unparsed_variable[i]}.'
                              + 'Ожидался символ \'"\'.')
        i += 1
        i, line_number = skip_spaces(unparsed_variable, i, line_number)
        if description != '':
            variable['description'] = description.strip()
    if i < len(unparsed_variable) and unparsed_variable[i] == '=':
        i += 1
        i, line_number = skip_spaces(unparsed_variable, i, line_number)
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
            i, line_number = skip_spaces(unparsed_variable, i, line_number)
            if i < len(unparsed_variable):
                raise SyntaxError(f'Некорректный символ, строка {line_number}: {unparsed_variable[i]}.')
            if variable['value'][-1] == '.':
                variable['value'] = variable['value'][:-1]
        elif unparsed_variable[i] == '"':
            i += 1
            while i < len(unparsed_variable) and unparsed_variable[i] != '"':
                variable['value'] += unparsed_variable[i]
                i += 1
            if i >= len(unparsed_variable) or unparsed_variable[i] != '"':
                raise SyntaxError(f'Некорректный символ, строка {line_number}: {unparsed_variable[i]}.'
                                  + 'Ожидался символ \'"\'.')
            i += 1
            i, line_number = skip_spaces(unparsed_variable, i, line_number)
            if i < len(unparsed_variable):
                raise SyntaxError(f'Некорректный символ, строка {line_number}: {unparsed_variable[i]}.')
        else:
            raise SyntaxError(f'Некорректный символ, строка {line_number}: {unparsed_variable[i]}.')
    i, line_number = skip_spaces(unparsed_variable, i, line_number)
    if i < len(unparsed_variable):
        raise SyntaxError(f'Некорректный символ, строка {line_number}: {unparsed_variable[i]}.')
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
        if i < len(unparsed_constant) and unparsed_constant[i] != '"':
            raise SyntaxError(f'Некорректный символ, строка { line_number }: { unparsed_constant[i] }.'
                              + 'Ожидался символ \'"\'.')
        i += 1
        while i < len(unparsed_constant) and unparsed_constant[i] != '"':
            description += unparsed_constant[i]
            i += 1
        if i >= len(unparsed_constant) or unparsed_constant[i] != '"':
            raise SyntaxError(f'Ожидался символ \'"\', строка { line_number }.')
        i += 1
        i, line_number = skip_spaces(unparsed_constant, i, line_number)
        if description != '':
            constant['description'] = description.strip()
    if i < len(unparsed_constant) and unparsed_constant[i] == '=':
        i += 1
        i, line_number = skip_spaces(unparsed_constant, i, line_number)
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
            i, line_number = skip_spaces(unparsed_constant, i, line_number)
            if i < len(unparsed_constant):
                raise SyntaxError(f'Некорректный символ, строка {line_number}: {unparsed_constant[i]}.')
            if constant['value'][-1] == '.':
                constant['value'] = constant['value'][:-1]
        elif unparsed_constant[i] == '"':
            i += 1
            while i < len(unparsed_constant) and unparsed_constant[i] != '"':
                constant['value'] += unparsed_constant[i]
                i += 1
            if i >= len(unparsed_constant) or unparsed_constant[i] != '"':
                raise SyntaxError(f'Некорректный символ, строка {line_number}: {unparsed_constant[i]}.'
                                  + 'Ожидался символ \'"\'.')
            i += 1
            i, line_number = skip_spaces(unparsed_constant, i, line_number)
            if i < len(unparsed_constant):
                raise SyntaxError(f'Некорректный символ, строка {line_number}: {unparsed_constant[i]}.')
        else:
            raise SyntaxError(f'Некорректный символ, строка {line_number}: {unparsed_constant[i]}.')
    i, line_number = skip_spaces(unparsed_constant, i, line_number)
    if i < len(unparsed_constant):
        raise SyntaxError(f'Некорректный символ, строка {line_number}: {unparsed_constant[i]}.')
    if constant['value'] == '':
        raise RuntimeError(f"Константа не может быть объявлена без значения, строка { start_line_number }: "
                           + f"{ constant['name'] }.")
    return constant


def parse_block(unparsed_block, line_number):
    block = {
        'name': '',
        'description': 'Описание отсутствует.',
        'commands': []
    }
    i, line_number = skip_spaces(unparsed_block, 0, line_number)
    while i < len(unparsed_block):
        if unparsed_block[i].isalpha():
            word = unparsed_block[i]
            i += 1
            while i < len(unparsed_block) and unparsed_block[i].isalpha():
                word += unparsed_block[i]
                i += 1
            i, line_number = skip_spaces(unparsed_block, i, line_number)
            if i < len(unparsed_block) and unparsed_block[i] != ':':
                raise SyntaxError(f'Некорректный символ, строка { line_number }: { unparsed_block[i] }.'
                                  + 'Ожидался символ ":".')
            if i >= len(unparsed_block):
                raise SystemError(f'Ожидался символ ":", строка { line_number }.')
            i, line_number = skip_spaces(unparsed_block, i, line_number)
            if word == 'name':
                if i < len(unparsed_block) and unparsed_block[i] == '"':
                    i += 1
                    unparsed_name = ''
                    while i < len(unparsed_block) and unparsed_block[i] != '"':
                        unparsed_name += unparsed_block[i]
                        i += 1
                    if i >= len(unparsed_block) or unparsed_block[i] != '"':
                        raise SyntaxError(f'Ожидался символ \'"\', строка { line_number }.')
                if i < len(unparsed_block) and unparsed_block[i] != '"':
                    raise SyntaxError(f'Некорректный символ, строка {line_number}: {unparsed_block[i]}.'
                                      + 'Ожидался символ \'"\'.')
                if i >= len(unparsed_block) or unparsed_block[i] != '"':
                    raise SyntaxError(f'Ожидался символ \'"\', строка {line_number}.')
            elif word == 'description':
                pass
            elif word == 'commands':
                pass
            else:
                raise SystemError(f'Некорректное ключевое слово, строка { line_number }: { word }.')
            i, line_number = skip_spaces(unparsed_block, i, line_number)
            if i < len(unparsed_block) and unparsed_block[i] != ';':
                raise SyntaxError(f'Ожидался символ ";", строка { line_number }.')
            if i >= len(unparsed_block) and unparsed_block[-1] != ';':
                raise SyntaxError(f'Ожидался символ ";", строка {line_number}.')
        else:
            raise SyntaxError(f'Некорректный символ, строка {line_number}: {unparsed_block[i]}.')
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
            if i < len(source) and source[i] != ';':
                raise SyntaxError(f'Ожидался символ ";", строка { line_number }.')
            if i >= len(source) and source[i - 1] != ';':
                raise SyntaxError(f'Ожидался символ ";", строка {line_number}.')
            variable = parse_variable(unparsed_variable, start_line_number, is_entered)
            i += 1
            is_entered = True
            parsed_data['variables'].append(variable)


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
            if i < len(source) and source[i] != ';':
                raise SyntaxError(f'Ожидался символ ";", строка {line_number}.')
            if i >= len(source) and source[i - 1] != ';':
                raise SyntaxError(f'Ожидался символ ";", строка {line_number}.')
            constant = parse_constant(unparsed_constant, start_line_number)
            i += 1
            parsed_data['constants'].append(constant)


def parse_blocks_block(source, line_number, parsed_data):
    is_block_expected = False
    i, line_number = skip_spaces(source, 0, line_number)
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
            if i < len(source) and source[i] != ']':
                raise SyntaxError(f'Некорректный символ, строка {line_number}: {source[i]}.'
                                  + 'Ожидался символ "]".')
            if i >= len(source) and source[-1] != ']':
                raise SyntaxError(f'Некорректный символ, строка {line_number}: {source[-1]}.'
                                  + 'Ожидался символ "]".')
            i += 1
            block = parse_block(unparsed_block, start_line_number)
            parsed_data['blocks'].append(block)
        elif source[i] == ',':
            is_block_expected = True
            i += 1
        else:
            raise SyntaxError(f'Некорректный символ, строка { line_number }: { source[i] }.')
    if is_block_expected:
        raise RuntimeError(f'Ожидался исполняемый блок, строка { line_number }.')


def parse_keyword_block(keyword, source, line_number, parsed_data):
    if keyword == 'Variables':
        parse_variables_block(source, line_number, parsed_data)
    elif keyword == 'Constants':
        parse_constants_block(source, line_number, parsed_data)
    elif keyword == 'Blocks':
        parse_blocks_block(source, line_number, parsed_data)


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
                word = word + source[i]
                i += 1
            if is_keyword(word):
                i, line_number = skip_spaces(source, i, line_number)
                if source[i] != '{':
                    raise SyntaxError(f'Некорректный символ, строка {line_number}: {source[i]}.')
                else:
                    start_line_number = line_number
                    keyword_block = source[i]
                    i += 1
                    while i < len(source) and source[i] != '}':
                        keyword_block += source[i]
                        if source[i] == '\n':
                            line_number += 1
                        i += 1
                    keyword_block += source[i]
                    i += 1
                    parse_keyword_block(word, keyword_block[1:-1], start_line_number, parsed_data)
            else:
                raise SyntaxError(f'Обнаружено неключевое слово, строка {line_number}: {word}.')
        else:
            raise SyntaxError(f'Некорректный символ, строка {line_number}: {source[i]}.')
    return parsed_data
