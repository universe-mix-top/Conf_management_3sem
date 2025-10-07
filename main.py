from UnixShellEmulator import UnixShellEmulator

import os
import sys

def parse_arguments():
    """Парсит аргументы командной строки"""
    vfs_path = None
    startup_script = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--vfs' and i + 1 < len(args):
            vfs_path = args[i + 1]
            i += 1
        elif args[i] == '--script' and i + 1 < len(args):
            startup_script = args[i + 1]
            i += 1
        i += 1

    return vfs_path, startup_script


def main():
    """Главная функция приложения"""
    vfs_path, startup_script = parse_arguments()

    # Команды для тестирования VFS
    vfs_test_commands = [
        "echo === ТЕСТИРОВАНИЕ VFS ===",
        "vfs status",
        "vfs on",
        "pwd",
        "ls",
        "ls /",
        "cd /home",
        "pwd",
        "ls",
        "cd user",
        "pwd",
        "ls",
        "cd documents",
        "pwd",
        "ls",
        "cat readme.txt",
        "cd /etc",
        "ls",
        "cat config.conf",
        "cd /bin",
        "ls",
        "cat ls",
        "echo --- Тест ошибок в VFS ---",
        "cd /nonexistent",
        "cat /unknown_file.txt",
        "ls /invalid/path",
        "vfs off",
        "pwd",
        "echo Тестирование VFS завершено!",
        "exit"
    ]

    # Если указан стартовый скрипт, загружаем команды из файла
    if startup_script and os.path.exists(startup_script):
        with open(startup_script, 'r', encoding='utf-8') as f:
            startup_commands = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    else:
        startup_commands = vfs_test_commands

    # Создаем и запускаем эмулятор
    shell = UnixShellEmulator(vfs_path=vfs_path, startup_script=startup_commands)
    shell.run()


if __name__ == "__main__":
    main()
def parse_arguments():
    """Парсит аргументы командной строки"""
    vfs_path = None
    startup_script = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--vfs' and i + 1 < len(args):
            vfs_path = args[i + 1]
            i += 1
        elif args[i] == '--script' and i + 1 < len(args):
            startup_script = args[i + 1]
            i += 1
        i += 1

    return vfs_path, startup_script


def main():
    """Главная функция приложения"""
    vfs_path, startup_script = parse_arguments()

    # Команды для тестирования VFS
    vfs_test_commands = [
        "echo === ТЕСТИРОВАНИЕ VFS ===",
        "vfs status",
        "vfs on",
        "pwd",
        "ls",
        "ls /",
        "cd /home",
        "pwd",
        "ls",
        "cd user",
        "pwd",
        "ls",
        "cd documents",
        "pwd",
        "ls",
        "cat readme.txt",
        "cd /etc",
        "ls",
        "cat config.conf",
        "cd /bin",
        "ls",
        "cat ls",
        "echo --- Тест ошибок в VFS ---",
        "cd /nonexistent",
        "cat /unknown_file.txt",
        "ls /invalid/path",
        "vfs off",
        "pwd",
        "echo Тестирование VFS завершено!",
        "exit"
    ]

    # Если указан стартовый скрипт, загружаем команды из файла
    if startup_script and os.path.exists(startup_script):
        with open(startup_script, 'r', encoding='utf-8') as f:
            startup_commands = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    else:
        startup_commands = vfs_test_commands

    # Создаем и запускаем эмулятор
    shell = UnixShellEmulator(vfs_path=vfs_path, startup_script=startup_commands)
    shell.run()


if __name__ == "__main__":
    main()