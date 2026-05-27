import pytest
from maletin import SubstitutionCipher, ShiftCipher, TextContainer, CommandProcessor

class TestCiphers:
    """Тестирование классов шифрования"""

    def test_substitution_cipher_success(self):
        """Проверка шифра замены"""
        cipher = SubstitutionCipher("abc", "Влад", "abc", "xyz")
        assert cipher.encrypt() == "xyz"

    def test_substitution_cipher_case(self):
        """Проверка сохранения регистра при замене"""
        cipher = SubstitutionCipher("AbC", "Влад", "abc", "xyz")
        assert cipher.encrypt() == "XyZ"

    def test_shift_cipher_success(self):
        """Проверка шифра сдвига"""
        cipher = ShiftCipher("abc", "Анна", 1)
        assert cipher.encrypt() == "bcd"

    def test_shift_cipher_bad_type(self):
        """Исключительная ситуация: неверный тип данных для сдвига"""
        cipher = ShiftCipher("abc", "Анна", "один")
        with pytest.raises(TypeError):
            cipher.encrypt()


class TestTextContainer:
    """Тестирование контейнера (добавление и удаление)"""

    @pytest.fixture(autouse=True)
    def setup_container(self):
        self.container = TextContainer()

    def test_add_object(self):
        """Проверка добавления"""
        cipher = ShiftCipher("text", "owner", 1)
        self.container.add_object(cipher)
        assert len(self.container._items) == 1

    def test_remove_by_owner(self):
        """Проверка удаления по владельцу"""
        self.container.add_object(ShiftCipher("t1", "Владимир", 1))
        self.container.add_object(ShiftCipher("t2", "Анна", 1))
        self.container.remove_by_condition("владелец = владимир")
        
        assert len(self.container._items) == 1
        assert self.container._items[0].get_owner_name() == "Анна"

    def test_remove_by_length(self):
        """Проверка удаления по длине"""
        self.container.add_object(ShiftCipher("123", "o1", 1))
        self.container.add_object(ShiftCipher("12345", "o2", 1))
        self.container.remove_by_condition("длина < 4")
        
        assert len(self.container._items) == 1
        assert self.container._items[0].get_text() == "12345"

    def test_remove_bad_condition(self):
        """Проверка некорректного условия удаления"""
        self.container.add_object(ShiftCipher("123", "o1", 1))
        self.container.remove_by_condition("владелец =")
        assert len(self.container._items) == 1


class TestCommandProcessor:
    """Тестирование обработчика команд"""

    @pytest.fixture(autouse=True)
    def setup_processor(self):
        self.container = TextContainer()
        self.processor = CommandProcessor(self.container)

    def test_process_add_sub(self):
        """Проверка добавления через команду ADD SUB"""
        self.processor.process_command("ADD SUB abc Влад abc xyz")
        assert len(self.container._items) == 1
        assert isinstance(self.container._items[0], SubstitutionCipher)

    def test_process_add_sub_missing_alphabets(self, capsys):
        """Исключительная ситуация: для SUB не хватает второго алфавита"""
        self.processor.process_command("ADD SUB abc Влад один_алфавит")
        captured = capsys.readouterr()
        assert "нужно указать два алфавита" in captured.out

    def test_process_add_shift_value_error(self, capsys):
        """Исключительная ситуация: вместо числа для сдвига передана строка"""
        self.processor.process_command("ADD SHIFT Hello Влад три")
        captured = capsys.readouterr()
        assert "Шаг сдвига должен быть целым числом" in captured.out
        assert len(self.container._items) == 0

    def test_process_unknown_command(self, capsys):
        """Проверка неизвестной команды"""
        self.processor.process_command("MAGIC_COMMAND data")
        captured = capsys.readouterr()
        assert "Неизвестная команда" in captured.out


class TestIntegration:
    """Интеграционные тесты (проверка работы всей системы)"""

    def test_full_scenario(self):
        """Успешный тест: полный сценарий работы"""
        container = TextContainer()
        processor = CommandProcessor(container)

        processor.process_command("ADD SHIFT message Алиса 5")
        processor.process_command("ADD SUB abc Боб abc xyz")
        processor.process_command("ADD SHIFT secret Алиса 2")

        assert len(container._items) == 3

        assert container._items[0].encrypt() == "rjxxflj"  # message +5
        assert container._items[1].encrypt() == "xyz"      # abc заменой


def test_cipher_performance_benchmark(benchmark):
    """Тест производительности: шифрование длинной строки 1000 раз"""
    # Создаем длинный текст (13000 символов)
    large_text = "Hello World! " * 1000
    cipher = ShiftCipher(large_text, "BenchmarkUser", 3)
    
    # Запускаем бенчмарк для метода encrypt
    result = benchmark(cipher.encrypt)
    assert len(result) == len(large_text)