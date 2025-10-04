import os
import socket


class UnixShellEmulator:
    def __init__(self):
        self.current_dir = os.getcwd()
        self.username = os.getenv('USER') or os.getenv('USERNAME') or 'user'
        self.hostname = socket.gethostname()
        self.commands = {
            'ls': self.cmd_ls,
            'cd': self.cmd_cd,
            'exit': self.cmd_exit,
            'pwd': self.cmd_pwd
        }

    def get_prompt(self):
        """Формирует приглашение к вводу в формате username@hostname:directory$"""
        # Получаем относительный путь от домашней директории
        home_dir = os.path.expanduser("~")
        if self.current_dir.startswith(home_dir):
            display_dir = "~" + self.current_dir[len(home_dir):]
        else:
            display_dir = self.current_dir

        return f"{self.username}@{self.hostname}:{display_dir}$ "

    def parse_input(self, user_input):
        """Парсит ввод пользователя на команду и аргументы"""
        try:
            parts = user_input.strip().split(' ')
            if not parts:
                return None, []
            command = parts[0]
            args = parts[1:]
            return command, args
        except ValueError as e:
            print(f"Ошибка парсинга: {e}")
            return None, []

    def cmd_ls(self, args):
        """Команда ls - вывод информации о файлах"""
        print(f"Команда: ls")
        print(f"Аргументы: {args}")

    def cmd_cd(self, args):
        """Команда cd - смена директории"""
        print(f"Команда: cd")
        print(f"Аргументы: {args}")

    def cmd_pwd(self, args):
        """Команда pwd - вывод текущей директории"""
        print(f"Команда: pwd")
        print(f"Аргументы: {args}")

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
            print(f"{command}: команда не найдена")

    def run(self):
        """Основной цикл REPL (Read-Eval-Print Loop)"""
        print("Добро пожаловать в эмулятор командной строки UNIX!")
        print("Доступные команды: ls, cd, pwd, exit")
        print("Для выхода введите 'exit'")
        print("-" * 50)

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

    def test_run(self, test_comands):
        """Основной цикл REPL (Read-Eval-Print Loop)"""
        print("Добро пожаловать в эмулятор командной строки UNIX!")
        print("Доступные команды: ls, cd, pwd, exit")
        print("Для выхода введите 'exit'")
        print("-" * 50)

        while True:
            try:
                for com in test_comands:
                    print(self.get_prompt(), com)
                    command, args = self.parse_input(com)

                    if command is None:
                        continue

                    self.execute_command(command, args)

            except KeyboardInterrupt:
                print("\n\nДля выхода введите 'exit'")
            except EOFError:
                print("\nВыход из эмулятора")
                break


def main():
    """Демонстрация работы эмулятора"""
    shell = UnixShellEmulator()

    print("=== ДЕМОНСТРАЦИЯ РАБОТЫ ЭМУЛЯТОРА ===\n")

    shell.run()


if __name__ == "__main__":
    main()