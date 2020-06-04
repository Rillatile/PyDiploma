import unittest
import parser
import executor


def parse_uncorrect_module_with_wrong_constant(*args, **kwargs):
    source = ('Variables {\n' +
              'a: "Тестовое описание." = 1;\n' +
              '!b;\n' +
              '}\n' +
              'Constants {\n' +
              'PI: "Число Пи.";\n' +
              '}\n' +
              'Blocks {\n' +
              '[\n' +
              'name: "Блок №1";\n' +
              'description: "Тестовый блок.";\n' +
              'commands: (\n' +
              'b = "a * 2";\n' +
              '"echo $PI";\n' +
              ')\n' +
              ']\n' +
              '}\n')
    data = parser.parse(source)


def parse_uncorrect_module_with_syntax_error(*args, **kwargs):
    source = ('Variables {\n' +
              'a: "Тестовое описание." = 1;\n' +
              '!b;\n' +
              '}\n' +
              'Constants {\n' +
              'PI: "Число Пи." = 3.14;\n' +
              'Blocks {\n' +
              '[\n' +
              'name: "Блок №1";\n' +
              'description: "Тестовый блок.";\n' +
              'commands: (\n' +
              'b = "a * 2";\n' +
              '"echo $PI";\n' +
              ')\n' +
              ']\n' +
              '}\n')
    data = parser.parse(source)


def parse_uncorrect_module_with_variable_that_already_exists(*args, **kwargs):
    source = ('Variables {\n' +
              'a: "Тестовое описание." = 1;\n' +
              '!b;\n' +
              'a;' +
              '}\n' +
              'Constants {\n' +
              'PI: "Число Пи." = 3.14;\n' +
              '}\n' +
              'Blocks {\n' +
              '[\n' +
              'name: "Блок №1";\n' +
              'description: "Тестовый блок.";\n' +
              'commands: (\n' +
              'b = "a * 2";\n' +
              '"echo $PI";\n' +
              ')\n' +
              ']\n' +
              '}\n')
    data = parser.parse(source)


def parse_uncorrect_module_with_constant_that_already_exists(*args, **kwargs):
    source = ('Variables {\n' +
              'a: "Тестовое описание." = 1;\n' +
              '!b;\n' +
              '}\n' +
              'Constants {\n' +
              'PI: "Число Пи." = 3.14;\n' +
              'a = 1;' +
              '}\n' +
              'Blocks {\n' +
              '[\n' +
              'name: "Блок №1";\n' +
              'description: "Тестовый блок.";\n' +
              'commands: (\n' +
              'b = "a * 2";\n' +
              '"echo $PI";\n' +
              ')\n' +
              ']\n' +
              '}\n')
    data = parser.parse(source)


def execute_uncorrect_module_with_result_variable_that_does_not_exists(*args, **kwargs):
    source = ('Variables {\n' +
              'a: "Тестовое описание." = 1;\n' +
              '!b;\n' +
              '}\n' +
              'Constants {\n' +
              'PI: "Число Пи." = 3.14;\n' +
              '}\n' +
              'Blocks {\n' +
              '[\n' +
              'name: "Блок №1";\n' +
              'description: "Тестовый блок.";\n' +
              'commands: (\n' +
              'c = "a * 2";\n' +
              '"echo $PI";\n' +
              ')\n' +
              ']\n' +
              '}\n')
    data = parser.parse(source)
    executor.execute(data, 0, None)


class TestParser(unittest.TestCase):
    def test_correct_module(self):
        source = ('Variables {\n' +
                  'a: "Тестовое описание." = 1;\n' +
                  '!b;\n' +
                  '}\n' +
                  'Constants {\n' +
                  'PI: "Число Пи." = 3.1415926;\n' +
                  '}\n' +
                  'Blocks {\n' +
                  '[\n' +
                  'name: "Блок №1";\n' +
                  'description: "Тестовый блок.";\n' +
                  'commands: (\n' +
                  'b = "a * 2";\n' +
                  '"echo $PI";\n' +
                  ')\n' +
                  ']\n' +
                  '}\n')
        data = parser.parse(source)
        expected_data = {
            'variables': [
                {
                    'name': 'a',
                    'description': 'Тестовое описание.',
                    'value': '1',
                    'is_entered': True
                },
                {
                    'name': 'b',
                    'description': 'Описание отсутствует.',
                    'value': '',
                    'is_entered': False
                }
            ],
            'constants': [
                {
                    'name': 'PI',
                    'description': 'Число Пи.',
                    'value': '3.1415926'
                }
            ],
            'blocks': [
                {
                    'name': 'Блок №1',
                    'description': 'Тестовый блок.',
                    'commands': [
                        {
                            'result_variable': 'b',
                            'command': 'a * 2',
                            'description': 'Описание отсутствует.'
                        },
                        {
                            'result_variable': '',
                            'command': 'echo $PI',
                            'description': 'Описание отсутствует.'
                        }
                    ]
                }
            ],
            'check': {
                'if': '',
                'good_message': 'Модуль выполнился успешно.',
                'bad_message': 'Выполнение модуля завершилось ошибкой.'
            }
        }
        self.assertEqual(data, expected_data, 'Результат парсинга отличается от ожидаемого.')

    def test_uncorrect_module_with_wrong_constant(self):
        self.assertRaises(RuntimeError, parse_uncorrect_module_with_wrong_constant,
                          'Модуль был корректно распарсен, хотя должно было быть выброшено исключение.')

    def test_uncorrect_module_with_syntax_error(self):
        self.assertRaises(SyntaxError, parse_uncorrect_module_with_syntax_error,
                          'Модуль был корректно распарсен, хотя должно было быть выброшено исключение.')

    def test_uncorrect_module_with_variable_that_already_exists(self):
        self.assertRaises(RuntimeError, parse_uncorrect_module_with_variable_that_already_exists,
                          'Модуль был корректно распарсен, хотя должно было быть выброшено исключение.')

    def test_uncorrect_module_with_constant_that_already_exists(self):
        self.assertRaises(RuntimeError, parse_uncorrect_module_with_constant_that_already_exists,
                          'Модуль был корректно распарсен, хотя должно было быть выброшено исключение.')

    def test_uncorrect_module_with_result_variable_that_does_not_exists(self):
        self.assertRaises(RuntimeError, execute_uncorrect_module_with_result_variable_that_does_not_exists,
                          'Модуль был корректно распарсен, хотя должно было быть выброшено исключение.')


if __name__ == '__main__':
    unittest.main()
