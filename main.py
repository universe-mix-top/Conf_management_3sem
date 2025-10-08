import os
import sys
from UnixShellEmulator import UnixShellEmulator


def parse_arguments():
    """Обрабатывает аргументы командной строки для настройки эмулятора"""
    vfs_path = None
    startup_script = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if (args[i] == '--vfs' or args[i] == '-v') and i + 1 < len(args):
            vfs_path = args[i + 1]
            i += 1
        elif (args[i] == '--script' or args[i] == '-s') and i + 1 < len(args):
            startup_script = args[i + 1]
            i += 1
        i += 1

    return vfs_path, startup_script


def main():
    """Главная функция: парсит аргументы и запускает эмулятор"""
    vfs_path, startup_script = parse_arguments()

    # Комплексный тестовый скрипт для всех команд включая touch и rm
    comprehensive_test_commands = [
        "echo Тестирование VFS",
        "vfs on",
        "pwd",
        "ls",
        "touch file1.txt",
        "touch file2.txt",
        "ls",
        "cd home",
        "pwd",
        "touch ../readme.txt",
        "ls",
        "cd ..",
        "rm file1.txt",
        "touch -d readme.txt",
        "ls",
        "vfs off",
        "exit"
    ]

    # Если указан стартовый скрипт, загружаем команды из файла
    if startup_script and os.path.exists(startup_script):
        with open(startup_script, 'r', encoding='utf-8') as f:
            startup_commands = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    elif startup_script:
        startup_commands = [cmd for cmd in comprehensive_test_commands if cmd and not cmd.startswith('#')]
    else:
        startup_commands = []

    # Создаем и запускаем эмулятор
    shell = UnixShellEmulator(vfs_path=vfs_path, startup_script=startup_commands)
    shell.run()


if __name__ == "__main__":
    main()