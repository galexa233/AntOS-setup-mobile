"""
Ant OS — v3.5.0
Устройство: Redmi Note 14
Поддержка SystemApps (системные приложения)
"""

import os
import sys
import json
import datetime
import zipfile
import tempfile
import importlib.util

sys.path.insert(0, "/storage/emulated/0/AntOS")

BASE_DIR        = "/storage/emulated/0/AntOS"
DATA_DIR        = os.path.join(BASE_DIR, "Datas")
ICONS_DIR       = os.path.join(BASE_DIR, "Icons")
WALLPAPER_DIR   = os.path.join(BASE_DIR, "wallpapers")
APPS_DIR        = os.path.join(BASE_DIR, "Apps")
SYSTEMAPPS_DIR  = os.path.join(BASE_DIR, "SystemApps")   # ⭐
SOUNDS_DIR      = os.path.join(BASE_DIR, "Sounds")

SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
LOG_FILE      = os.path.join(DATA_DIR, "logs.txt")
VIRUS_FILE    = os.path.join(DATA_DIR, "antguard.json")


# ═══════════════════════════════════════════
#   🛡️ ИМПОРТ ANTGUARD
# ═══════════════════════════════════════════
try:
    from AntGuard import AntGuard
    print("[AntSystem] ✅ AntGuard импортирован")
except ImportError as e:
    print(f"[AntSystem] ⚠️ AntGuard.py не найден: {e}")
    class AntGuard:
        VERSION = "0.0"
        def __init__(self, os_core=None):
            self.status = "OK"
            self.threats = []
            self.scanned = 0
            self.scanned_code = 0
            self.last_scan = ""
            self.os = os_core
        def scan(self):
            return {"status": "OK", "threats": [], "scanned": 0,
                    "scanned_code": 0, "last_scan": ""}
        def get_color(self):
            return (0.5, 0.5, 0.5, 1)
        def get_status_text(self):
            return "[ -- ] AntGuard не установлен"
        def quarantine(self):
            return 0
        def _save(self):
            pass


def ensure_dirs():
    for d in [BASE_DIR, DATA_DIR, ICONS_DIR, WALLPAPER_DIR,
              APPS_DIR, SYSTEMAPPS_DIR, SOUNDS_DIR]:
        os.makedirs(d, exist_ok=True)


def icon_path(name):
    for ext in [".png", ".PNG", ".jpg", ".JPG", ".jpeg", ".webp"]:
        p = os.path.join(ICONS_DIR, name + ext)
        if os.path.exists(p):
            return p
    return None


def logo_path():
    for n in ["AntOS", "antos", "Antos", "logo", "Logo"]:
        p = icon_path(n)
        if p:
            return p
    return None


def sound_path(name):
    for ext in [".mp3", ".MP3", ".ogg", ".wav", ".m4a"]:
        p = os.path.join(SOUNDS_DIR, name + ext)
        if os.path.exists(p):
            return p
    return None


def list_wallpapers():
    try:
        return sorted([f for f in os.listdir(WALLPAPER_DIR)
                       if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))])
    except Exception:
        return []


def wallpaper_path(name):
    if not name:
        return None
    p = os.path.join(WALLPAPER_DIR, name)
    return p if os.path.exists(p) else None


# ═══════════════════════════════════════════
#   📦 СПИСОК ПРИЛОЖЕНИЙ (Apps + SystemApps)
# ═══════════════════════════════════════════
def list_apps():
    """Все приложения — пользовательские + системные."""
    apps = []
    for folder, is_system in [(APPS_DIR, False), (SYSTEMAPPS_DIR, True)]:
        if not os.path.exists(folder):
            continue
        try:
            for f in os.listdir(folder):
                if f.lower().endswith((".zip", ".pyapp")):
                    apps.append({
                        "file": f,
                        "path": os.path.join(folder, f),
                        "system": is_system,
                    })
        except Exception:
            pass
    apps.sort(key=lambda x: (not x["system"], x["file"]))
    return apps


def list_app_files():
    """Только имена файлов."""
    return [a["file"] for a in list_apps()]


def read_app_meta(zip_path):
    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            for n in z.namelist():
                if n.endswith("main.json"):
                    return json.loads(z.read(n).decode("utf-8"))
    except Exception:
        pass
    return {"name": os.path.basename(zip_path), "version": "?"}


def run_pyapp(zip_path, os_core):
    try:
        tmp = tempfile.mkdtemp(prefix="antos_")
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(tmp)
        main_py = None
        for root, dirs, files in os.walk(tmp):
            if "main.py" in files:
                main_py = os.path.join(root, "main.py")
                break
        if not main_py:
            os_core.notify("Ant OS", "main.py не найден")
            return False
        spec = importlib.util.spec_from_file_location("antapp", main_py)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, "open_app"):
            mod.open_app(os_core)
        elif hasattr(mod, "main"):
            mod.main(os_core)
        return True
    except Exception as e:
        os_core.notify("Ant OS", f"Ошибка: {e}")
        return False


def find_app_by_icon(icon_name):
    """Ищет приложение по иконке в Apps и SystemApps."""
    for app in list_apps():
        try:
            meta = read_app_meta(app["path"])
            if meta.get("icon", "").replace(".png", "") == icon_name:
                return app["path"]
        except Exception:
            pass
    for app in list_apps():
        if icon_name in app["file"].lower():
            return app["path"]
    return None


# ═══════════════════════════════════════════
#   🔊 SOUND
# ═══════════════════════════════════════════
class SoundManager:
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.cache = {}
        self.volume = 1.0

    def play(self, name):
        if not self.enabled:
            return False
        path = sound_path(name)
        if not path:
            return False
        try:
            from kivy.core.audio import SoundLoader
            if path not in self.cache:
                snd = SoundLoader.load(path)
                if snd:
                    snd.volume = self.volume
                    self.cache[path] = snd
            sound = self.cache.get(path)
            if sound:
                sound.play()
                return True
        except Exception as e:
            print(f"[Sound] {e}")
        return False

    def set_enabled(self, val):
        self.enabled = bool(val)


# ═══════════════════════════════════════════
#   🔒 FULL SCREEN
# ═══════════════════════════════════════════
def apply_fullscreen():
    try:
        from kivy.core.window import Window
        Window.fullscreen = "auto"
        Window.show_cursor = False
    except Exception as e:
        print(f"[FS] {e}")
    try:
        from jnius import autoclass
        from android.runnable import run_on_ui_thread
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        activity = PythonActivity.mActivity

        @run_on_ui_thread
        def hide_ui():
            try:
                View = autoclass("android.view.View")
                decor = activity.getWindow().getDecorView()
                flags = (View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                         | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                         | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                         | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                         | View.SYSTEM_UI_FLAG_FULLSCREEN
                         | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY)
                decor.setSystemUiVisibility(flags)
            except Exception:
                pass
        hide_ui()
    except Exception:
        pass


def remove_fullscreen():
    try:
        from kivy.core.window import Window
        Window.fullscreen = False
    except Exception:
        pass
    try:
        from jnius import autoclass
        from android.runnable import run_on_ui_thread
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        activity = PythonActivity.mActivity

        @run_on_ui_thread
        def show_ui():
            try:
                View = autoclass("android.view.View")
                decor = activity.getWindow().getDecorView()
                decor.setSystemUiVisibility(View.SYSTEM_UI_FLAG_VISIBLE)
            except Exception:
                pass
        show_ui()
    except Exception:
        pass


# ═══════════════════════════════════════════
#   ЯДРО
# ═══════════════════════════════════════════
class AntSystem:
    VERSION = "3.5.0"
    CODENAME = "Ant"
    DEVICE = "Redmi Note 14"

    def __init__(self):
        ensure_dirs()
        self.user = "user"
        self.wifi = True
        self.battery = 74
        self.wallpaper = ""
        self.fullscreen = True
        self.sound_enabled = True
        self.notifications = []
        self.running_apps = []
        self._load_settings()
        self.guard = AntGuard(self)
        self.guard.scan()
        self.sound = SoundManager(enabled=self.sound_enabled)

    @property
    def NAME(self):
        return "Ant OS"

    def _load_settings(self):
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    d = json.load(f)
                self.user = d.get("user", self.user)
                self.wifi = d.get("wifi", self.wifi)
                self.battery = d.get("battery", self.battery)
                self.wallpaper = d.get("wallpaper", "")
                self.fullscreen = d.get("fullscreen", self.fullscreen)
                self.sound_enabled = d.get("sound_enabled", self.sound_enabled)
        except Exception:
            pass

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump({"user": self.user, "wifi": self.wifi,
                           "battery": self.battery,
                           "wallpaper": self.wallpaper,
                           "fullscreen": self.fullscreen,
                           "sound_enabled": self.sound_enabled,
                           "version": self.VERSION}, f, indent=2)
        except Exception:
            pass

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.save_settings()
        if self.fullscreen:
            apply_fullscreen()
        else:
            remove_fullscreen()
        state = "ВКЛ" if self.fullscreen else "ВЫКЛ"
        self.notify("Ant OS", f"Полный экран: {state}")
        return self.fullscreen

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        self.sound.set_enabled(self.sound_enabled)
        self.save_settings()
        state = "ВКЛ" if self.sound_enabled else "ВЫКЛ"
        self.notify("Ant OS", f"Звуки: {state}")
        return self.sound_enabled

    def play(self, name):
        self.sound.play(name)

    def boot(self):
        print(f"Ant OS v{self.VERSION}")
        print(f"[AntGuard] {self.guard.status}")
        sys_apps = [a for a in list_apps() if a["system"]]
        usr_apps = [a for a in list_apps() if not a["system"]]
        print(f"[SystemApps] {len(sys_apps)}")
        print(f"[Apps]       {len(usr_apps)}")
        self.save_settings()

    def shutdown(self):
        self.save_settings()
        try:
            self.guard._save()
        except Exception:
            pass

    def unlock(self, pin="1234"):
        return pin == "1234"

    def notify(self, title, text):
        self.notifications.append({"title": title, "text": text})

    def launch(self, name):
        if name not in self.running_apps:
            self.running_apps.append(name)

    def set_wallpaper(self, filename):
        if wallpaper_path(filename) or filename == "":
            self.wallpaper = filename
            self.save_settings()
            return True
        return False

    def count_icons(self):
        names = ["phone","sms","camera","browser","music","gallery",
                 "settings","calc","wifi","battery","clock","info"]
        return [n for n in names if icon_path(n)]

    def status(self):
        sys_apps = [a for a in list_apps() if a["system"]]
        usr_apps = [a for a in list_apps() if not a["system"]]
        return (f"Ant OS v{self.VERSION}\n"
                f"Иконок: {len(self.count_icons())}/12\n"
                f"Обоев: {len(list_wallpapers())}\n"
                f"Системных: {len(sys_apps)}\n"
                f"Пользовательских: {len(usr_apps)}\n"
                f"Full Screen: {'ВКЛ' if self.fullscreen else 'ВЫКЛ'}\n"
                f"Звуки: {'ВКЛ' if self.sound_enabled else 'ВЫКЛ'}\n"
                f"AntGuard: {self.guard.status}")


# ═══════════════════════════════════════════
#   UI
# ═══════════════════════════════════════════
try:
    from kivy.app import App
    from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.behaviors import ButtonBehavior
    from kivy.uix.image import Image
    from kivy.uix.progressbar import ProgressBar
    from kivy.uix.popup import Popup
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.floatlayout import FloatLayout
    from kivy.graphics import Color, Rectangle
    from kivy.clock import Clock
    from kivy.animation import Animation
    from kivy.metrics import dp, sp
    from kivy.utils import get_color_from_hex
    KIVY_OK = True
except ImportError as e:
    KIVY_OK = False
    KIVY_ERROR = str(e)


if KIVY_OK:
    ORANGE = get_color_from_hex("#FF6A00")
    BLACK = (0, 0, 0, 1)
    GRAY = get_color_from_hex("#1A1A1A")
    TEXT = (1, 1, 1, 1)
    MUTED = get_color_from_hex("#888888")
    GREEN = (0.2, 0.9, 0.3, 1)
    RED = (1, 0.2, 0.2, 1)
    YELLOW = (1, 0.8, 0.2, 1)
    BLUE = (0.3, 0.6, 1, 1)


    class ColoredBox(BoxLayout):
        def __init__(self, bg_color=BLACK, **kw):
            super().__init__(**kw)
            with self.canvas.before:
                Color(*bg_color)
                self._r = Rectangle(pos=self.pos, size=self.size)
            self.bind(pos=self._u, size=self._u)
        def _u(self, *a):
            self._r.pos = self.pos
            self._r.size = self.size


    class StatusDot(Label):
        def __init__(self, color=GREEN, **kw):
            super().__init__(text="●", font_size=sp(12), color=color,
                             size_hint=(None, None), size=(dp(14), dp(20)),
                             halign="center", valign="middle", **kw)


    class AppIcon(ButtonBehavior, BoxLayout):
        def __init__(self, icon_name, letter, size=dp(60), **kw):
            super().__init__(orientation="vertical",
                             size_hint=(None, None),
                             size=(size, size), **kw)
            p = icon_path(icon_name)
            if p:
                self.add_widget(Image(source=p,
                                      size_hint=(None, None),
                                      size=(size, size),
                                      allow_stretch=True, keep_ratio=True,
                                      nocache=True))
            else:
                lbl = Label(text=letter, font_size=sp(28), bold=True,
                            color=ORANGE, halign="center", valign="middle")
                lbl.bind(size=lambda *_: setattr(lbl, "text_size", lbl.size))
                self.add_widget(lbl)


    class NavButton(ButtonBehavior, BoxLayout):
        def __init__(self, png_name, fallback, size=dp(55), **kw):
            super().__init__(orientation="vertical",
                             size_hint=(None, None),
                             size=(size, size), **kw)
            p = icon_path(png_name)
            if p:
                self.add_widget(Image(source=p,
                                      size_hint=(None, None),
                                      size=(dp(44), dp(44)),
                                      pos_hint={"center_x": 0.5, "center_y": 0.5},
                                      allow_stretch=True, keep_ratio=True,
                                      nocache=True))
            else:
                lbl = Label(text=fallback, font_size=sp(28), bold=True,
                            color=ORANGE, halign="center", valign="middle")
                lbl.bind(size=lambda *_: setattr(lbl, "text_size", lbl.size))
                self.add_widget(lbl)


    class BootScreen(Screen):
        def __init__(self, os_core, on_done, **kw):
            super().__init__(**kw)
            self.os = os_core
            self.on_done = on_done
            root = ColoredBox(orientation="vertical", bg_color=BLACK,
                              padding=dp(30), spacing=dp(15))
            root.add_widget(BoxLayout(size_hint_y=0.15))
            logo = logo_path()
            if logo:
                li = Image(source=logo, size_hint=(None, None),
                           size=(dp(200), dp(200)),
                           pos_hint={"center_x": 0.5},
                           allow_stretch=True, keep_ratio=True, nocache=True)
                root.add_widget(li)
                li.opacity = 0
                Animation(opacity=1, duration=1.2).start(li)
            else:
                root.add_widget(Label(text="A", font_size=sp(120),
                                      color=ORANGE,
                                      size_hint_y=None, height=dp(140)))
            root.add_widget(BoxLayout(size_hint_y=0.05))
            root.add_widget(Label(text="Ant OS", font_size=sp(36),
                                  color=TEXT, bold=True,
                                  size_hint_y=None, height=dp(55)))
            root.add_widget(Label(text=f"v{self.os.VERSION}",
                                  font_size=sp(14), color=MUTED,
                                  size_hint_y=None, height=dp(30)))
            root.add_widget(BoxLayout(size_hint_y=0.15))
            self.progress = ProgressBar(max=100, value=0,
                                        size_hint_y=None, height=dp(6))
            root.add_widget(self.progress)
            self.lbl = Label(text="Инициализация...", font_size=sp(13),
                             color=MUTED,
                             size_hint_y=None, height=dp(30))
            root.add_widget(self.lbl)
            self.add_widget(root)
            Clock.schedule_once(self._start, 0.5)

        def _start(self, dt):
            self.os.play("boot")
            self._steps = [(25, "Ядро..."), (50, "Datas/..."),
                           (75, "AntGuard..."), (100, "Готово")]
            self._i = 0
            Clock.schedule_interval(self._tick, 0.5)

        def _tick(self, dt):
            if self._i >= len(self._steps):
                Clock.unschedule(self._tick)
                self.os.boot()
                Clock.schedule_once(lambda *_: self.on_done(), 0.4)
                return
            v, t = self._steps[self._i]
            Animation(value=v, duration=0.3).start(self.progress)
            self.lbl.text = t
            self._i += 1


    class LockScreen(Screen):
        def __init__(self, os_core, on_unlock, **kw):
            super().__init__(**kw)
            self.os = os_core
            self.on_unlock = on_unlock
            root = ColoredBox(orientation="vertical",
                              bg_color=get_color_from_hex("#0A0E1A"),
                              padding=dp(30), spacing=dp(10))
            root.add_widget(BoxLayout(size_hint_y=0.12))
            self.clock = Label(text="", font_size=sp(72), color=TEXT,
                               size_hint_y=None, height=dp(90),
                               halign="center", valign="middle")
            self.clock.bind(size=lambda *_: setattr(self.clock, "text_size", self.clock.size))
            root.add_widget(self.clock)
            self.date = Label(text="", font_size=sp(16), color=MUTED,
                              size_hint_y=None, height=dp(30))
            root.add_widget(self.date)
            root.add_widget(BoxLayout(size_hint_y=0.15))
            logo = logo_path()
            if logo:
                root.add_widget(Image(source=logo, size_hint=(None, None),
                                      size=(dp(90), dp(90)),
                                      pos_hint={"center_x": 0.5},
                                      allow_stretch=True, keep_ratio=True,
                                      nocache=True))
            root.add_widget(BoxLayout(size_hint_y=0.15))
            btn = Button(text="РАЗБЛОКИРОВАТЬ", font_size=sp(16), bold=True,
                         size_hint=(None, None), size=(dp(240), dp(56)),
                         pos_hint={"center_x": 0.5},
                         background_normal="", background_color=ORANGE,
                         color=BLACK)
            btn.bind(on_release=self._unlock)
            root.add_widget(btn)
            root.add_widget(Label(text="PIN: 1234", font_size=sp(12),
                                  color=MUTED,
                                  size_hint_y=None, height=dp(30)))
            self.add_widget(root)
            Clock.schedule_interval(self._upd, 1)

        def _upd(self, dt):
            n = datetime.datetime.now()
            self.clock.text = n.strftime("%H:%M")
            months = ["января","февраля","марта","апреля","мая","июня",
                      "июля","августа","сентября","октября","ноября","декабря"]
            days = ["Пн","Вт","Ср","Чт","Пт","Сб","Вс"]
            self.date.text = f"{days[n.weekday()]}, {n.day} {months[n.month-1]}"

        def _unlock(self, *a):
            if self.os.unlock("1234"):
                self.os.play("unlock")
                self.on_unlock()


    class HomeScreen(Screen):
        def __init__(self, os_core, **kw):
            super().__init__(**kw)
            self.os = os_core
            self.wall_img = None
            base = FloatLayout()
            self.base = base
            self._apply_wall()
            overlay = BoxLayout(orientation="vertical")

            bar = ColoredBox(orientation="horizontal",
                             bg_color=(0, 0, 0, 0.7),
                             size_hint_y=None, height=dp(30),
                             padding=(dp(12), dp(2), dp(12), dp(2)),
                             spacing=dp(6))
            self.time_lbl = Label(text="", font_size=sp(12), color=TEXT,
                                  halign="left", valign="middle")
            self.time_lbl.bind(size=lambda *_: setattr(self.time_lbl, "text_size", self.time_lbl.size))
            bar.add_widget(self.time_lbl)
            right = BoxLayout(orientation="horizontal", size_hint_x=None,
                              width=dp(140), spacing=dp(4))
            self.guard_dot = StatusDot(color=self.os.guard.get_color())
            right.add_widget(self.guard_dot)
            wp = icon_path("wifi")
            if wp:
                right.add_widget(Image(source=wp, size_hint=(None, None),
                                       size=(dp(18), dp(18)),
                                       allow_stretch=True, keep_ratio=True,
                                       nocache=True))
            bp = icon_path("battery")
            if bp:
                right.add_widget(Image(source=bp, size_hint=(None, None),
                                       size=(dp(18), dp(18)),
                                       allow_stretch=True, keep_ratio=True,
                                       nocache=True))
            right.add_widget(Label(text=f"{self.os.battery}%",
                                   font_size=sp(12), color=TEXT,
                                   size_hint_x=None, width=dp(38),
                                   halign="right", valign="middle"))
            bar.add_widget(right)
            overlay.add_widget(bar)
            overlay.add_widget(BoxLayout(size_hint_y=None, height=dp(20)))

            grid = GridLayout(cols=4, spacing=dp(6), padding=dp(10),
                              size_hint_y=None)
            grid.bind(minimum_height=grid.setter("height"))
            apps = [
                ("phone",    "T",  "Телефон"),
                ("sms",      "S",  "SMS"),
                ("camera",   "C",  "Камера"),
                ("browser",  "W",  "Браузер"),
                ("music",    "M",  "Музыка"),
                ("gallery",  "G",  "Галерея"),
                ("settings", "N",  "Настройки"),
                ("calc",     "=",  "Калькул."),
                ("wifi",     "Wi", "Wi-Fi"),
                ("battery",  "BT", "Батарея"),
                ("clock",    "O",  "Часы"),
                ("info",     "i",  "Инфо"),
                ("antivirus","AV", "Antivirus"),
            ]
            for n, l, label in apps:
                grid.add_widget(self._icon(n, l, label))
            overlay.add_widget(grid)
            overlay.add_widget(BoxLayout())

            dock = ColoredBox(orientation="horizontal",
                              bg_color=(0, 0, 0, 0.7),
                              size_hint_y=None, height=dp(65),
                              spacing=dp(20),
                              padding=(dp(40), dp(8), dp(40), dp(8)))
            for n, l in [("phone","T"),("sms","S"),
                         ("browser","W"),("settings","N")]:
                d = AppIcon(n, l, size=dp(50))
                d.bind(on_release=lambda x, nn=n: self._launch(nn))
                dock.add_widget(d)
            overlay.add_widget(dock)

            nav = ColoredBox(orientation="horizontal",
                             bg_color=(0, 0, 0, 0.95),
                             size_hint_y=None, height=dp(65),
                             spacing=dp(15),
                             padding=(dp(30), dp(4), dp(30), dp(4)))
            b1 = NavButton("back", "◀", size=dp(55))
            b1.bind(on_release=self._nav_back)
            nav.add_widget(b1)
            b2 = NavButton("window", "■", size=dp(55))
            b2.bind(on_release=self._nav_window)
            nav.add_widget(b2)
            b3 = NavButton("home", "⌂", size=dp(55))
            b3.bind(on_release=self._nav_home)
            nav.add_widget(b3)
            overlay.add_widget(nav)

            base.add_widget(overlay)
            self.add_widget(base)
            Clock.schedule_interval(self._tick, 1)

        def _icon(self, name, letter, label):
            box = BoxLayout(orientation="vertical",
                            size_hint_y=None, height=dp(90))
            ic = AppIcon(name, letter, size=dp(60))
            ic.pos_hint = {"center_x": 0.5}
            ic.bind(on_release=lambda x, n=label: self._launch(n))
            box.add_widget(ic)
            box.add_widget(Label(text=label, font_size=sp(11), color=TEXT,
                                 size_hint_y=None, height=dp(22),
                                 halign="center", valign="middle"))
            return box

        def _apply_wall(self):
            if self.wall_img and self.wall_img in self.base.children:
                self.base.remove_widget(self.wall_img)
            self.wall_img = None
            w = wallpaper_path(self.os.wallpaper)
            if w:
                self.wall_img = Image(source=w, allow_stretch=True,
                                      keep_ratio=False, nocache=True, opacity=0.55)
                self.base.add_widget(self.wall_img)

        def _launch(self, name):
            self.os.launch(name)
            self.os.play("click")
            if name == "Antivirus":
                self._popup_guard()
                return
            if name == "Калькул.":
                f = find_app_by_icon("calc")
                if f:
                    run_pyapp(f, self.os)
                else:
                    self._popup("Калькулятор",
                                "Не найдено.\n"
                                "Положи calculator.zip в SystemApps/")
                return
            if name == "Инфо":
                text = self.os.status()
            elif name == "Настройки":
                self._popup_settings(); return
            elif name == "Батарея":
                text = f"Батарея: {self.os.battery}%"
            elif name == "Wi-Fi":
                text = f"Wi-Fi: {'ВКЛ' if self.os.wifi else 'ВЫКЛ'}"
            elif name == "Часы":
                text = datetime.datetime.now().strftime("%H:%M:%S")
            else:
                text = f"«{name}»\n\nв разработке"
            self._popup(name, text)

        def _popup(self, title, text):
            c = ColoredBox(orientation="vertical", bg_color=GRAY,
                           padding=dp(20), spacing=dp(15))
            c.add_widget(Label(text=text, font_size=sp(15), color=TEXT,
                               halign="center", valign="middle"))
            b = Button(text="OK", font_size=sp(16), background_normal="",
                       background_color=ORANGE, color=BLACK,
                       size_hint_y=None, height=dp(48))
            c.add_widget(b)
            p = Popup(title=title, title_color=ORANGE, title_size=sp(18),
                      content=c, size_hint=(0.85, None), height=dp(280),
                      background="", background_color=(0,0,0,0.9),
                      separator_color=ORANGE)
            b.bind(on_release=p.dismiss)
            p.open()

        def _popup_settings(self):
            c = ColoredBox(orientation="vertical", bg_color=GRAY,
                           padding=dp(20), spacing=dp(10))
            sys_apps = [a for a in list_apps() if a["system"]]
            usr_apps = [a for a in list_apps() if not a["system"]]
            for txt in [
                f"Wi-Fi: {'ВКЛ' if self.os.wifi else 'ВЫКЛ'}",
                f"Батарея: {self.os.battery}%", "-"*20,
                f"Ant OS v{self.os.VERSION}",
                f"Иконок: {len(self.os.count_icons())}/12",
                f"Обоев: {len(list_wallpapers())}",
                f"⭐ Системных: {len(sys_apps)}",
                f"📦 Пользовательских: {len(usr_apps)}",
                f"AntGuard: {self.os.guard.status}",
            ]:
                c.add_widget(Label(text=txt, font_size=sp(14), color=TEXT,
                                   size_hint_y=None, height=dp(30), halign="left"))

            snd_text = f"🔊 Звуки: {'ВКЛ' if self.os.sound_enabled else 'ВЫКЛ'}"
            snd_btn = Button(text=snd_text, font_size=sp(14),
                             background_normal="", background_color=GRAY,
                             color=ORANGE, size_hint_y=None, height=dp(42))
            def toggle_snd(x):
                self.os.toggle_sound()
                snd_btn.text = f"🔊 Звуки: {'ВКЛ' if self.os.sound_enabled else 'ВЫКЛ'}"
                self.os.play("click")
            snd_btn.bind(on_release=toggle_snd)
            c.add_widget(snd_btn)

            fs_text = f"🔒 Полный экран: {'ВКЛ' if self.os.fullscreen else 'ВЫКЛ'}"
            fs_btn = Button(text=fs_text, font_size=sp(14),
                            background_normal="", background_color=GRAY,
                            color=ORANGE, size_hint_y=None, height=dp(42))
            def toggle_fs(x):
                self.os.toggle_fullscreen()
                fs_btn.text = f"🔒 Полный экран: {'ВКЛ' if self.os.fullscreen else 'ВЫКЛ'}"
            fs_btn.bind(on_release=toggle_fs)
            c.add_widget(fs_btn)

            gb_box = BoxLayout(orientation="horizontal",
                               size_hint_y=None, height=dp(50),
                               spacing=dp(10))
            antiv = icon_path("antivirus")
            if antiv:
                gb_box.add_widget(Image(source=antiv,
                                        size_hint=(None, None),
                                        size=(dp(40), dp(40)),
                                        allow_stretch=True, keep_ratio=True,
                                        nocache=True))
            gb = Button(text="Antivirus by Ant OS", font_size=sp(14),
                        background_normal="", background_color=GRAY,
                        color=ORANGE)
            gb.bind(on_release=lambda x: self._popup_guard())
            gb_box.add_widget(gb)
            c.add_widget(gb_box)

            wb = Button(text="Сменить обои", font_size=sp(14),
                        background_normal="", background_color=GRAY,
                        color=ORANGE, size_hint_y=None, height=dp(42))
            wb.bind(on_release=lambda x: self._popup_walls())
            c.add_widget(wb)

            ab = Button(text="📦 Все приложения", font_size=sp(14),
                        background_normal="", background_color=GRAY,
                        color=ORANGE, size_hint_y=None, height=dp(42))
            ab.bind(on_release=lambda x: self._popup_apps())
            c.add_widget(ab)

            b = Button(text="Закрыть", font_size=sp(16),
                       background_normal="", background_color=ORANGE,
                       color=BLACK, size_hint_y=None, height=dp(48))
            c.add_widget(b)
            p = Popup(title="Настройки", title_color=ORANGE, title_size=sp(18),
                      content=c, size_hint=(0.9, None), height=dp(800),
                      background="", background_color=(0,0,0,0.9),
                      separator_color=ORANGE)
            b.bind(on_release=p.dismiss)
            p.open()

        def _popup_apps(self):
            """📋 Список ВСЕХ приложений — системные + пользовательские."""
            apps = list_apps()
            c = ColoredBox(orientation="vertical", bg_color=GRAY,
                           padding=dp(15), spacing=dp(8))

            if not apps:
                c.add_widget(Label(
                    text="Нет приложений\n\n"
                         "⭐ SystemApps/ — системные\n"
                         "📦 Apps/ — пользовательские",
                    font_size=sp(14), color=MUTED,
                    halign="center", valign="middle"))
            else:
                sc = ScrollView()
                inner = BoxLayout(orientation="vertical",
                                  size_hint_y=None, spacing=dp(6))
                inner.bind(minimum_height=inner.setter("height"))

                # Сначала системные
                sys_apps = [a for a in apps if a["system"]]
                usr_apps = [a for a in apps if not a["system"]]

                if sys_apps:
                    lbl = Label(text=f"⭐ СИСТЕМНЫЕ ({len(sys_apps)})",
                                font_size=sp(12), bold=True, color=ORANGE,
                                size_hint_y=None, height=dp(24),
                                halign="left")
                    lbl.bind(size=lambda *_: setattr(lbl, "text_size", lbl.size))
                    inner.add_widget(lbl)

                    for a in sys_apps:
                        meta = read_app_meta(a["path"])
                        name = meta.get("name", a["file"])
                        btn = Button(
                            text=f"⭐ {name}\n   {a['file']}",
                            font_size=sp(13),
                            background_normal="",
                            background_color=get_color_from_hex("#2A1A0A"),
                            color=ORANGE,
                            size_hint_y=None, height=dp(60))
                        btn.bind(on_release=lambda x, p=a["path"]:
                                 (run_pyapp(p, self.os), popup.dismiss()))
                        inner.add_widget(btn)

                if usr_apps:
                    lbl = Label(text=f"📦 ПОЛЬЗОВАТЕЛЬСКИЕ ({len(usr_apps)})",
                                font_size=sp(12), bold=True, color=BLUE,
                                size_hint_y=None, height=dp(24),
                                halign="left")
                    lbl.bind(size=lambda *_: setattr(lbl, "text_size", lbl.size))
                    inner.add_widget(lbl)

                    for a in usr_apps:
                        meta = read_app_meta(a["path"])
                        name = meta.get("name", a["file"])
                        btn = Button(
                            text=f"📦 {name}\n   {a['file']}",
                            font_size=sp(13),
                            background_normal="", background_color=GRAY,
                            color=TEXT,
                            size_hint_y=None, height=dp(60))
                        btn.bind(on_release=lambda x, p=a["path"]:
                                 (run_pyapp(p, self.os), popup.dismiss()))
                        inner.add_widget(btn)

                sc.add_widget(inner)
                c.add_widget(sc)

            b = Button(text="Закрыть", font_size=sp(16),
                       background_normal="", background_color=ORANGE,
                       color=BLACK, size_hint_y=None, height=dp(48))
            c.add_widget(b)
            popup = Popup(title="📱 Приложения Ant OS",
                          title_color=ORANGE, title_size=sp(18),
                          content=c, size_hint=(0.9, 0.8),
                          background="", background_color=(0,0,0,0.95),
                          separator_color=ORANGE)
            b.bind(on_release=popup.dismiss)
            popup.open()

        def _popup_walls(self):
            walls = list_wallpapers()
            c = ColoredBox(orientation="vertical", bg_color=GRAY,
                           padding=dp(10), spacing=dp(8))
            if not walls:
                c.add_widget(Label(text="Нет обоев", font_size=sp(14),
                                   color=MUTED,
                                   halign="center", valign="middle"))
            else:
                sc = ScrollView()
                inner = BoxLayout(orientation="vertical",
                                  size_hint_y=None, spacing=dp(6))
                inner.bind(minimum_height=inner.setter("height"))
                rb = Button(text="[ Чёрный ]", font_size=sp(14),
                            background_normal="", background_color=BLACK,
                            color=ORANGE, size_hint_y=None, height=dp(50))
                rb.bind(on_release=lambda x: self._set_wall("", popup))
                inner.add_widget(rb)
                for w in walls:
                    b = Button(text=w, font_size=sp(14), background_normal="",
                               background_color=GRAY, color=TEXT,
                               size_hint_y=None, height=dp(50))
                    b.bind(on_release=lambda x, ww=w: self._set_wall(ww, popup))
                    inner.add_widget(b)
                sc.add_widget(inner)
                c.add_widget(sc)
            b = Button(text="Отмена", font_size=sp(16), background_normal="",
                       background_color=ORANGE, color=BLACK,
                       size_hint_y=None, height=dp(48))
            c.add_widget(b)
            popup = Popup(title="Обои", title_color=ORANGE, title_size=sp(18),
                          content=c, size_hint=(0.9, 0.7),
                          background="", background_color=(0,0,0,0.95),
                          separator_color=ORANGE)
            b.bind(on_release=popup.dismiss)
            popup.open()

        def _set_wall(self, filename, popup=None):
            if self.os.set_wallpaper(filename):
                self.os.notify("Ant OS", f"Обои: {filename or 'чёрный'}")
            if popup:
                popup.dismiss()
            self._apply_wall()

        def _popup_guard(self):
            g = self.os.guard
            c = ColoredBox(orientation="vertical", bg_color=GRAY,
                           padding=dp(12), spacing=dp(8))

            antiv = icon_path("antivirus")
            if antiv:
                c.add_widget(Image(source=antiv,
                                   size_hint=(None, None),
                                   size=(dp(90), dp(90)),
                                   pos_hint={"center_x": 0.5},
                                   allow_stretch=True, keep_ratio=True,
                                   nocache=True))

            c.add_widget(Label(text=g.get_status_text(), font_size=sp(14),
                               bold=True, color=g.get_color(),
                               size_hint_y=None, height=dp(30),
                               halign="center"))

            c.add_widget(Label(
                text=f"Файлов: {g.scanned}  |  Скриптов: {g.scanned_code}  |  Угроз: {len(g.threats)}",
                font_size=sp(12), color=MUTED,
                size_hint_y=None, height=dp(22),
                halign="center"))
            c.add_widget(Label(
                text=f"Последняя: {g.last_scan or '—'}",
                font_size=sp(11), color=MUTED,
                size_hint_y=None, height=dp(20),
                halign="center"))

            if not g.threats:
                c.add_widget(Label(text="Все файлы безопасны",
                                   font_size=sp(12), color=GREEN,
                                   size_hint_y=None, height=dp(30),
                                   halign="center", valign="middle"))

            if g.threats:
                c.add_widget(Label(text=f"⚠ Угроз: {len(g.threats)}",
                                   font_size=sp(13), bold=True, color=RED,
                                   size_hint_y=None, height=dp(25),
                                   halign="center"))
                sc = ScrollView(size_hint=(1, 1))
                inner = BoxLayout(orientation="vertical",
                                  size_hint_y=None, spacing=dp(4))
                inner.bind(minimum_height=inner.setter("height"))
                for t in g.threats[:30]:
                    level = t.get("level", "?")
                    color = {"HIGH": RED, "MEDIUM": YELLOW,
                             "LOW": MUTED}.get(level, TEXT)
                    text = (f"[{level}] {t.get('folder','')}/{t.get('file','')}\n"
                            f"   → {t.get('desc','')}")
                    lbl = Label(text=text, font_size=sp(11), color=color,
                                size_hint_y=None, height=dp(40),
                                halign="left", valign="middle")
                    lbl.bind(size=lambda *_: setattr(lbl, "text_size", lbl.size))
                    inner.add_widget(lbl)
                sc.add_widget(inner)
                c.add_widget(sc)

            btn_row = BoxLayout(orientation="horizontal",
                                size_hint_y=None, height=dp(46),
                                spacing=dp(8))
            scan_btn = Button(text="🔍 Сканировать", font_size=sp(13),
                              background_normal="", background_color=ORANGE,
                              color=BLACK)
            scan_btn.bind(on_release=lambda x: (
                self.os.guard.scan(), popup.dismiss(), self._popup_guard()))
            btn_row.add_widget(scan_btn)

            if g.threats:
                q_btn = Button(text="🛡️ Карантин", font_size=sp(13),
                               background_normal="", background_color=RED,
                               color=(1, 1, 1, 1))
                q_btn.bind(on_release=lambda x: (
                    self.os.guard.quarantine(), popup.dismiss(),
                    self._popup_guard()))
                btn_row.add_widget(q_btn)
            c.add_widget(btn_row)

            b = Button(text="Закрыть", font_size=sp(15),
                       background_normal="", background_color=GRAY,
                       color=ORANGE,
                       size_hint_y=None, height=dp(46))
            c.add_widget(b)

            popup = Popup(title="🛡️ Antivirus by Ant OS",
                          title_color=ORANGE, title_size=sp(18),
                          content=c, size_hint=(0.95, 0.9),
                          background="", background_color=(0,0,0,0.95),
                          separator_color=ORANGE)
            b.bind(on_release=popup.dismiss)
            popup.open()

        def _nav_back(self, *a):
            from kivy.core.window import Window
            for w in list(Window.children):
                if isinstance(w, Popup):
                    try: w.dismiss()
                    except Exception: pass

        def _nav_window(self, *a):
            apps = self.os.running_apps[:]
            c = ColoredBox(orientation="vertical", bg_color=GRAY,
                           padding=dp(15), spacing=dp(8))
            c.add_widget(Label(text=f"Запущено: {len(apps)}",
                               font_size=sp(15), bold=True, color=ORANGE,
                               size_hint_y=None, height=dp(30)))
            if not apps:
                c.add_widget(Label(text="Нет", font_size=sp(14),
                                   color=MUTED,
                                   halign="center", valign="middle"))
            else:
                for app in apps:
                    c.add_widget(Label(text=f"• {app}", font_size=sp(13),
                                       color=TEXT,
                                       size_hint_y=None, height=dp(28)))
            b = Button(text="Закрыть", font_size=sp(16), background_normal="",
                       background_color=ORANGE, color=BLACK,
                       size_hint_y=None, height=dp(48))
            c.add_widget(b)
            p = Popup(title="Запущенные", title_color=ORANGE,
                      title_size=sp(18), content=c,
                      size_hint=(0.9, 0.7),
                      background="", background_color=(0,0,0,0.95),
                      separator_color=ORANGE)
            b.bind(on_release=p.dismiss)
            p.open()

        def _nav_home(self, *a):
            from kivy.core.window import Window
            for w in list(Window.children):
                if isinstance(w, Popup):
                    try: w.dismiss()
                    except Exception: pass

        def _tick(self, *a):
            self.time_lbl.text = datetime.datetime.now().strftime("%H:%M | %d.%m")
            try:
                self.guard_dot.color = self.os.guard.get_color()
            except Exception:
                pass


    class AntOSApp(App):
        def build(self):
            self.title = "Ant OS"
            fs = True
            try:
                if os.path.exists(SETTINGS_FILE):
                    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                        fs = json.load(f).get("fullscreen", True)
            except Exception:
                pass
            if fs:
                apply_fullscreen()
            else:
                remove_fullscreen()

            self.os = AntSystem()
            sm = ScreenManager(transition=FadeTransition(duration=0.4))
            sm.add_widget(BootScreen(self.os,
                on_done=lambda: setattr(sm, "current", "lock"), name="boot"))
            sm.add_widget(LockScreen(self.os,
                on_unlock=lambda: setattr(sm, "current", "home"), name="lock"))
            sm.add_widget(HomeScreen(self.os, name="home"))
            sm.current = "boot"
            return sm

        def on_stop(self):
            remove_fullscreen()
            self.os.shutdown()


if __name__ == "__main__":
    print("=" * 46)
    print(f"  ANT OS v{AntSystem.VERSION}")
    print("=" * 46)
    ensure_dirs()
    sys_apps = [a for a in list_apps() if a["system"]]
    usr_apps = [a for a in list_apps() if not a["system"]]
    print(f"  ⭐ SystemApps: {len(sys_apps)}")
    for a in sys_apps:
        print(f"      {a['file']}")
    print(f"  📦 Apps: {len(usr_apps)}")
    for a in usr_apps:
        print(f"      {a['file']}")
    test_os = AntSystem()
    print()
    print(test_os.status())
    print()
    if KIVY_OK:
        print("Kivy OK — запуск...\n")
        AntOSApp().run()
    else:
        print(f"Kivy: {KIVY_ERROR}")
