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


if __name__ == "__main__":
    unittest.main()
