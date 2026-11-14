from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.core.window import Window
import datetime
import os

# ===== НАСТРОЙКИ ПУТЕЙ =====
VERSION = "0.1"
BASE_DIR = "/storage/emulated/0/AntOSMobile"
DISK_DIR = os.path.join(BASE_DIR, "disk")
NOTES_FILE = os.path.join(DISK_DIR, "AntOS", "notes.txt")
WIFI_NAME_FILE = os.path.join(DISK_DIR, "HostWiFi", "wifi_name.txt")
WIFI_PWD_FILE = os.path.join(DISK_DIR, "HostWiFi", "wifi_password")

Window.clearcolor = (0.05, 0.05, 0.1, 1)

def read_file(path, default="Не задано"):
    try:
        with open(path, "r") as f:
            text = f.read().strip()
            return text if text else default
    except:
        return default

# ===== ЭКРАН ЗАГРУЗКИ =====
class BootScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        layout = BoxLayout(orientation="vertical", padding=30, spacing=20)
        title = Label(text="AntOS Mobile", font_size=48, color=(0.4, 0.9, 1, 1), bold=True)
        self.status = Label(text="Загрузка файловой системы...", font_size=20, color=(1, 1, 1, 1))
        layout.add_widget(Label())
        layout.add_widget(title)
        layout.add_widget(self.status)
        layout.add_widget(Label())
        self.add_widget(layout)
        Clock.schedule_once(self.go_desktop, 2.5)

    def go_desktop(self, dt):
        self.manager.current = "desktop"

# ===== РАБОЧИЙ СТОЛ =====
class DesktopScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        main = BoxLayout(orientation="vertical", padding=15, spacing=10)

        top = BoxLayout(size_hint_y=0.1)
        self.clock_label = Label(text="", font_size=18, halign="right", color=(1, 1, 1, 1))
        top.add_widget(Label(text="AntOS", font_size=18, color=(0.4, 0.9, 1, 1), bold=True))
        top.add_widget(self.clock_label)
        main.add_widget(top)
        Clock.schedule_interval(self.update_clock, 1)

        grid = GridLayout(cols=3, spacing=15, size_hint_y=0.85)
        apps = [
            ("Время", self.open_time),
            ("Калькулятор", self.open_calc),
            ("Заметки", self.open_notes),
            ("Wi-Fi", self.open_settings),
            ("О системе", self.open_about),
            ("Выход", self.exit_app),
        ]
        for name, action in apps:
            btn = Button(text=name, font_size=18, background_color=(0.2, 0.4, 0.6, 1))
            btn.bind(on_press=action)
            grid.add_widget(btn)
        main.add_widget(grid)
        self.add_widget(main)

    def update_clock(self, dt):
        self.clock_label.text = datetime.datetime.now().strftime("%H:%M:%S")

    def open_time(self, *a):
        self.manager.current = "app"
        self.manager.get_screen("app").load("Время",
            datetime.datetime.now().strftime("%d.%m.%Y\n%H:%M:%S"))

    def open_calc(self, *a):
        self.manager.current = "app"
        self.manager.get_screen("app").load_calc()

    def open_notes(self, *a):
        self.manager.current = "app"
        self.manager.get_screen("app").load_notes()

    def open_settings(self, *a):
        self.manager.current = "app"
        wifi_name = read_file(WIFI_NAME_FILE)
        wifi_pwd = read_file(WIFI_PWD_FILE)
        self.manager.get_screen("app").load("Wi-Fi Сеть", 
            f"Имя сети:\n{wifi_name}\n\nПароль:\n{wifi_pwd}\n\n(Данные из HostWiFi)")

    def open_about(self, *a):
        self.manager.current = "app"
        self.manager.get_screen("app").load("О системе",
            f"AntOS Mobile v{VERSION}\nСделано на Python + Kivy\nФайловая система активна!")

    def exit_app(self, *a):
        App.get_running_app().stop()

# ===== УНИВЕРСАЛЬНЫЙ ЭКРАН ПРИЛОЖЕНИЯ =====
class AppScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.box = BoxLayout(orientation="vertical", padding=15, spacing=10)
        self.add_widget(self.box)

    def clear_box(self):
        self.box.clear_widgets()

    def load(self, title, text):
        self.clear_box()
        top = BoxLayout(size_hint_y=0.15)
        back = Button(text="< Назад", size_hint_x=0.3, background_color=(0.6, 0.2, 0.2, 1))
        back.bind(on_press=lambda *a: setattr(self.manager, "current", "desktop"))
        top.add_widget(back)
        top.add_widget(Label(text=title, font_size=22, color=(0.4, 0.9, 1, 1), bold=True))
        self.box.add_widget(top)
        self.box.add_widget(Label(text=text, font_size=18, color=(1, 1, 1, 1)))

    def load_calc(self):
        self.clear_box()
        top = BoxLayout(size_hint_y=0.15)
        back = Button(text="< Назад", size_hint_x=0.3, background_color=(0.6, 0.2, 0.2, 1))
        back.bind(on_press=lambda *a: setattr(self.manager, "current", "desktop"))
        top.add_widget(back)
        top.add_widget(Label(text="Калькулятор", font_size=22, color=(0.4, 0.9, 1, 1), bold=True))
        self.box.add_widget(top)

        self.calc_input = TextInput(text="", multiline=False, font_size=24, size_hint_y=0.15)
        self.box.add_widget(self.calc_input)
        result_btn = Button(text="Вычислить", size_hint_y=0.12, background_color=(0.2, 0.6, 0.3, 1))
        result_btn.bind(on_press=self.do_calc)
        self.box.add_widget(result_btn)
        self.calc_result = Label(text="", font_size=28, color=(0.4, 1, 0.6, 1))
        self.box.add_widget(self.calc_result)

    def do_calc(self, *a):
        try:
            self.calc_result.text = "= " + str(eval(self.calc_input.text))
        except:
            self.calc_result.text = "Ошибка!"

    def load_notes(self):
        self.clear_box()
        top = BoxLayout(size_hint_y=0.15)
        back = Button(text="< Назад", size_hint_x=0.3, background_color=(0.6, 0.2, 0.2, 1))
        back.bind(on_press=lambda *a: setattr(self.manager, "current", "desktop"))
        top.add_widget(back)
        top.add_widget(Label(text="Заметки", font_size=22, color=(0.4, 0.9, 1, 1), bold=True))
        self.box.add_widget(top)

        self.note_input = TextInput(hint_text="Текст заметки...", multiline=True, font_size=18, size_hint_y=0.3)
        self.box.add_widget(self.note_input)
        save = Button(text="Сохранить", size_hint_y=0.12, background_color=(0.2, 0.6, 0.3, 1))
        save.bind(on_press=self.save_note)
        self.box.add_widget(save)
        self.notes_label = Label(text="", font_size=16, color=(1, 1, 1, 1))
        self.box.add_widget(self.notes_label)
        self.refresh_notes()

    def save_note(self, *a):
        text = self.note_input.text.strip()
        if text:
            try:
                with open(NOTES_FILE, "a") as f:
                    f.write(datetime.datetime.now().strftime("%d.%m %H:%M") + " - " + text + "\n")
                self.note_input.text = ""
                self.refresh_notes()
            except Exception as e:
                self.notes_label.text = f"Ошибка записи: {e}"

    def refresh_notes(self):
        try:
            with open(NOTES_FILE, "r") as f:
                self.notes_label.text = f.read()
        except:
            self.notes_label.text = "Заметок пока нет"

# ===== ПРИЛОЖЕНИЕ =====
class AntOS(App):
    def build(self):
        self.title = "AntOS Mobile v0.1"
        sm = ScreenManager()
        sm.add_widget(BootScreen(name="boot"))
        sm.add_widget(DesktopScreen(name="desktop"))
        sm.add_widget(AppScreen(name="app"))
        sm.current = "boot"
        return sm

AntOS().run()
