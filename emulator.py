import sys
import os
import zipfile
import tempfile
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime

class VirtualFileSystem:
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

    def list_dir(self):
        try:
            return os.listdir(self.current_dir)
        except FileNotFoundError:
            return []

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

    def get_current_dir(self):
        rel_path = os.path.relpath(self.current_dir, self.temp_dir)
        if rel_path == ".":
            return "/"
        else:
            return "/" + rel_path.replace("\\", "/")

    def read_file(self, filename):
        fpath = os.path.join(self.current_dir, filename)
        if os.path.isfile(fpath):
            try:
                with open(fpath, 'r') as f:
                    return f.read().splitlines()
            except Exception as e:
                return [f"Ошибка чтения файла: {e}"]
        return [f"Файл не найден: {filename}"]

    def cleanup(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

class XMLLogger:
    def __init__(self, log_path, user):
        self.log_path = log_path
        self.user = user
        self.root = ET.Element("log")
        self.tree = ET.ElementTree(self.root)

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

    def save(self):
        self.tree.write(self.log_path, encoding='utf-8', xml_declaration=True)

def command_uname():
    return "Linux"

def command_uniq(lines):
    if not lines:
        return ""
    unique_lines = [lines[0]]
    for line in lines[1:]:
        if line != unique_lines[-1]:
            unique_lines.append(line)
    return "\n".join(unique_lines)

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

if __name__ == "__main__":
    main()
