import os
import socket
import sys


class UnixShellEmulator:
    def __init__(self, vfs_path=None, startup_script=None):
        self.current_dir = os.getcwd()
        self.username = os.getenv('USER') or os.getenv('USERNAME') or 'user'
        self.hostname = socket.gethostname()
        self.vfs_path = vfs_path or os.getcwd()
        self.startup_script = startup_script

        # Создаем VFS директорию если её нет
        if self.vfs_path and not os.path.exists(self.vfs_path):
            os.makedirs(self.vfs_path)

        self.commands = {
            'ls': self.cmd_ls,
            'cd': self.cmd_cd,
            'exit': self.cmd_exit,
            'pwd': self.cmd_pwd,
            'echo': self.cmd_echo,
            'whoami': self.cmd_whoami,
            'hostname': self.cmd_hostname,
        }

    def get_prompt(self):
        """Формирует приглашение к вводу в формате username@hostname:directory$"""
        home_dir = os.path.expanduser("~")
        if self.current_dir.startswith(home_dir):
            display_dir = "~" + self.current_dir[len(home_dir):]
        else:
            display_dir = self.current_dir

        return f"{self.username}@{self.hostname}:{display_dir}$ "

    def parse_input(self, user_input):
        """Парсит ввод пользователя на команду и аргументы"""
        try:
            parts = user_input.strip(' ')
            if not parts or not parts[0]:
                return None, []
            command = parts[0]
            args = parts[1:]
            return command, args
        except KeyError as e:
            print(f"Такая команда не найдена: {e}")
            return None, []
        except ValueError as e:
            print(f"Ошибка парсинга: {e}")
            return None, []

    def cmd_ls(self, args):
        """Команда ls - вывод информации о файлах"""
        print(f"Команда: ls")
        print(f"Аргументы: {args}")
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
            print(*items, sep='\n')

        except PermissionError:
            print(f"ls: невозможно открыть каталог '{args[0] if args else '.'}': Отказано в доступе")
        except Exception as e:
            print(f"ls: ошибка: {e}")

    def cmd_cd(self, args):
        """Команда cd - смена директории"""
        print(f"Команда: cd")
        print(f"Аргументы: {args}")
        new_dir = self.current_dir
        if not args:
            # cd без аргументов - переход в домашнюю директорию
            new_dir = os.path.expanduser("~")
            self.current_dir = new_dir
            os.chdir(new_dir)

        current = args[0]
        if current == "~":
            new_dir = os.path.expanduser("~")
        elif current == "-":
            new_dir = os.path.dirname(current)
        elif current[:2] == '..':
            while True:
                if current[:2] == '..':
                    current = current[1:]
                    new_dir = os.path.dirname(current)
                    continue
                current = current[1:]
                break
            current = current[1:]
            new_dir = os.path.join(new_dir, current)
        elif current[0] == r'\\'[0]:
            new_dir = os.path.join(current)
        else:
            if current[:2] == r'.\\'[:2]: current = current[2:]
            new_dir = os.path.join(new_dir, current)
        new_dir = os.path.normpath(new_dir)

        try:
            new_dir = os.path.abspath(new_dir)

            if not os.path.exists(new_dir):
                print(f"cd: {args[0]}: Нет такого файла или каталога")
                return

            if not os.path.isdir(new_dir):
                print(f"cd: {args[0]}: Не является каталогом")
                return

            self.current_dir = new_dir
            os.chdir(new_dir)  # Меняем реальную текущую директорию

        except Exception as e:
            print(f"cd: ошибка: {e}")

    def cmd_pwd(self, args):
        """Команда pwd - вывод текущей директории"""
        print(f"Команда: pwd")
        print(f"Аргументы: {args}")
        print(self.current_dir)

    def cmd_echo(self, args):
        """Команда echo - вывод текста"""
        print(f"Команда: echo")
        print(f"Аргументы: {args}")
        print(' '.join(args))

    def cmd_whoami(self, args):
        """Команда whoami - вывод имени пользователя"""
        print(f"Команда: whoami")
        print(f"Аргументы: {args}")
        print(self.username)

    def cmd_hostname(self, args):
        """Команда hostname - вывод имени хоста"""
        print(f"Команда: hostname")
        print(f"Аргументы: {args}")
        print(self.hostname)

    def cmd_exit(self, args):
        """Команда exit - выход из эмулятора"""
        print(f"Команда: exit")
        print(f"Аргументы: {args}")
        print("Выход из эмулятора командной строки")
        exit(0)

    def execute_command(self, command, args):
        """Выполняет команду"""
        if command in self.commands:
            self.commands[command](args)
        else:
            print(f"Команда не найдена: {command}")

    def run_startup_script(self):
        """Выполняет стартовый скрипт если он указан"""
        for com in self.startup_script:
            print(self.get_prompt())
            com, args = self.parse_input(com)
            self.execute_command(com, args)

    def run(self):
        """Основной цикл REPL (Read-Eval-Print Loop)"""
        print("Добро пожаловать в эмулятор командной строки UNIX!")
        print(f"VFS путь: {self.vfs_path}")
        if self.startup_script:
            print(f"Стартовый скрипт: {self.startup_script}")
        print("Доступные команды: ls, cd, pwd, echo, whoami, hostname, exit")
        print("Для выхода введите 'exit'")
        print("-" * 50)

        # Выполняем стартовый скрипт
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


def main(vfs_path=os.getcwd()):
    """Главная функция приложения"""

    # Отладочный вывод параметров
    print("=== ОТЛАДОЧНЫЙ ВЫВОД ПАРАМЕТРОВ ===")
    print(f"VFS путь: {vfs_path}")
    print(f"Текущая директория: {os.getcwd()}")
    print("=" * 40)
    print()

    # Набор команд для тестирования и демонстрации
    demo_commands = [
        "echo === ДЕМОНСТРАЦИЯ РАБОТЫ ЭМУЛЯТОРА ===",
        "pwd",
        "whoami",
        "hostname",
        "echo --- Тест команды ls ---",
        "ls",
        "ls /tmp",
        "ls /nonexistent_directory",
        "echo --- Тест команды cd ---",
        "cd /tmp",
        "pwd",
        "ls",
        "cd ~",
        "pwd",
        "echo --- Тест неизвестной команды ---",
        "unknown_command",
        "echo --- Тест команды echo ---",
        "echo Hello World!",
        "echo Это тест с несколькими аргументами",
        "exit"
    ]

    # Создаем и запускаем эмулятор
    shell = UnixShellEmulator(startup_script=demo_commands)
    shell.run()


if __name__ == "__main__":
    main()