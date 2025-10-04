import os
import socket
from main import UnixShellEmulator

def main():
    """Демонстрация работы эмулятора"""
    shell = UnixShellEmulator()

    print("=== ДЕМОНСТРАЦИЯ РАБОТЫ ЭМУЛЯТОРА ===\n")

    # Демонстрация различных сценариев
    demo_commands = [
        "pwd",
        "ls",
        "ls /nonexistent",
        "cd /tmp",
        "pwd",
        "cd ~",
        "unknown_command",
        "ls -l -a",
        'ls "folder with spaces"',
        "exit"
    ]

    shell.test_run(demo_commands)


if __name__ == "__main__":
    main()