# Эмулятор Командной Оболочки ОС

## Общее описание

**Эмулятор Командной Оболочки ОС** — это программное обеспечение, разработанное на языке Python, которое имитирует функциональность командной оболочки UNIX-подобной операционной системы. Цель проекта — предоставить пользователю возможность взаимодействовать с виртуальной файловой системой через удобный интерфейс командной строки (CLI), максимально приближенный к реальному сеансу работы с shell в UNIX-среде.**

**Эмулятор запускается из реальной командной строки и использует ZIP-архив в качестве образа виртуальной файловой системы, что позволяет работать с файлами и директориями без необходимости их распаковки. Все действия пользователя логируются в XML-файл, содержащий информацию о выполненных командах, их выводе, пользователе и времени выполнения.**

## Основные возможности

- **Работа в режиме CLI:** Пользователь взаимодействует с эмулятором через командную строку, вводя команды и получая соответствующий вывод.
- **Виртуальная файловая система:** Использование ZIP-архива как образа файловой системы позволяет работать с файлами и директориями без необходимости их распаковки.
- **Поддержка базового набора команд:**
  - `ls` — вывод списка файлов и каталогов.
  - `cd` — смена текущего каталога.
  - `exit` — выход из эмулятора.
- **Дополнительные команды:**
  - `uname` — отображение имени операционной системы.
  - `uniq` — вывод уникальных строк из файла или ввода.
- **Логирование действий:** Все команды и их результаты записываются в XML-файл, что позволяет отслеживать действия пользователя во время сеанса работы с эмулятором.
- **Тестирование:** Все функции эмулятора покрыты автоматическими тестами, обеспечивающими надежность и корректность работы.


### Эмулятор использует ZIP-архив в качестве образа виртуальной файловой системы. Для его создания нужны следующие шаги: 
Создадим структуру файла: 
mkdir -p test_filesystem/dir1
echo "line1" > test_filesystem/file1.txt
echo "line1" >> test_filesystem/file1.txt
echo "line2" >> test_filesystem/file1.txt
echo "line2" >> test_filesystem/file1.txt
echo "line3" >> test_filesystem/file1.txt
echo "subfile content" > test_filesystem/dir1/subfile.txt


Упакуем директорию в ZIP-архив:
```zip -r test_filesystem.zip test_filesystem```

Проверим содержимое ZIP-архива:
```unzip -l test_filesystem.zip```
Ожидаемый вывод будет:

    Length    Date   Time     Name
 ---------  ---------- -----   ----
        0  12-10-2024 09:37   test_filesystem/
       30  12-10-2024 09:37   test_filesystem/file1.txt
        0  12-10-2024 09:37   test_filesystem/subdir/
       16  12-10-2024 09:37   test_filesystem/subdir/subfile.txt
       18  12-10-2024 09:37   test_filesystem/example.txt
        0  12-10-2024 09:37   test_filesystem/dir1/
       16  12-10-2024 09:37   test_filesystem/dir1/subfile.txt

 ---------                     -------


Проверим лог-файл:
После завершения откроем log.xml для просмотра записанных действий:
```cat log.xml```

````
<?xml version='1.0'encoding='utf-8'?>
<log><entry><user>user1</user><command>ls</command><output>test_filesystem</output><time>2024-12-10T16:41:19.113503</time></entry><entry><user>user1</user><command>cd test_filesystem</command><output /><time>2024-12-10T16:41:29.261719</time></entry><entry><user>user1</user><command>ls</command><output>file1.txt
subdir
example.txt
dir1</output><time>2024-12-10T16:41:30.431261</time></entry><entry><user>user1</user><command>uniq file1.txt</command><output>line1
line2
line3</output><time>2024-12-10T16:41:39.254912</time></entry><entry><user>user1</user><command>uname</command><output>Linux</output><time>2024-12-10T16:41:46.392775</time></entry><entry><user>user1</user><command>exit</command><output>Выход...</output><time>2024-12-10T16:41:49.229799</time></entry></log>%
````

# Реализация классов и их функций
# Класс VirtualFileSystem
Отвечает за взаимодействие с виртуальной файловой системой, основанной на ZIP-архиве.

## __init__(self, zip_path)
Инициализирует виртуальную файловую систему.
````
def __init__(self, zip_path):
    if not zipfile.is_zipfile(zip_path):
        print(f"Ошибка: Файл {zip_path} не является корректным ZIP-архивом.")
        sys.exit(1)
    self.temp_dir = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(self.temp_dir)
    except zipfile.BadZipFile:
        print(f"Ошибка: Не удалось распаковать ZIP-архив {zip_path}.")
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        sys.exit(1)
    self.current_dir = self.temp_dir
````
Проверяет, является ли указанный файл корректным ZIP-архивом.
Создаёт временную директорию для распаковки архива.
Распаковывает содержимое ZIP-архива во временную директорию.
Устанавливает текущую директорию на временную директорию.
## list_dir(self)
Возвращает список файлов и директорий в текущей директории.

````
def list_dir(self):
    try:
        return os.listdir(self.current_dir)
    except FileNotFoundError:
        return []
````
Возвращает список файлов и директорий в текущей директории.
В случае ошибки возвращает пустой список.
## change_dir(self, path)
Изменяет текущую директорию на указанную.

````
def change_dir(self, path):
    new_path = os.path.join(self.current_dir, path)
    new_path = os.path.normpath(new_path)
    # Проверка, что новый путь находится внутри temp_dir
    if os.path.commonpath([new_path, self.temp_dir]) != self.temp_dir:
        return False
    if os.path.isdir(new_path):
        self.current_dir = new_path
        return True
    else:
        return False
````
Изменяет текущую директорию на указанную.
Проверяет, что новая директория находится внутри временной директории, предотвращая выход за её пределы.
Возвращает True при успешном изменении директории, иначе False.
## get_current_dir(self)
Возвращает относительный путь текущей директории относительно корневой директории виртуальной файловой системы.

````
def get_current_dir(self):
    rel_path = os.path.relpath(self.current_dir, self.temp_dir)
    if rel_path == ".":
        return "/"
    else:
        return "/" + rel_path.replace("\\", "/")
````
Возвращает относительный путь текущей директории.
Если текущая директория — корневая, возвращает /.
## read_file(self, filename)
Читает содержимое указанного файла.

````
def read_file(self, filename):
    fpath = os.path.join(self.current_dir, filename)
    if os.path.isfile(fpath):
        try:
            with open(fpath, 'r') as f:
                return f.read().splitlines()
        except Exception as e:
            return [f"Ошибка чтения файла: {e}"]
    return [f"Файл не найден: {filename}"]
````
Читает содержимое указанного файла.
Возвращает список строк файла или сообщение об ошибке, если файл не найден.
## cleanup(self)
Удаляет временную директорию, очищая ресурсы после завершения работы с файловой системой.

````
def cleanup(self):
    shutil.rmtree(self.temp_dir, ignore_errors=True)
Описание:
Удаляет временную директорию.
Использует shutil.rmtree для удаления директорий и файлов.
Класс XMLLogger
Отвечает за логирование действий пользователя в XML-файл.
````
## __init__(self, log_path, user)
Инициализирует логгер.

````
def __init__(self, log_path, user):
    self.log_path = log_path
    self.user = user
    self.root = ET.Element("log")
    self.tree = ET.ElementTree(self.root)
````


Устанавливает путь к лог-файлу и имя пользователя.
Создаёт корневой элемент XML для записи логов.
## log(self, command, output)
Добавляет запись о выполненной команде.

````
def log(self, command, output):
    entry = ET.SubElement(self.root, "entry")
    user_el = ET.SubElement(entry, "user")
    user_el.text = self.user
    cmd_el = ET.SubElement(entry, "command")
    cmd_el.text = command
    out_el = ET.SubElement(entry, "output")
    out_el.text = output
    time_el = ET.SubElement(entry, "time")
    time_el.text = datetime.now().isoformat()
````

Добавляет запись о выполненной команде, её выводе, пользователе и времени выполнения.
Использует xml.etree.ElementTree для создания элементов XML.
## save(self)
Сохраняет лог-файл.

````
def save(self):
    self.tree.write(self.log_path, encoding='utf-8', xml_declaration=True)
````
Записывает все собранные записи в XML-файл логов.
Указывает кодировку и декларацию XML.
Командные функции
## command_uname()
Возвращает название операционной системы.

````
def command_uname():
    return "Linux"
````
Простая функция, которая возвращает строку "Linux".
Используется для имитации вывода команды uname.
## command_uniq(lines)
Возвращает уникальные строки из списка.

````
def command_uniq(lines):
    if not lines:
        return ""
    unique_lines = [lines[0]]
    for line in lines[1:]:
        if line != unique_lines[-1]:
            unique_lines.append(line)
    return "\n".join(unique_lines)
````
Принимает список строк lines.
Возвращает строки без последовательных дубликатов, объединённые через перенос строки.
Если список пуст, возвращает пустую строку.
## Основная функция main()
Управляет основным циклом эмулятора и обработкой команд.

````
def main():
    if len(sys.argv) != 5:
        print("Usage: python emulator.py <username> <hostname> <zip_path> <log_path>")
        sys.exit(1)

    username = sys.argv[1]
    hostname = sys.argv[2]
    zip_path = sys.argv[3]
    log_path = sys.argv[4]

    vfs = VirtualFileSystem(zip_path)
    logger = XMLLogger(log_path, username)

    try:
        while True:
            prompt = f"{username}@{hostname}:{vfs.get_current_dir()}$ "
            try:
                command_line = input(prompt).strip()
            except EOFError:
                # Обработка EOF (например, Ctrl+D)
                print("\nExiting...")
                logger.log("exit", "Exiting via EOF")
                logger.save()
                break
            except KeyboardInterrupt:
                # Обработка прерывания (например, Ctrl+C)
                print("\nExiting on KeyboardInterrupt")
                logger.log("exit", "Exiting via KeyboardInterrupt")
                logger.save()
                break

            if not command_line:
                continue

            parts = command_line.split()
            cmd = parts[0]
            args = parts[1:]

            output = ""
            if cmd == "ls":
                contents = vfs.list_dir()
                output = "\n".join(contents)
                print(output)
            elif cmd == "cd":
                if len(args) != 1:
                    output = "cd требует один аргумент"
                    print(output)
                else:
                    if vfs.change_dir(args[0]):
                        output = ""
                    else:
                        output = f"Нет такой директории: {args[0]}"
                        print(output)
            elif cmd == "uname":
                output = command_uname()
                print(output)
            elif cmd == "uniq":
                if len(args) == 1:
                    file_content = vfs.read_file(args[0])
                    if file_content and not file_content[0].startswith("Файл не найден"):
                        output = command_uniq(file_content)
                        print(output)
                    else:
                        output = f"Файл не найден: {args[0]}"
                        print(output)
                else:
                    print("Введите ввод (Ctrl+D для завершения):")
                    lines = []
                    try:
                        while True:
                            line = input()
                            lines.append(line)
                    except EOFError:
                        pass
                    output = command_uniq(lines)
                    print(output)
            elif cmd == "exit":
                output = "Выход..."
                print(output)
                logger.log(command_line, output)
                logger.save()
                break
            else:
                output = f"Команда не найдена: {cmd}"
                print(output)

            logger.log(command_line, output)
    finally:
        vfs.cleanup()
````
Проверяет количество аргументов командной строки. Ожидается 4 аргумента: username, hostname, zip_path, log_path.
Инициализирует виртуальную файловую систему и логгер.
Запускает основной цикл, в котором:
Отображает приглашение к вводу.
Принимает команду от пользователя.
Обрабатывает команды ls, cd, uname, uniq, exit.
Логирует каждую команду и её вывод.
Обрабатывает сигналы EOF (например, Ctrl+D) и прерывания (Ctrl+C) для корректного завершения сеанса.
В блоке finally очищает временную файловую систему.
# Тестирование
Все функции эмулятора покрыты автоматическими тестами, которые обеспечивают корректность работы поддерживаемых команд и функционала виртуальной файловой системы.

## Запуск тестов
Нужно проверить что мы в корневой директории проекта и активировали виртуальное окружение:
```
cd konfig_1
source .venv/bin/activate
```
```python -m unittest discover tests```
Ожидаемый результат:
````
..............
----------------------------------------------------------------------
Ran 14 tests in 0.025s
OK
````
##Описание тестов
Пример тестов для команды uname:

````
def test_uname_command_output(self):
    self.assertEqual(command_uname(), "Linux")
````
````
def test_uname_command_type(self):
    self.assertIsInstance(command_uname(), str)
````
Пример тестов для команды uniq:

````
def test_uniq_command_basic(self):
    lines = ["a", "a", "b", "b", "c"]
    result = command_uniq(lines)
    self.assertEqual(result, "a\nb\nc")
````
````
def test_uniq_command_empty(self):
    lines = []
    result = command_uniq(lines)
    self.assertEqual(result, "")
````
## Пример файла тестов
````
import unittest
import os
import shutil
import tempfile
import zipfile
from emulator import VirtualFileSystem, command_uname, command_uniq


class TestCommands(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Создаём временный ZIP-архив для тестов
        cls.test_dir = tempfile.mkdtemp()

        # Создаём поддиректорию dir1
        dir1_path = os.path.join(cls.test_dir, "dir1")
        os.mkdir(dir1_path)

        # Создаём файл file1.txt
        file1_path = os.path.join(cls.test_dir, "file1.txt")
        with open(file1_path, 'w') as f:
            f.write("line1\nline1\nline2\nline2\nline3\n")

        # Создаём файл subfile.txt внутри dir1
        subfile_path = os.path.join(dir1_path, "subfile.txt")
        with open(subfile_path, 'w') as f:
            f.write("subfile content\n")

        # Создаём ZIP-архив и добавляем файлы
        cls.zip_path = os.path.join(cls.test_dir, "fs.zip")
        with zipfile.ZipFile(cls.zip_path, 'w') as z:
            z.write(file1_path, "file1.txt")
            z.write(dir1_path, "dir1/")
            z.write(subfile_path, "dir1/subfile.txt")  # Добавляем subfile.txt

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.test_dir, ignore_errors=True)

    # Тесты для команды uname
    def test_uname_command_output(self):
        self.assertEqual(command_uname(), "Linux")

    def test_uname_command_type(self):
        self.assertIsInstance(command_uname(), str)

    # Тесты для команды uniq
    def test_uniq_command_basic(self):
        lines = ["a", "a", "b", "b", "c"]
        result = command_uniq(lines)
        self.assertEqual(result, "a\nb\nc")

    def test_uniq_command_empty(self):
        lines = []
        result = command_uniq(lines)
        self.assertEqual(result, "")

    def test_uniq_command_single_line(self):
        lines = ["unique"]
        result = command_uniq(lines)
        self.assertEqual(result, "unique")

    def test_uniq_command_no_duplicates(self):
        lines = ["a", "b", "c"]
        result = command_uniq(lines)
        self.assertEqual(result, "a\nb\nc")

    # Тесты для VirtualFileSystem
    def test_vfs_list_dir(self):
        vfs = VirtualFileSystem(self.zip_path)
        contents = vfs.list_dir()
        self.assertIn("file1.txt", contents)
        self.assertIn("dir1", contents)
        vfs.cleanup()

    def test_vfs_change_dir_valid(self):
        vfs = VirtualFileSystem(self.zip_path)
        result = vfs.change_dir("dir1")
        self.assertTrue(result)
        self.assertEqual(vfs.get_current_dir(), "/dir1")
        vfs.cleanup()

    def test_vfs_change_dir_invalid(self):
        vfs = VirtualFileSystem(self.zip_path)
        result = vfs.change_dir("nonexistent")
        self.assertFalse(result)
        vfs.cleanup()

    def test_vfs_get_current_dir_root(self):
        vfs = VirtualFileSystem(self.zip_path)
        self.assertEqual(vfs.get_current_dir(), "/")
        vfs.cleanup()

    def test_vfs_get_current_dir_subdir(self):
        vfs = VirtualFileSystem(self.zip_path)
        vfs.change_dir("dir1")
        self.assertEqual(vfs.get_current_dir(), "/dir1")
        vfs.cleanup()

    def test_vfs_read_file_exists(self):
        vfs = VirtualFileSystem(self.zip_path)
        content = vfs.read_file("file1.txt")
        expected = ["line1", "line1", "line2", "line2", "line3"]
        self.assertEqual(content, expected)
        vfs.cleanup()

    def test_vfs_read_file_not_exists(self):
        vfs = VirtualFileSystem(self.zip_path)
        content = vfs.read_file("nonexistent.txt")
        self.assertEqual(content, [f"Файл не найден: nonexistent.txt"])
        vfs.cleanup()

    def test_vfs_read_file_in_subdir(self):
        vfs = VirtualFileSystem(self.zip_path)
        vfs.change_dir("dir1")
        content = vfs.read_file("subfile.txt")
        self.assertEqual(content, ["subfile content"])
        vfs.cleanup()


class TestShellEmulatorCommands(unittest.TestCase):
    def setUp(self):
        self.zip_path = 'test_fs.zip'
        self.log_path = 'test_log.xml'
        # Создаём тестовый zip-файл
        with zipfile.ZipFile(self.zip_path, 'w') as zf:
            zf.writestr('file1.txt', 'line1\nline1\nline2\nline2\nline3\n')
            zf.writestr('dir1/subfile.txt', 'subfile content\n')
        
        self.username = 'testuser'
        self.hostname = 'testhost'

    def tearDown(self):
        # Удаляем созданные файлы
        if os.path.exists(self.zip_path):
            os.remove(self.zip_path)
        if os.path.exists(self.log_path):
            os.remove(self.log_path)

    def run_emulator_command(self, command):
        # Перенаправляем stdin и stdout
        original_stdin = sys.stdin
        original_stdout = sys.stdout
        sys.stdin = StringIO(command + '\nexit\n')
        sys.stdout = StringIO()
        try:
            import emulator
            emulator.main()
            output = sys.stdout.getvalue()
        finally:
            sys.stdin = original_stdin
            sys.stdout = original_stdout
        return output

    def test_ls_command(self):
        output = self.run_emulator_command('ls')
        self.assertIn('dir1', output)
        self.assertIn('file1.txt', output)

    def test_cd_command_valid(self):
        # Тест смены директории на существующую
        output = self.run_emulator_command('cd dir1')
        self.assertIn('/dir1$', output)

    def test_cd_command_invalid(self):
        # Тест смены директории на несуществующую
        output = self.run_emulator_command('cd nonexistent')
        self.assertIn('Нет такой директории: nonexistent', output)

    def test_uname_command(self):
        output = self.run_emulator_command('uname')
        self.assertIn('Linux', output)

    def test_uniq_command_file_exists(self):
        output = self.run_emulator_command('uniq file1.txt')
        self.assertIn('line1', output)
        self.assertIn('line2', output)
        self.assertIn('line3', output)

    def test_uniq_command_file_not_exists(self):
        output = self.run_emulator_command('uniq nonexistent.txt')
        self.assertIn('Файл не найден: nonexistent.txt', output)

    def test_exit_command(self):
        output = self.run_emulator_command('exit')
        self.assertIn('Выход...', output)

    def test_log_file_creation(self):
        self.run_emulator_command('ls')
        self.assertTrue(os.path.exists(self.log_path))
        with open(self.log_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('<user>testuser</user>', content)
            self.assertIn('<command>ls</command>', content)


if __name__ == "__main__":
    unittest.main()
````
# Детальное описание функциональности
## Класс VirtualFileSystem
Управление виртуальной файловой системой, основанной на ZIP-архиве.

Методы:
```__init__(self, zip_path)```

Инициализация виртуальной файловой системы. Проверяет, является ли указанный файл ZIP-архивом. Создаёт временную директорию для распаковки архива.
Распаковывает содержимое ZIP-архива во временную директорию.

```list_dir(self)```

Получение списка файлов и директорий в текущей директории. Возвращает список содержимого текущей директории.
Реализация команды ls для отображения содержимого каталога.
```change_dir(self, path)```

Изменение текущей директории. Проверяет, существует ли указанная директория.
Изменяет текущую директорию на новую, если она существует и находится внутри временной директории.
```get_current_dir(self)```

Получение относительного пути текущей директории.
Возвращает путь текущей директории относительно корневой директории виртуальной файловой системы.
```read_file(self, filename)```

Открывает и читает содержимое указанного файла.
Возвращает список строк файла или сообщение об ошибке, если файл не найден.
Реализация команды uniq для чтения и обработки файлов.
```cleanup(self)```

Очистка временной директории. Удаляет временную директорию, очищая ресурсы после завершения работы с файловой системой.
Освобождение ресурсов и предотвращение накопления временных файлов.
## Класс XMLLogger
Логирование действий пользователя в XML-файл.

Методы:
```__init__(self, log_path, user)```

Инициализация логгера. Устанавливает путь к лог-файлу и имя пользователя.
Создаёт корневой элемент XML для записи логов.

```log(self, command, output)```

Запись команды и её вывода в лог. Добавляет новую запись о выполненной команде, её выводе, пользователе и времени выполнения.

```save(self)```

Сохранение лог-файла. Записывает все собранные записи в XML-файл логов.

## Функции команд
```command_uname()```

Имитация команды uname. Возвращает строку "Linux".
Реализация базовой команды для отображения имени операционной системы.
```command_uniq(lines)```

Имитация команды uniq. Принимает список строк и возвращает строки без последовательных дубликатов.
Если список пуст, возвращает пустую строку.

## Функция main()
Управление основным циклом эмулятора и обработкой пользовательских команд.

### Шаги:
Проверка аргументов командной строки:

Ожидается 4 аргумента: username, hostname, zip_path, log_path.
Если количество аргументов неверно, выводится сообщение об использовании и эмулятор завершается.
Инициализация компонентов:

Создаётся экземпляр VirtualFileSystem с указанным путем к ZIP-архиву.
Создаётся экземпляр XMLLogger с указанным путем к лог-файлу и именем пользователя.
Основной цикл:

Отображает приглашение к вводу, включающее имя пользователя, хост и текущую директорию.
Принимает команду от пользователя.
**Обрабатывает команды:**
````
ls: выводит содержимое текущей директории.
cd <каталог>: изменяет текущую директорию.
uname: выводит название операционной системы.
uniq <файл>: выводит уникальные строки из указанного файла или из ввода.
exit: завершает работу эмулятора.
Неизвестные команды: выводит сообщение об ошибке.
Логирует каждую выполненную команду и её вывод.
Обрабатывает сигналы EOF (Ctrl+D) и прерывания (Ctrl+C) для корректного завершения сеанса.
В блоке finally выполняет очистку временной файловой системы.
````

# Команды для сборки проекта
## 1.Установка зависимостей:
Эмулятор использует стандартные библиотеки Python и не требует установки дополнительных пакетов.

## 2.Запуск тестов:
```python -m unittest discover tests```

# Примеры использования
## Запуск эмулятора
```python emulator.py user1 myhost test_filesystem.zip log.xml```

## Пример сеанса работы:

### С помощью ручного ввода рассмотрим как работают команды в эмуляторе
![image](https://github.com/user-attachments/assets/1e1b5a57-dc2a-4f31-b60e-95b3cc605bc1)
**В результате видим во время прогна всех необходимых команд в одной сессии, все они корректно выполняют свою работу**
