"""
Ant OS — setup.py
Установка: pip install .
Запуск: antos
"""
from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import sys

VERSION = "3.6.0"
BASE_DIR = "/storage/emulated/0/AntOS"


# ═══════════════════════════════════════════
#   СОЗДАНИЕ ПАПОК ПРИ УСТАНОВКЕ
# ═══════════════════════════════════════════
def create_antos_dirs():
    """Создаёт все папки Ant OS."""
    dirs = [
        BASE_DIR,
        os.path.join(BASE_DIR, "Apps"),
        os.path.join(BASE_DIR, "SystemApps"),
        os.path.join(BASE_DIR, "Icons"),
        os.path.join(BASE_DIR, "Sounds"),
        os.path.join(BASE_DIR, "wallpapers"),
        os.path.join(BASE_DIR, "Datas"),
        os.path.join(BASE_DIR, "Datas", "quarantine"),
        os.path.join(BASE_DIR, "HtmlSupport"),
        os.path.join(BASE_DIR, "Market"),
    ]

    print("\n🐜 Ant OS — создание папок:")
    for d in dirs:
        try:
            os.makedirs(d, exist_ok=True)
            print(f"  ✅ {d}")
        except PermissionError:
            print(f"  ⚠️ {d} — нет доступа")
        except Exception as e:
            print(f"  ❌ {d} — {e}")

    # Создать пустые файлы данных
    default_files = {
        os.path.join(BASE_DIR, "Datas", "settings.json"): '{}',
        os.path.join(BASE_DIR, "Datas", "notify.json"): '[]',
        os.path.join(BASE_DIR, "Datas", "logs.txt"): '',
    }
    for path, content in default_files.items():
        if not os.path.exists(path):
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"  📄 {path}")
            except Exception as e:
                print(f"  ❌ {path}: {e}")

    print("\n✅ Ant OS готова!\n")


# ═══════════════════════════════════════════
#   КОПИРОВАНИЕ AntSystem.py
# ═══════════════════════════════════════════
def copy_antos_files():
    """Копирует основные модули в BASE_DIR."""
    here = os.path.abspath(os.path.dirname(__file__))
    files_to_copy = [
        "AntSystem.py",
        "AntGuard.py",
        "battery.py",
    ]

    print("\n🐜 Ant OS — копирование файлов:")
    for fname in files_to_copy:
        src = os.path.join(here, fname)
        dst = os.path.join(BASE_DIR, fname)
        if os.path.exists(src):
            try:
                with open(src, "r", encoding="utf-8") as f:
                    content = f.read()
                with open(dst, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"  📄 {dst}")
            except Exception as e:
                print(f"  ❌ {fname}: {e}")
        else:
            print(f"  ⚠️ {fname} не найден")


# ═══════════════════════════════════════════
#   КОМАНДА УСТАНОВКИ (после pip install)
# ═══════════════════════════════════════════
class PostInstallCommand(install):
    """Создаёт папки + копирует файлы после установки."""
    def run(self):
        install.run(self)
        create_antos_dirs()
        copy_antos_files()


# ═══════════════════════════════════════════
#   SETUP
# ═══════════════════════════════════════════
setup(
    name="antos",
    version=VERSION,
    description="Ant OS — мобильная ОС на Python + Kivy",
    author="galexa233",
    url="https://github.com/galexa233/AntOS",
    license="MIT",

    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "kivy>=2.3.0",
        "kivymd>=1.2.0",
        "pillow>=10.0.0",
        "requests>=2.31.0",
        "plyer>=2.1.0",
    ],
    python_requires=">=3.8",

    # Команды
    entry_points={
        "console_scripts": [
            "antos=antos.__main__:main",
            "antos-info=antos.system:print_status",
            "antos-guard=antos.guard:main",
        ],
    },

    # Кастомная команда install (создание папок)
    cmdclass={
        "install": PostInstallCommand,
    },

    zip_safe=False,
)
