import base64
from datetime import datetime
import os
import zipfile


class VirtualFileSystem:
    """Виртуальная файловая система на основе ZIP-архива"""

    def __init__(self, vfs_path=None):
        """Инициализация VFS: загружает из архива или создает по умолчанию"""
        self.vfs_path = vfs_path
        self.filesystem = {}
        self.current_vfs_dir = "/"

        if vfs_path and os.path.exists(vfs_path):
            self.load_vfs(vfs_path)
        else:
            # Создаем минимальную VFS по умолчанию
            self.filesystem = {
                "/": {
                    "type": "directory",
                    "content": {
                        "home": {
                            "type": "directory",
                            "content": {
                                "text.txt": {
                                    "type": "file",
                                    "content": "Текст файла",
                                    "created": datetime.now().isoformat(),
                                    "modified": datetime.now().isoformat()
                                }
                            },
                        },
                        "tmp": {"type": "directory", "content": {}},
                        "readme.txt": {
                            "type": "file",
                            "content": "Добро пожаловать в VFS!",
                            "created": datetime.now().isoformat(),
                            "modified": datetime.now().isoformat()
                        }
                    }
                }
            }

    def load_vfs(self, vfs_path):
        """Загружает структуру VFS из ZIP-архива в память"""
        try:
            if not zipfile.is_zipfile(vfs_path):
                raise ValueError("Файл не является ZIP-архивом")

            with zipfile.ZipFile(vfs_path, 'r') as zip_ref:
                self.filesystem = {"/": {"type": "directory", "content": {}}}

                for file_info in zip_ref.filelist:
                    path_parts = file_info.filename.split('/')
                    current_dir = self.filesystem["/"]["content"]

                    # Строим структуру директорий
                    for i, part in enumerate(path_parts):
                        if i == len(path_parts) - 1:  # Файл
                            if part:  # Не пустое имя файла
                                with zip_ref.open(file_info.filename) as f:
                                    content = f.read()
                                    # Пытаемся декодировать как текст, иначе оставляем бинарным
                                    try:
                                        content = content.decode('utf-8')
                                    except UnicodeDecodeError:
                                        content = base64.b64encode(content).decode('utf-8')

                                current_dir[part] = {
                                    "type": "file",
                                    "content": content,
                                    "created": datetime.now().isoformat(),
                                    "modified": datetime.now().isoformat()
                                }
                        else:  # Директория
                            if part not in current_dir:
                                current_dir[part] = {
                                    "type": "directory",
                                    "content": {}
                                }
                            current_dir = current_dir[part]["content"]

                print(f"VFS успешно загружена из {vfs_path}")

        except Exception as e:
            print(f"Ошибка загрузки VFS: {e}")
            # Создаем минимальную VFS при ошибке
            self.filesystem = {
                "/": {
                    "type": "directory",
                    "content": {
                        "error.txt": {
                            "type": "file",
                            "content": f"Ошибка загрузки VFS: {e}",
                            "created": datetime.now().isoformat(),
                            "modified": datetime.now().isoformat()
                        }
                    }
                }
            }

    def resolve_path(self, path):
        """Преобразует путь в указатель на содержимое директории в VFS"""
        path = os.path.normpath(path).replace('\\', '/')
        if path.startswith("/"):
            current_dir = self.filesystem["/"]["content"]
            path_parts = path[1:].split("/")
        else:
            current_dir = self.get_current_dir_content()
            path_parts = path.split("/")

        if ".." in os.path.normpath(os.path.join(self.current_vfs_dir, path)):  # Проверка на выход из корнивой директории
            print('Путь выходит за пределы корневой директории')
            return None

        for part in path_parts:
            if not part or part == ".":
                continue
            elif ".." in part and path.count('.') == len(path):
                current_vfs_dir = self.current_vfs_dir
                for step in range(len(part) - 1): current_vfs_dir = os.path.dirname(current_vfs_dir)
                current_dir = self.resolve_path(current_vfs_dir)

            elif part in current_dir and current_dir[part]["type"] == "directory":
                current_dir = current_dir[part]["content"]
            else:
                return None  # Путь не найден

        return current_dir

    def get_current_dir_content(self):
        """Возвращает содержимое текущей рабочей директории VFS"""
        return self.resolve_path(self.current_vfs_dir)

    def list_directory(self, path=".") -> None|list:
        """Возвращает список файлов и папок в указанной директории VFS"""
        if path == ".":
            dir_content = self.get_current_dir_content()
        else:
            dir_content = self.resolve_path(path)

        if dir_content is None:
            return None

        items = []
        for name, info in dir_content.items():
            items.append((name, info["type"]))
        return items

    def change_directory(self, path):
        """Изменяет текущую рабочую директорию в VFS"""
        if path == "/":
            self.current_vfs_dir = "/"
            return True
        elif path.startswith("/"):
            new_dir = self.resolve_path(path)
        else:
            new_path = os.path.join(self.current_vfs_dir, path).replace("\\", "/")
            new_dir = self.resolve_path(new_path)

        if new_dir is not None:
            # Сохраняем нормализованный путь
            if path.startswith("/"):
                self.current_vfs_dir = path
            else:
                self.current_vfs_dir = os.path.normpath(
                    os.path.join(self.current_vfs_dir, path)
                ).replace("\\", "/")
            return True
        return False

    def read_file(self, path):
        """Читает и возвращает содержимое файла из VFS"""
        if path.startswith("/"):
            dir_path = os.path.dirname(path).replace("\\", "/")
        else:
            dir_path = os.path.join(self.current_vfs_dir, os.path.dirname(path)).replace("\\", "/")

        filename = os.path.basename(path)
        dir_content = self.resolve_path(dir_path)

        if dir_content and filename in dir_content and dir_content[filename]["type"] == "file":
            return dir_content[filename]["content"]
        return None

    def create_file(self, path, content="", display_time=False):
        """Создает новый файл в VFS (команда touch)"""
        dir_path = os.path.dirname(path)
        filename = os.path.basename(path)
        dir_content = self.resolve_path(dir_path)

        if dir_content is None:
            return False, "Нет такой директории"

        if filename in dir_content:
            if dir_content[filename]["type"] == "file":
                if display_time:
                    return True, (f'\tВремя создания: {dir_content[filename]["created"]}\n'
                                  f'\t\tВремя модификации: {dir_content[filename]["modified"]}')
                # Файл существует - обновляем время модификации
                dir_content[filename]["modified"] = datetime.now().isoformat()
                return True, "Тайминг файла обновлен"
            else:
                return False, "Невозможно создать файл - директория с таким именем уже существует"

        # Создаем новый файл
        dir_content[filename] = {
            "type": "file",
            "content": content,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat()
        }
        return True, "Файл создан"

    def remove_file(self, path):
        """Удаляет файл из VFS (команда rm)"""
        dir_path = os.path.dirname(path)
        filename = os.path.basename(path)
        dir_content = self.resolve_path(dir_path)

        if dir_content is None:
            return False, "Нет такой директории"

        if filename not in dir_content:
            return False, "Нет такого файла"

        if dir_content[filename]["type"] != "file":
            return False, "Невозможно удалить - это директория"

        # Удаляем файл из VFS
        del dir_content[filename]
        return True, "Файл удален"