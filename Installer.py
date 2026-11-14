import os
import sys

# --- НАСТРОЙКИ УСТАНОВКИ ---
VERSION = "0.1"
BASE_DIR = "/storage/emulated/0/AntOSMobile"

# Список папок, которые создаст установщик
FOLDERS = [
    "disk/AntOS",
    "disk/AppsData",
    "disk/HostWiFi",
    "disk/System32",
    "src",
    "setup"
]

# Файлы по умолчанию, которые создаст установщик (если их нет)
DEFAULT_FILES = {
    "version.txt": VERSION,
    "disk/HostWiFi/wifi_name.txt": "AntOS_Home_WiFi",
    "disk/HostWiFi/wifi_password": "12345678",
    "disk/HostWiFi/settings_wifi.json": '{"enabled": true, "security": "WPA2"}'
}

def print_boot(text):
    print(f"[AntOS] {text}")

def install():
    print("=" * 35)
    print("     УСТАНОВКА AntOS Mobile v0.1")
    print("=" * 35)
    
    # 1. Создаем базовую папку, если ее нет
    if not os.path.exists(BASE_DIR):
        try:
            os.makedirs(BASE_DIR)
            print_boot(f"Создана корневая папка: {BASE_DIR}")
        except Exception as e:
            print(f"ОШИБКА: Нет доступа к памяти.\n{e}")
            sys.exit()

    # 2. Создаем все папки из списка
    print_boot("Создание файловой системы...")
    for folder in FOLDERS:
        path = os.path.join(BASE_DIR, folder)
        if not os.path.exists(path):
            os.makedirs(path)
            print_boot(f"Создана папка: {folder}/")

    # 3. Создаем файлы с базовыми настройками
    print_boot("Создание системных файлов...")
    for file_path, content in DEFAULT_FILES.items():
        full_path = os.path.join(BASE_DIR, file_path)
        if not os.path.exists(full_path):
            with open(full_path, "w") as f:
                f.write(content)
            print_boot(f"Создан файл: {file_path}")

    print("=" * 35)
    print("УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО!")
    print("=" * 35)

    # 4. Проверка библиотеки Kivy
    try:
        import kivy
        print_boot("Проверка Kivy: ОК")
    except ImportError:
        print("\n[ВНИМАНИЕ] Библиотека Kivy не установлена!")
        print("Без нее графическая ОС не запустится.")
        print("Откройте Pydroid 3 -> Pip -> введите kivy -> Install\n")
        return # Останавливаемся, если нет Киви

    # 5. Запуск ОС
    run_file = os.path.join(BASE_DIR, "setup", "run.py")
    if os.path.exists(run_file):
        print_boot("Запуск системы...")
        # Небольшая пауза для красоты
        import time
        time.sleep(1)
        os.system(f"python {run_file}")
    else:
        print("\n[ОШИБКА] Файл setup/run.py не найден!")
        print("Скачайте его с GitHub и положите в папку setup.")

if __name__ == "__main__":
    install()
