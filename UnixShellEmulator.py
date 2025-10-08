import os
import socket

from IPython.core.display_functions import display

from VirtualFileSystem import VirtualFileSystem


class UnixShellEmulator:
    def __init__(self, vfs_path=None, startup_script=None):
        self.current_dir = os.getcwd()
        self.username = os.getenv('USER') or os.getenv('USERNAME') or 'user'
        self.hostname = socket.gethostname()
        self.vfs_path = vfs_path
        self.startup_script = startup_script

        # Инициализируем VFS
        self.vfs = VirtualFileSystem(vfs_path)
        self.in_vfs_mode = False

        self.commands = {
            'ls': self.cmd_ls,
            'cd': self.cmd_cd,
            'exit': self.cmd_exit,
            'pwd': self.cmd_pwd,
            'echo': self.cmd_echo,
            'whoami': self.cmd_whoami,
            'hostname': self.cmd_hostname,
            'vfs': self.cmd_vfs,
            'cat': self.cmd_cat,
            'touch': self.cmd_touch,
            'rm': self.cmd_rm,
        }

    def get_prompt(self):
        """Формирует приглашение к вводу"""
        if self.in_vfs_mode:
            display_dir = self.vfs.current_vfs_dir
            if display_dir == "/":
                display_dir = "/"
            else:
                display_dir = display_dir.rstrip("/")
            return f"[VFS]{self.username}@{self.hostname}:{display_dir}$ "

        home_dir = os.path.expanduser("~")
        if self.current_dir.startswith(home_dir):
            display_dir = "~" + self.current_dir[len(home_dir):]
        else:
            display_dir = self.current_dir
        return f"{self.username}@{self.hostname}:{display_dir}$ "

    def parse_input(self, user_input):
        """Парсит ввод пользователя на команду и аргументы"""
        try:
            parts = user_input.strip().split()
            if not parts or not parts[0]:
                return None, []
            command = parts[0]
            args = parts[1:]
            return command, args
        except Exception as e:
            print(f"Ошибка парсинга: {e}")
            return None, []

    def cmd_ls(self, args):
        """Команда ls - вывод информации о файлах"""
        if self.in_vfs_mode:
            path = args[0] if args else "."
            items = self.vfs.list_directory(path)
            if items is None:
                print(f"ls: невозможно получить доступ к '{path}': Нет такого файла или каталога")
                return

            for name, item_type in items:
                if item_type == "directory":
                    print(f"\033[93m{name}/\033[0m")
                else:
                    print(name)
        else:
            target_dir = self.current_dir
            if args:
                target_dir = os.path.join(self.current_dir, args[0])

            try:
                if not os.path.exists(target_dir):
                    print(f"ls: невозможно получить доступ к '{args[0]}': Нет такого файла или каталога")
                    return

                if os.path.isfile(target_dir):
                    print(args[0])
                    return

                items = os.listdir(target_dir)
                for item in items:
                    item_path = os.path.join(target_dir, item)
                    if os.path.isdir(item_path):
                        print(f"\033[93m{item}/\033[0m")
                    else:
                        print(item)

            except PermissionError:
                print(f"ls: невозможно открыть каталог '{args[0] if args else '.'}': Отказано в доступе")
            except Exception as e:
                print(f"ls: ошибка: {e}")

    def cmd_cd(self, args):
        """Команда cd - смена директории"""
        if self.in_vfs_mode:
            if not args:
                path = "/"
            else:
                path = args[0]

            if not self.vfs.change_directory(path):
                print(f"cd: {path}: Нет такого файла или каталога")
            return

        if not args:
            new_dir = os.path.expanduser("~")
            self.current_dir = new_dir
            os.chdir(new_dir)
            return
        target = args[0]

        if target == "~":
            new_dir = os.path.expanduser("~")
        elif target.startswith("~/"):
            new_dir = os.path.expanduser("~") + target[1:]
        else:
            if os.path.isabs(target):
                new_dir = target
            else:
                new_dir = os.path.join(self.current_dir, target)

        try:
            new_dir = os.path.abspath(new_dir)

            if not os.path.exists(new_dir):
                print(f"cd: {target}: Нет такого файла или каталога")
                return

            if not os.path.isdir(new_dir):
                print(f"cd: {target}: Не является каталогом")
                return

            self.current_dir = new_dir
            os.chdir(new_dir)

        except Exception as e:
            print(f"cd: ошибка: {e}")

    def cmd_pwd(self, args):
        """Команда pwd - вывод текущей директории"""
        if self.in_vfs_mode:
            print(self.vfs.current_vfs_dir)
        else:
            print(self.current_dir)

    def cmd_echo(self, args):
        """Команда echo - вывод текста"""
        print(' '.join(args))

    def cmd_whoami(self, args):
        """Команда whoami - вывод имени пользователя"""
        print(self.username)

    def cmd_hostname(self, args):
        """Команда hostname - вывод имени хоста"""
        print(self.hostname)

    def cmd_vfs(self, args):
        """Команда vfs - управление виртуальной файловой системой"""
        if not args:
            print("Использование: vfs [on|off|status]")
            return

        subcommand = args[0]
        if subcommand == "on":
            self.in_vfs_mode = True
            print("Режим VFS включен")
        elif subcommand == "off":
            self.in_vfs_mode = False
            print("Режим VFS выключен")
        elif subcommand == "status":
            status = "включен" if self.in_vfs_mode else "выключен"
            print(f"Режим VFS: {status}")
            if self.vfs_path:
                print(f"VFS загружена из: {self.vfs_path}")
            else:
                print("Используется VFS по умолчанию")
        else:
            print(f"vfs: неизвестная подкоманда: {subcommand}")

    def cmd_cat(self, args):
        """Команда cat - вывод содержимого файла"""
        if not args:
            print("Использование: cat <файл>")
            return

        filename = args[0]
        if self.in_vfs_mode:
            content = self.vfs.read_file(filename)
            if content is None:
                print(f"cat: {filename}: Нет такого файла или каталога")
            else:
                print(content)
        else:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    print(f.read())
            except FileNotFoundError:
                print(f"cat: {filename}: Нет такого файла или каталога")
            except Exception as e:
                print(f"cat: ошибка: {e}")

    def cmd_touch(self, args):
        """Создает новые файлы или обновляет время модификации существующих"""
        if not args:
            print("Использование: touch <файл1> [-d(--display) - вывод даты создания и модификации]")
            return

        if not self.in_vfs_mode:
            print("touch: команда доступна только в режиме VFS")
            return

        display_time = '-d' in args or '--display' in args

        for path in args:
            if path == '-d' or path == '--display':
                continue
            success, message = self.vfs.create_file(path, display_time=display_time)
            if success:
                print(f"touch: {message}: '{path}'")
            else:
                print(f"touch: невозможно создать '{path}': {message}")

    def cmd_rm(self, args):
        """Удаляет файлы из VFS"""
        if not args:
            print("Использование: rm <файл1> [файл2 ...]")
            return

        if not self.in_vfs_mode:
            print("rm: команда доступна только в режиме VFS")
            return

        for filename in args:
            success, message = self.vfs.remove_file(filename)
            if success:
                print(f"rm: {message}: '{filename}'")
            else:
                print(f"rm: невозможно удалить '{filename}': {message}")


    def cmd_exit(self, args):
        """Завершает работу эмулятора"""
        print("Выход из эмулятора командной строки")
        exit(0)

    def execute_command(self, command, args):
        """Выполняет команду или сообщает об ошибке если команда не найдена"""
        if command in self.commands:
            self.commands[command](args)
        else:
            print(f"{command}: команда не найдена")

    def run_startup_script(self):
        """Выполняет команды из стартового скрипта"""
        print("Выполнение стартового скрипта:")
        print("-" * 50)

        try:
            for com in self.startup_script:
                print(f"{self.get_prompt()}\033[92m{com}\033[0m")
                command, args = self.parse_input(com)

                if command is None:
                    continue

                self.execute_command(command, args)
        finally:
            print("-" * 50)
            print("Стартовый скрипт выполнен")
            print()

    def run(self):
        """Основной цикл работы эмулятора: чтение-выполнение-вывод"""
        print("Добро пожаловать в эмулятор командной строки UNIX!")
        if self.vfs_path:
            print(f"VFS путь: {self.vfs_path}")
        else:
            print("VFS: используется файловая система по умолчанию")

        if self.startup_script:
            print(f"Выполняется стартовый скрипт с {len(self.startup_script)} командами")

        print("Доступные команды: ls, cd, pwd, echo, whoami, hostname, vfs, cat, touch, rm, exit")
        print("Для выхода введите 'exit'")
        print("-" * 50)

        if self.startup_script:
            self.run_startup_script()

        while True:
            try:
                user_input = input(self.get_prompt())
                command, args = self.parse_input(user_input)

                if command is None:
                    continue

                self.execute_command(command, args)

            except KeyboardInterrupt:
                print("\n\nДля выхода введите 'exit'")
            except EOFError:
                print("\nВыход из эмулятора")
                break
