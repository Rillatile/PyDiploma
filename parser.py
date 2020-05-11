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
    return variable


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
            if source[i] != ';':
                raise SyntaxError(f'Некорректный символ, строка {line_number}: {source[i]}.'
                                  + 'Ожидалась ";".')
            i += 1
            variable = parse_variable(unparsed_variable, start_line_number, is_entered)
            parsed_data['variables'].append(variable)


def parse_keyword_block(keyword, source, line_number, parsed_data):
    if keyword == 'Variables':
        parse_variables_block(source, line_number, parsed_data)
    elif keyword == 'Constants':
        pass
    elif keyword == 'Blocks':
        pass


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
