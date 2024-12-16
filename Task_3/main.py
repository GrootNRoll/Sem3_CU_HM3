import tomllib as toml
import re
import sys
import math



class ConfigParser:
    def __init__(self):
        self.constants = {}

    def parse(self, input_text):
        """Парсинг TOML-данных с удалением комментариев."""
        # Удаляем однострочные комментарии NB. и многострочные /# ... #/
        input_text = re.sub(r'NB\..*', '', input_text)  # Удаляем однострочные комментарии
        input_text = re.sub(r'/#.*?#/', '', input_text, flags=re.DOTALL)  # Удаляем многострочные комментарии
        try:
            data = toml.loads(input_text)
            return data
        except toml.TOMLDecodeError as e:
            sys.stderr.write(f"Ошибка парсинга TOML: {e}\n")
            sys.exit(1)

    def transform(self, data):
        """Трансформация данных TOML в учебный конфигурационный язык."""
        return self._transform_element(data)

    def _transform_element(self, element):
        if isinstance(element, dict):
            return self._transform_dict(element)
        elif isinstance(element, list):
            return f"[{', '.join(self._transform_element(e) for e in element)}]"
        elif isinstance(element, str):
            return f"'{element}'"
        elif isinstance(element, (int, float)):
            return str(element)
        else:
            raise ValueError(f"Неподдерживаемый тип данных: {type(element)}")

    def _transform_dict(self, dictionary):
        items = []
        for key, value in dictionary.items():
            if not re.match(r"^[a-zA-Z][a-zA-Z0-9]*$", key):
                raise ValueError(f"Некорректное имя ключа: {key}")
            items.append(f"{key} : {self._transform_element(value)}")
        return f"([\n  {',\n  '.join(items)}\n])"

    def compute_constant(self, expression):
        """Вычисление выражений в префиксной форме."""
        tokens = expression.strip('{}!').split()
        operator = tokens[0]
        operands = [self.constants.get(t, float(t) if t.isdigit() else t) for t in tokens[1:]]

        if operator == '+':
            return sum(operands)
        elif operator == '-':
            return operands[0] - operands[1]
        elif operator == '*':
            return math.prod(operands)
        elif operator == '/':
            return operands[0] / operands[1]
        elif operator == 'sqrt':
            return math.sqrt(operands[0])
        elif operator == 'print':
            print(*operands)
            return operands[0]
        else:
            raise ValueError(f"Неизвестная операция: {operator}")

    def process_constants(self, data):
        """Обработка объявлений констант."""
        for key, value in data.items():
            if isinstance(value, str) and value.startswith('!{'):
                self.constants[key] = self.compute_constant(value)
            else:
                self.constants[key] = value

if __name__ == "__main__":
    input_text = sys.stdin.read()
    parser = ConfigParser()

    # Парсинг TOML
    toml_data = parser.parse(input_text)

    # Обработка констант
    parser.process_constants(toml_data)

    # Трансформация в целевой язык
    try:
        result = parser.transform(toml_data)
        print(result)
    except Exception as e:
        sys.stderr.write(f"Ошибка трансформации: {e}\n")
        sys.exit(1)
