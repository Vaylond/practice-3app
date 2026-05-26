from abc import ABC, abstractmethod
import sys
import subprocess


if len(sys.argv) < 2 or sys.argv[1] != "external_window":
    # Вызываем новое окно cmd
    subprocess.Popen(
        ['start', 'cmd', '/k',
         sys.executable,
         sys.argv[0],
         'external_window'],
        shell=True
    )
    sys.exit() # Закрываем фоновый процесс в VS Code


class EncryptedText(ABC):
    def __init__(self, text, owner_name):
        self._text = text
        self._owner_name = owner_name

    def get_text(self):
        return self._text

    def get_owner_name(self):
        return self._owner_name

    @abstractmethod
    def encrypt(self):
        pass

    def __str__(self):
        return (
            f"Владелец: {self._owner_name} | "
            f"Оригинал: '{self._text}' | "
            f"Зашифровано: '{self.encrypt()}'"
        )


class SubstitutionCipher(EncryptedText):
    def __init__(self, text, owner_name, source_alphabet, replacement_alphabet):
        super().__init__(text, owner_name)
        self._source_alphabet = source_alphabet.lower()
        self._replacement_alphabet = replacement_alphabet.lower()

    def encrypt(self):
        res = ""
        for char in self._text:
            char_lower = char.lower()
            if char_lower in self._source_alphabet:
                idx = self._source_alphabet.index(char_lower)
                new_char = self._replacement_alphabet[idx]
                res += new_char.upper() if char.isupper() else new_char
            else:
                res += char
        return res

    def __str__(self):
        return f"[Шифр Замены] {super().__str__()}"


class ShiftCipher(EncryptedText):
    def __init__(self, text, owner_name, shift_step):
        super().__init__(text, owner_name)
        self._shift_step = shift_step

    def encrypt(self):
        res = ""
        for char in self._text:
            res += chr(ord(char) + self._shift_step)
        return res

    def __str__(self):
        return f"[Шифр Сдвига] {super().__str__()}"


class TextContainer(object):
    def __init__(self):
        self._items = []

    def add_object(self, item):
        self._items.append(item)
        print(f"-> Добавлен объект для владельца {item.get_owner_name()}")

    def remove_by_condition(self, condition):
        parts = condition.split()
        if len(parts) < 3:
            return

        field = parts[0].lower()
        operator = parts[1]
        value = parts[2].lower()

        new_items = []
        for item in self._items:
            keep = True
            if field == "владелец" and operator == "=":
                if item.get_owner_name().lower() == value:
                    keep = False
            elif field == "длина":
                length = int(value)
                if operator == "<" and len(item.get_text()) < length:
                    keep = False
                elif operator == ">" and len(item.get_text()) > length:
                    keep = False

            if keep:
                new_items.append(item)

        removed_count = len(self._items) - len(new_items)
        self._items = new_items
        print(f"-> Удалено объектов по условию '{condition}': {removed_count}")

    def print_all(self):
        print("\n===== СОДЕРЖИМОЕ КОНТЕЙНЕРА =====")
        if not self._items:
            print("[Контейнер пуст]")
        for idx, item in enumerate(self._items, 1):
            print(f"{idx}. {item}")
        print("==================================\n")


class CommandProcessor:
    def __init__(self, container):
        self._container = container

    def process_file(self, filename):
        print(f"Начало обработки файла: {filename}")
        try:
            with open(filename, "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        self.process_command(line)
        except FileNotFoundError:
            print(f"Ошибка: Файл {filename} не найден!")

    def process_command(self, command):
        parts = command.split()
        if not parts:
            return

        cmd_type = parts[0].upper()

        if cmd_type == "PRINT":
            self._container.print_all()

        elif cmd_type == "REM":
            if len(parts) < 4:
                print("Ошибка: Команда REM должна содержать условие!")
                return
            condition = " ".join(parts[1:])
            self._container.remove_by_condition(condition)

        elif cmd_type == "ADD":
            if len(parts) < 5:
                print("Ошибка: Недостаточно аргументов для ADD!")
                return

            cipher_type = parts[1].upper()
            text = parts[2]
            owner = parts[3]

            if cipher_type == "SUB":
                if len(parts) < 6:
                    print("Ошибка: Для шифра замены нужно указать два алфавита!")
                    return
                src_alphabet = parts[4]
                repl_alphabet = parts[5]
                obj = SubstitutionCipher(text, owner, src_alphabet, repl_alphabet)
                self._container.add_object(obj)

            elif cipher_type == "SHIFT":
                try:
                    shift_step = int(parts[4])
                    obj = ShiftCipher(text, owner, shift_step)
                    self._container.add_object(obj)
                except ValueError:
                    print(f"Ошибка: Шаг сдвига должен быть целым числом!")
            else:
                print(f"Ошибка: Неизвестный тип шифра '{cipher_type}'")
        else:
            print(f"Ошибка: Неизвестная команда '{cmd_type}'")


if __name__ == "__main__":
    container = TextContainer()
    processor = CommandProcessor(container)
    processor.process_file("commands.txt")

    print("\nНажмите Enter для выхода из программы...")
    input()
