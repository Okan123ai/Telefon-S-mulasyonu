import ast
import json
import math
import operator
import os
import secrets
import shutil
import tempfile
import time
import tkinter as tk
import webbrowser
from datetime import datetime
from pathlib import Path
from string import ascii_letters, digits, punctuation
from tkinter import filedialog, messagebox, ttk
from urllib.parse import quote_plus


BG = "#10131c"
CARD = "#202536"
TEXT = "#f4f6ff"
MUTED = "#aab1c5"
ACCENT = "#7c8cff"
DATA_FILE = Path(__file__).with_name("telefon_verileri.json")
BACKUP_FILE = DATA_FILE.with_suffix(".json.bak")

DEFAULT_DATA = {
    "contacts": [],
    "conversations": {},
    "notes": [],
    "events": [],
    "recent_calls": [],
    "settings": {"wifi": True, "bluetooth": False, "sound": True, "brightness": 75},
    "installed_apps": [],
    "tasks": [],
    "shopping_list": [],
    "journal": [],
    "photos": [],
    "save_metadata": {"schema_version": 2, "saved_at": ""},
    "device": {
        "version": "Android 14",
        "setup_complete": True,
        "name": "Telefonum",
        "account_skipped": True,
    },
}

BUILTIN_APPS = [
    {"id": "store", "name": "Play Store", "icon": "▶", "color": "#2684fc"},
    {"id": "phone", "name": "Telefon", "icon": "☎", "color": "#35a96f"},
    {"id": "messages", "name": "Mesajlar", "icon": "✉", "color": "#4388dd"},
    {"id": "contacts", "name": "Kişiler", "icon": "●", "color": "#e7893e"},
    {"id": "settings", "name": "Ayarlar", "icon": "⚙", "color": "#788398"},
    {"id": "calculator", "name": "Hesap Mak.", "icon": "▦", "color": "#8764d9"},
    {"id": "gallery", "name": "Galeri", "icon": "▧", "color": "#d9658b"},
    {"id": "notes", "name": "Notlar", "icon": "▤", "color": "#ceaa42"},
    {"id": "calendar", "name": "Takvim", "icon": "▣", "color": "#db625e"},
    {"id": "clock", "name": "Saat", "icon": "◷", "color": "#448f98"},
    {"id": "browser", "name": "İnternet", "icon": "◎", "color": "#4182a7"},
    {"id": "files", "name": "Dosyalar", "icon": "▱", "color": "#598c53"},
    {"id": "saves", "name": "Kayıt Merkezi", "icon": "▣", "color": "#6177bd"},
]

STORE_APPS = [
    {
        "id": "tasks", "name": "Yapılacaklar", "icon": "✓", "color": "#3b9b80",
        "description": "Görev ekle, tamamla ve listeni sakla.",
    },
    {
        "id": "weather", "name": "Hava Durumu", "icon": "☀", "color": "#e29c42",
        "description": "Şehir seçerek çevrimdışı demo hava bilgisini gör.",
    },
    {
        "id": "converter", "name": "Birim Dönüştürücü", "icon": "⇄", "color": "#5687c5",
        "description": "Uzunluk, ağırlık ve sıcaklık dönüştür.",
    },
    {
        "id": "timer", "name": "Zamanlayıcı", "icon": "◴", "color": "#b96568",
        "description": "Geri sayım başlat, duraklat ve sıfırla.",
    },
    {
        "id": "journal", "name": "Günlük", "icon": "✎", "color": "#9a72bd",
        "description": "Tarihli günlük kayıtları oluştur ve sil.",
    },
    {
        "id": "password", "name": "Şifre Üretici", "icon": "⚿", "color": "#587c62",
        "description": "Yerel olarak güçlü ve rastgele şifre üret.",
    },
    {
        "id": "shopping", "name": "Alışveriş Listesi", "icon": "▤", "color": "#c27445",
        "description": "Alışveriş ürünlerini ekle ve listeden kaldır.",
    },
]

APP_ACTIONS = {
    "store": "show_store",
    "phone": "show_phone",
    "messages": "show_messages",
    "contacts": "show_contacts",
    "settings": "show_settings",
    "calculator": "show_calculator",
    "gallery": "show_gallery",
    "notes": "show_notes",
    "calendar": "show_calendar",
    "clock": "show_clock",
    "browser": "show_browser",
    "files": "show_files",
    "saves": "show_save_center",
    "tasks": "show_tasks",
    "weather": "show_weather",
    "converter": "show_converter",
    "timer": "show_timer",
    "journal": "show_journal",
    "password": "show_password_generator",
    "shopping": "show_shopping_list",
}

ANDROID_VERSIONS = [
    {
        "name": "Android 8.1 Oreo",
        "version": "Android 8.1",
        "codename": "Oreo",
        "description": "Klasik uygulama çekmecesi ve sade görünüm",
        "layout": "oreo",
        "colors": ("#dce8f4", "#f8fbff", "#172b40", "#5b7187", "#3276bd"),
    },
    {
        "name": "Android 10",
        "version": "Android 10",
        "codename": "Q",
        "description": "Minimal simgeler ve koyu renkli arayüz",
        "layout": "minimal",
        "colors": ("#090a0d", "#17191e", "#f5f5f5", "#92959d", "#d0d2d7"),
    },
    {
        "name": "Android 12",
        "version": "Android 12",
        "codename": "Snow Cone",
        "description": "Pastel renkler ve Material tarzı kartlar",
        "layout": "material12",
        "colors": ("#eee9f8", "#faf7ff", "#281f37", "#756985", "#7652c8"),
    },
    {
        "name": "Android 13",
        "version": "Android 13",
        "codename": "Tiramisu",
        "description": "Yumuşak yeşil tonlar ve düzenli uygulama ızgarası",
        "layout": "material13",
        "colors": ("#e4f1e7", "#f6fbf5", "#1a3022", "#617566", "#23834b"),
    },
    {
        "name": "Android 14",
        "version": "Android 14",
        "codename": "Upside Down Cake",
        "description": "Koyu duvar kâğıdı ve modern ana ekran",
        "layout": "pixel14",
        "colors": ("#101426", "#202944", "#f7f5ff", "#b9c3e8", "#9b8cff"),
    },
    {
        "name": "Android 15",
        "version": "Android 15",
        "codename": "Vanilla Ice Cream",
        "description": "Yeni nesil koyu tema ve canlı vurgu renkleri",
        "layout": "pixel15",
        "colors": ("#071e22", "#12363a", "#e7fffb", "#98c8c3", "#00c9a7"),
    },
]


class PhoneSimulator:
    def __init__(self, root):
        self.root = root
        root.title("Telefon Simülasyonu")
        root.configure(bg="#090b10")
        root.resizable(False, False)

        self.data = self.load_data()
        self.apply_android_theme(self.data["device"]["version"])
        self.call_started = None
        self.call_number = ""
        self.current_directory = Path.home()
        self.stopwatch_started = None
        self.stopwatch_elapsed = 0.0
        self.stopwatch_job = None
        self.call_pulse_job = None
        self.call_pulse_phase = 0
        self.install_job = None
        self.install_version = None
        self.install_progress = 0
        self.setup_step = 0
        self.setup_values = {}
        self.setup_widgets = {}
        self.timer_job = None
        self.timer_deadline = None
        self.timer_remaining = 0
        self.persisted_data = self.serialized_data()

        self.phone = tk.Frame(root, bg="#252833", padx=12, pady=12)
        self.phone.pack(padx=22, pady=18)
        self.screen = tk.Frame(self.phone, bg=BG, width=370, height=760)
        self.screen.pack()
        self.screen.pack_propagate(False)

        self.show_home()
        self.update_clock()
        self.root.protocol("WM_DELETE_WINDOW", self.close_application)
        self.schedule_autosave()

    def load_data(self):
        if not DATA_FILE.exists():
            return json.loads(json.dumps(DEFAULT_DATA))
        try:
            with DATA_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, dict):
                raise ValueError("Kayıt dosyasının kökü bir JSON nesnesi olmalı.")
        except (OSError, json.JSONDecodeError, ValueError) as error:
            if BACKUP_FILE.exists():
                try:
                    with BACKUP_FILE.open("r", encoding="utf-8") as file:
                        backup = json.load(file)
                    if not isinstance(backup, dict):
                        raise ValueError("Yedek dosyasının kökü bir JSON nesnesi olmalı.")
                    messagebox.showwarning(
                        "Yedekten kurtarıldı",
                        f"Ana kayıt okunamadı; yedek kayıt yüklendi.\n\n{error}",
                    )
                    return self.normalize_data(backup)
                except (OSError, json.JSONDecodeError, ValueError) as backup_error:
                    messagebox.showerror(
                        "Kayıtlar yüklenemedi",
                        f"Ana kayıt: {error}\n\nYedek kayıt: {backup_error}",
                    )
                    return json.loads(json.dumps(DEFAULT_DATA))
            messagebox.showerror(
                "Veriler yüklenemedi",
                f"Kayıt dosyası okunamadı. Boş verilerle devam edilecek.\n\n{error}",
            )
            return json.loads(json.dumps(DEFAULT_DATA))

        return self.normalize_data(data)

    @staticmethod
    def normalize_data(data):
        if not isinstance(data, dict):
            raise ValueError("Kayıt dosyasının kökü bir JSON nesnesi olmalı.")
        for key, default in DEFAULT_DATA.items():
            if key not in data or not isinstance(data[key], type(default)):
                data[key] = json.loads(json.dumps(default))
        data["save_metadata"]["schema_version"] = 2
        if not isinstance(data["save_metadata"].get("saved_at"), str):
            data["save_metadata"]["saved_at"] = ""
        valid_app_ids = {item["id"] for item in STORE_APPS}
        data["installed_apps"] = list(dict.fromkeys(
            app_id for app_id in data["installed_apps"]
            if isinstance(app_id, str) and app_id in valid_app_ids
        ))
        data["tasks"] = [
            {"text": task["text"], "done": task.get("done", False)}
            for task in data["tasks"]
            if isinstance(task, dict)
            and isinstance(task.get("text"), str)
            and isinstance(task.get("done", False), bool)
        ]
        data["shopping_list"] = [
            item for item in data["shopping_list"] if isinstance(item, str)
        ]
        data["journal"] = [
            {"date": entry["date"], "text": entry["text"]}
            for entry in data["journal"]
            if isinstance(entry, dict)
            and isinstance(entry.get("date"), str)
            and isinstance(entry.get("text"), str)
        ]
        device = data["device"]
        valid_versions = {item["version"] for item in ANDROID_VERSIONS}
        if device.get("version") not in valid_versions:
            device["version"] = "Android 14"
        if not isinstance(device.get("setup_complete"), bool):
            device["setup_complete"] = True
        if not isinstance(device.get("name"), str):
            device["name"] = "Telefonum"
        if not isinstance(device.get("account_skipped"), bool):
            device["account_skipped"] = True
        return data

    def serialized_data(self):
        return json.dumps(self.data, ensure_ascii=False, sort_keys=True)

    def apply_android_theme(self, version):
        global BG, CARD, TEXT, MUTED, ACCENT
        selected = next(
            (item for item in ANDROID_VERSIONS if item["version"] == version),
            ANDROID_VERSIONS[4],
        )
        BG, CARD, TEXT, MUTED, ACCENT = selected["colors"]
        self.android_layout = selected["layout"]
        if hasattr(self, "screen"):
            self.screen.configure(bg=BG)
        if hasattr(self, "phone"):
            self.phone.configure(bg=self.blend_color(BG, "#ffffff", 0.16))
        self.root.configure(bg=self.blend_color(BG, "#000000", 0.4))
        self.root.title(f"Telefon Simülasyonu — {selected['name']}")

    def save_data(self):
        temporary_path = None
        try:
            DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            self.data["save_metadata"] = {
                "schema_version": 2,
                "saved_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            }
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=DATA_FILE.parent,
                prefix=f"{DATA_FILE.stem}.", suffix=".tmp", delete=False
            ) as file:
                json.dump(self.data, file, ensure_ascii=False, indent=2)
                file.flush()
                os.fsync(file.fileno())
                temporary_path = Path(file.name)
            if DATA_FILE.exists():
                shutil.copy2(DATA_FILE, BACKUP_FILE)
            os.replace(temporary_path, DATA_FILE)
            temporary_path = None
        except (OSError, TypeError) as error:
            messagebox.showerror("Kayıt yapılamadı", f"Veriler kaydedilemedi.\n\n{error}")
            return False
        finally:
            if temporary_path is not None:
                try:
                    if temporary_path.exists():
                        temporary_path.unlink()
                except OSError as error:
                    messagebox.showerror(
                        "Geçici dosya temizlenemedi", str(error), parent=self.root
                    )
        self.persisted_data = self.serialized_data()
        return True

    def schedule_autosave(self):
        self.autosave_job = self.root.after(30000, self.autosave_if_changed)

    def autosave_if_changed(self):
        if not self.root.winfo_exists():
            return
        if self.serialized_data() != self.persisted_data:
            self.save_data()
        self.schedule_autosave()

    def close_application(self):
        if self.serialized_data() != self.persisted_data and not self.save_data():
            if not messagebox.askyesno(
                "Kayıt yapılamadı",
                "Son değişiklikler kaydedilemedi. Yine de çıkmak istiyor musun?",
                parent=self.root,
            ):
                return
        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None
        if self.call_pulse_job is not None:
            self.root.after_cancel(self.call_pulse_job)
            self.call_pulse_job = None
        if hasattr(self, "autosave_job"):
            self.root.after_cancel(self.autosave_job)
        self.root.destroy()

    def clear(self):
        if self.call_pulse_job is not None:
            self.root.after_cancel(self.call_pulse_job)
            self.call_pulse_job = None
        for widget in self.screen.winfo_children():
            widget.destroy()

    def update_clock(self):
        if not self.root.winfo_exists():
            return
        if hasattr(self, "clock_label") and self.clock_label.winfo_exists():
            self.clock_label.config(text=datetime.now().strftime("%H:%M"))
        if hasattr(self, "home_clock_label") and self.home_clock_label.winfo_exists():
            self.home_clock_label.config(text=datetime.now().strftime("%H:%M"))
        if hasattr(self, "status_detail_label") and self.status_detail_label.winfo_exists():
            settings = self.data["settings"]
            wifi = "● Wi-Fi" if settings.get("wifi", False) else "○ Wi-Fi"
            bluetooth = "● BT" if settings.get("bluetooth", False) else "○ BT"
            sound = "♫" if settings.get("sound", False) else "×"
            self.status_detail_label.config(text=f"{wifi}  {bluetooth}  {sound}  ▰ 82%")
        self.root.after(1000, self.update_clock)

    def status_bar(self, parent):
        bar = tk.Frame(parent, bg=BG)
        bar.pack(fill="x", padx=18, pady=(12, 4))
        self.clock_label = tk.Label(
            bar, text=datetime.now().strftime("%H:%M"),
            bg=BG, fg=TEXT, font=("Segoe UI", 10, "bold")
        )
        self.clock_label.pack(side="left")
        settings = self.data["settings"]
        wifi = "● Wi-Fi" if settings.get("wifi", False) else "○ Wi-Fi"
        bluetooth = "● BT" if settings.get("bluetooth", False) else "○ BT"
        sound = "♫" if settings.get("sound", False) else "×"
        self.status_detail_label = tk.Label(
            bar, text=f"{wifi}  {bluetooth}  {sound}  ▰ 82%",
            bg=BG, fg=TEXT, font=("Segoe UI", 9)
        )
        self.status_detail_label.pack(side="right")

    def make_button(self, parent, text, command, color=ACCENT, **kwargs):
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="white",
            activebackground=color,
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            **kwargs,
        )
        hover_color = self.blend_color(color, "#ffffff", 0.12)
        self.bind_button_hover(button, color, hover_color)
        return button

    @staticmethod
    def blend_color(start, end, amount):
        start_rgb = tuple(int(start[index:index + 2], 16) for index in (1, 3, 5))
        end_rgb = tuple(int(end[index:index + 2], 16) for index in (1, 3, 5))
        blended = tuple(
            round(start_rgb[index] + (end_rgb[index] - start_rgb[index]) * amount)
            for index in range(3)
        )
        return "#{:02x}{:02x}{:02x}".format(*blended)

    def show_home(self):
        self.clear()
        self.screen.configure(bg=BG)
        self.status_bar(self.screen)

        weekdays = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        months = [
            "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
            "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık",
        ]
        now = datetime.now()
        date_text = f"{weekdays[now.weekday()]}, {now.day} {months[now.month - 1]}"
        hero = tk.Frame(self.screen, bg=CARD, padx=16, pady=12)
        hero.pack(fill="x", padx=18, pady=(18, 12))
        if self.android_layout == "minimal":
            hero_content = tk.Frame(hero, bg=CARD)
            hero_content.pack(fill="x")
            tk.Label(
                hero_content, text=date_text, bg=CARD,
                fg=MUTED, font=("Segoe UI", 9, "bold")
            ).pack(side="left", anchor="s", pady=(0, 7))
            clock_parent = hero_content
            clock_side = "right"
        elif self.android_layout == "pixel15":
            hero_content = tk.Frame(hero, bg=CARD)
            hero_content.pack(fill="x")
            tk.Label(
                hero_content, text="BUGÜN", bg=CARD, fg=ACCENT,
                font=("Segoe UI", 9, "bold")
            ).pack(anchor="w")
            tk.Label(
                hero_content, text=date_text, bg=CARD, fg=TEXT,
                font=("Segoe UI", 9)
            ).pack(anchor="w")
            clock_parent = hero_content
            clock_side = "right"
        elif self.android_layout == "oreo":
            tk.Label(
                hero, text=f"Merhaba, {self.data['device']['name']}",
                bg=CARD, fg=ACCENT, font=("Segoe UI", 13, "bold")
            ).pack(anchor="w")
            tk.Label(
                hero, text=date_text, bg=CARD, fg=MUTED,
                font=("Segoe UI", 9)
            ).pack(anchor="w", pady=(2, 0))
            clock_parent = hero
            clock_side = "top"
        elif self.android_layout == "material13":
            tk.Label(
                hero, text="CİHAZIN BUGÜN HAZIR",
                bg=CARD, fg=ACCENT, font=("Segoe UI", 9, "bold")
            ).pack(anchor="w")
            clock_parent = hero
            clock_side = "top"
        else:
            tk.Label(
                hero, text=date_text, bg=CARD,
                fg=MUTED if self.android_layout == "material12" else TEXT,
                font=("Segoe UI", 10, "bold")
            ).pack()
            clock_parent = hero
            clock_side = "top"
        clock_size = {
            "oreo": 34,
            "minimal": 34,
            "material12": 48,
            "material13": 38,
            "pixel14": 46,
            "pixel15": 36,
        }[self.android_layout]
        self.home_clock_label = tk.Label(
            clock_parent, text=now.strftime("%H:%M"), bg=CARD,
            fg=ACCENT if self.android_layout == "material12" else TEXT,
            font=("Segoe UI", clock_size, "bold")
        )
        self.home_clock_label.pack(side=clock_side)
        tk.Label(
            hero, text=f"{self.data['device']['name']}  ·  {self.data['device']['version']}",
            bg=CARD, fg=MUTED if self.android_layout == "pixel15" else ACCENT,
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w" if self.android_layout == "minimal" else "center", pady=(2, 0))
        if self.android_layout == "material13":
            quick_settings = tk.Frame(self.screen, bg=BG)
            quick_settings.pack(fill="x", padx=18, pady=(0, 8))
            tk.Label(
                quick_settings,
                text=f"● Wi-Fi {'Açık' if self.data['settings'].get('wifi') else 'Kapalı'}"
                     f"     ● Bluetooth {'Açık' if self.data['settings'].get('bluetooth') else 'Kapalı'}",
                bg=CARD, fg=TEXT, font=("Segoe UI", 8, "bold"),
                padx=8, pady=7
            ).pack(fill="x")
        tk.Label(
            self.screen, text="Uygulamalar",
            bg=BG, fg=TEXT, font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=24, pady=(0, 5))

        apps = BUILTIN_APPS + [
            item for item in STORE_APPS
            if item["id"] in self.data["installed_apps"]
        ]
        grid = tk.Frame(self.screen, bg=BG)
        grid.pack()
        columns = {
            "oreo": 4,
            "minimal": 2,
            "material12": 2,
            "material13": 3,
            "pixel14": 3,
            "pixel15": 2,
        }[self.android_layout]
        for index, app in enumerate(apps):
            if self.android_layout == "minimal":
                button_text = f"{app['icon']}   {app['name']}"
                button_width, button_height = 18, 1
            elif self.android_layout == "oreo":
                button_text = f"{app['icon']}\n{app['name']}"
                button_width, button_height = 8, 2
            elif self.android_layout == "material12":
                button_text = f"{app['icon']}  {app['name']}"
                button_width, button_height = 16, 2
            elif self.android_layout == "pixel15":
                button_text = f"{app['icon']}   {app['name']}"
                button_width, button_height = 17, 2
            else:
                button_text = f"{app['icon']}\n{app['name']}"
                button_width, button_height = 10, 3
            button_font_size = 9 if self.android_layout == "oreo" else 10
            button = tk.Button(
                grid,
                text=button_text,
                command=lambda app_id=app["id"]: self.launch_app(app_id),
                bg=app["color"],
                fg="white",
                activebackground=app["color"],
                activeforeground="white",
                relief="flat",
                font=("Segoe UI", button_font_size, "bold"),
                width=button_width,
                height=button_height,
                cursor="hand2",
            )
            button.grid(row=index // columns, column=index % columns, padx=5, pady=4)
            self.bind_button_hover(button, app["color"])

        tk.Label(
            self.screen, text=f"{len(apps)} UYGULAMA  ·  CİHAZINIZ HAZIR",
            bg=BG, fg=MUTED, font=("Segoe UI", 8, "bold")
        ).pack(side="bottom", pady=12)

    def launch_app(self, app_id):
        action_name = APP_ACTIONS.get(app_id)
        if action_name is None:
            messagebox.showerror("Uygulama açılamadı", "Bu uygulama kataloğa kayıtlı değil.")
            return
        if app_id in {item["id"] for item in STORE_APPS}:
            if app_id not in self.data["installed_apps"]:
                messagebox.showinfo(
                    "Uygulama yüklü değil",
                    "Bu uygulamayı kullanmak için önce Play Store'dan yükle.",
                )
                self.show_store()
                return
        getattr(self, action_name)()

    def bind_button_hover(self, button, base_color, hover_color=None):
        if hover_color is None:
            hover_color = self.blend_color(base_color, "#ffffff", 0.12)
        button.bind(
            "<Enter>",
            lambda event: self.animate_button_color(event.widget, hover_color),
        )
        button.bind(
            "<Leave>",
            lambda event: self.animate_button_color(event.widget, base_color),
        )

    def animate_button_color(self, button, end_color):
        pending_job = getattr(button, "_color_job", None)
        if pending_job is not None:
            button.after_cancel(pending_job)
        start = button.winfo_rgb(button.cget("bg"))
        end = button.winfo_rgb(end_color)
        steps = 5

        def animate(step=1):
            if not button.winfo_exists():
                return
            ratio = step / steps
            current = tuple(
                round(start[index] + (end[index] - start[index]) * ratio) // 256
                for index in range(3)
            )
            color_value = "#{:02x}{:02x}{:02x}".format(*current)
            button.configure(bg=color_value, activebackground=color_value)
            if step < steps:
                button._color_job = button.after(18, lambda: animate(step + 1))
            else:
                button._color_job = None

        animate()

    def app_page(self, title, back_command=None):
        self.clear()
        self.screen.configure(bg=BG)
        self.status_bar(self.screen)
        header = tk.Frame(self.screen, bg=BG)
        header.pack(fill="x", padx=12, pady=(2, 8))
        tk.Button(
            header, text="‹", command=back_command or self.show_home,
            bg=BG, fg=TEXT, relief="flat", font=("Segoe UI", 23),
            cursor="hand2"
        ).pack(side="left")
        tk.Label(
            header, text=title, bg=BG, fg=TEXT,
            font=("Segoe UI", 17, "bold")
        ).pack(side="left", padx=8)
        body = tk.Frame(self.screen, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=(0, 14))
        return body

    def show_store(self):
        body = self.app_page("Play Store")
        list_area = tk.Frame(body, bg=BG)
        list_area.pack(fill="both", expand=True)
        canvas = tk.Canvas(list_area, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_area, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        catalog = tk.Frame(canvas, bg=BG)
        canvas_window = canvas.create_window((0, 0), window=catalog, anchor="nw")
        catalog.bind(
            "<Configure>",
            lambda _event: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda event: canvas.itemconfigure(canvas_window, width=event.width),
        )
        catalog.bind(
            "<MouseWheel>",
            lambda event: canvas.yview_scroll(-int(event.delta / 120), "units"),
        )

        installed = self.data["device"]["version"]
        tk.Label(
            catalog, text="Android sürümleri",
            bg=BG, fg=TEXT, font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", pady=(0, 3))
        tk.Label(
            catalog, text=f"Şu an yüklü: {installed}",
            bg=BG, fg=MUTED, font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(0, 8))
        tk.Label(
            catalog,
            text="Kurulumlar bu simülatör içinde gerçekleşir; gerçek cihaz yazılımı değiştirilmez.",
            bg=BG, fg=MUTED, font=("Segoe UI", 8), wraplength=310, justify="left"
        ).pack(anchor="w", pady=(0, 8))

        for release in ANDROID_VERSIONS:
            row = tk.Frame(catalog, bg=CARD, padx=10, pady=7)
            row.pack(fill="x", pady=3)
            details = tk.Frame(row, bg=CARD)
            details.pack(side="left", fill="x", expand=True)
            tk.Label(
                details, text=release["name"], bg=CARD, fg=TEXT,
                font=("Segoe UI", 10, "bold"), anchor="w"
            ).pack(anchor="w")
            tk.Label(
                details, text=f"{release['codename']} · {release['description']}",
                bg=CARD, fg=MUTED,
                font=("Segoe UI", 8), anchor="w", wraplength=190, justify="left"
            ).pack(anchor="w")
            action_text = "Yeniden kur" if release["version"] == installed else "Yükle"
            self.make_button(
                row, action_text,
                lambda item=release: self.start_android_install(item),
                release["colors"][4], padx=10, pady=5
            ).pack(side="right", padx=(6, 0))

        tk.Label(
            catalog, text="Uygulamalar",
            bg=BG, fg=TEXT, font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", pady=(12, 4))
        tk.Label(
            catalog,
            text="Simülatörde çalışan yerleşik uygulamalar ve ek uygulamalar.",
            bg=BG, fg=MUTED, font=("Segoe UI", 8), wraplength=300, justify="left"
        ).pack(anchor="w", pady=(0, 6))
        for app in BUILTIN_APPS + STORE_APPS:
            row = tk.Frame(catalog, bg=CARD, padx=10, pady=6)
            row.pack(fill="x", pady=3)
            tk.Label(
                row, text=app["icon"], bg=CARD, fg=app["color"],
                font=("Segoe UI", 18, "bold"), width=2
            ).pack(side="left", padx=(0, 8))
            details = tk.Frame(row, bg=CARD)
            details.pack(side="left", fill="x", expand=True)
            tk.Label(
                details, text=app["name"], bg=CARD, fg=TEXT,
                font=("Segoe UI", 9, "bold"), anchor="w"
            ).pack(anchor="w")
            description = app.get("description", "Simülatörün yerleşik uygulaması.")
            tk.Label(
                details, text=description, bg=CARD, fg=MUTED,
                font=("Segoe UI", 8), anchor="w", wraplength=180, justify="left"
            ).pack(anchor="w")
            is_installed = (
                app["id"] in APP_ACTIONS
                and (
                    app["id"] not in {item["id"] for item in STORE_APPS}
                    or app["id"] in self.data["installed_apps"]
                )
            )
            if is_installed:
                button_text = "Aç"
                action = lambda app_id=app["id"]: self.launch_app(app_id)
            else:
                button_text = "Yükle"
                action = lambda app_id=app["id"]: self.install_store_app(app_id)
            self.make_button(
                row, button_text, action, app["color"], padx=8, pady=4
            ).pack(side="right", padx=(6, 0))

    def install_store_app(self, app_id):
        if app_id not in {app["id"] for app in STORE_APPS}:
            messagebox.showerror("Yükleme başarısız", "Uygulama kataloğu doğrulanamadı.")
            return
        if app_id not in self.data["installed_apps"]:
            self.data["installed_apps"].append(app_id)
            if not self.save_data():
                self.data["installed_apps"].remove(app_id)
                return
        self.show_store()

    def start_android_install(self, release):
        self.install_version = release
        self.install_progress = 0
        body = self.app_page(
            "Android kurulumu", back_command=self.cancel_android_install
        )
        tk.Label(
            body, text=release["name"], bg=BG, fg=TEXT,
            font=("Segoe UI", 20, "bold")
        ).pack(pady=(90, 8))
        self.install_status_label = tk.Label(
            body, text="Sürüm hazırlanıyor…", bg=BG, fg=MUTED,
            font=("Segoe UI", 10)
        )
        self.install_status_label.pack(pady=(0, 15))
        self.install_canvas = tk.Canvas(
            body, width=300, height=14, bg=CARD, highlightthickness=0
        )
        self.install_canvas.pack()
        self.install_progress_bar = self.install_canvas.create_rectangle(
            0, 0, 0, 14, fill=release["colors"][4], outline=""
        )
        self.install_percent_label = tk.Label(
            body, text="0%", bg=BG, fg=TEXT, font=("Segoe UI", 11, "bold")
        )
        self.install_percent_label.pack(pady=8)
        self.make_button(
            body, "İptal", self.cancel_android_install, "#454b5c",
            width=18, height=2
        ).pack(pady=20)
        self.install_job = self.root.after(40, self.advance_android_install)

    def advance_android_install(self):
        if self.install_version is None:
            self.install_job = None
            return
        self.install_progress = min(100, self.install_progress + 2)
        progress = self.install_progress
        self.install_canvas.coords(
            self.install_progress_bar, 0, 0, 3 * progress, 14
        )
        self.install_percent_label.config(text=f"{progress}%")
        if progress < 35:
            status = "Sürüm dosyaları hazırlanıyor…"
        elif progress < 75:
            status = "Arayüz ve uygulamalar yükleniyor…"
        elif progress < 100:
            status = "Kurulum tamamlanıyor…"
        else:
            status = "Kurulum tamamlandı"
        self.install_status_label.config(text=status)
        if progress == 100:
            self.install_job = None
            self.begin_device_setup()
        else:
            self.install_job = self.root.after(40, self.advance_android_install)

    def cancel_android_install(self):
        if self.install_job is not None:
            self.root.after_cancel(self.install_job)
            self.install_job = None
        self.install_version = None
        self.show_store()

    def begin_device_setup(self):
        if self.install_version is None:
            return
        self.setup_previous_version = self.data["device"]["version"]
        self.setup_values = {
            "wifi": self.data["settings"].get("wifi", True),
            "bluetooth": self.data["settings"].get("bluetooth", False),
            "account_skipped": True,
            "name": self.data["device"].get("name", "Telefonum"),
        }
        self.setup_step = 0
        self.setup_previous_complete = self.data["device"]["setup_complete"]
        self.data["device"]["setup_complete"] = False
        self.apply_android_theme(self.install_version["version"])
        self.show_setup_step()

    def show_setup_step(self):
        release = self.install_version
        if release is None:
            self.show_store()
            return
        body = self.app_page(
            f"{release['version']} kurulumu", back_command=self.cancel_device_setup
        )
        step_titles = ("Hoş geldiniz", "Bağlantı", "Hesap", "Son dokunuşlar")
        tk.Label(
            body, text=f"Cihaz kurulumu  ·  Adım {self.setup_step + 1}/4",
            bg=BG, fg=ACCENT, font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(4, 3))
        tk.Label(
            body, text=step_titles[self.setup_step], bg=BG, fg=TEXT,
            font=("Segoe UI", 20, "bold")
        ).pack(anchor="w", pady=(0, 10))
        progress = tk.Canvas(body, height=8, bg=CARD, highlightthickness=0)
        progress.pack(fill="x", pady=(0, 18))
        progress.update_idletasks()
        width = max(progress.winfo_width(), 280)
        progress.create_rectangle(
            0, 0, width * (self.setup_step + 1) / 4, 8,
            fill=ACCENT, outline=""
        )
        self.setup_widgets = {}

        if self.setup_step == 0:
            tk.Label(
                body, text=f"Yeni arayüzün hazır: {release['name']}",
                bg=BG, fg=TEXT, font=("Segoe UI", 14, "bold")
            ).pack(anchor="w", pady=(18, 8))
            tk.Label(
                body,
                text="Birkaç kısa adımda bağlantı ve cihaz tercihlerini ayarla. "
                     "Bu kurulum yalnızca simülatörün görünümünü değiştirir.",
                bg=BG, fg=MUTED, font=("Segoe UI", 10), wraplength=300,
                justify="left"
            ).pack(anchor="w")
        elif self.setup_step == 1:
            tk.Label(
                body, text="Hızlı ayarlar", bg=BG, fg=MUTED,
                font=("Segoe UI", 10)
            ).pack(anchor="w", pady=(0, 8))
            for key, label in (("wifi", "Wi-Fi"), ("bluetooth", "Bluetooth")):
                variable = tk.BooleanVar(value=self.setup_values[key])
                self.setup_widgets[key] = variable
                tk.Checkbutton(
                    body, text=label, variable=variable,
                    bg=CARD, fg=TEXT, selectcolor=CARD,
                    activebackground=CARD, activeforeground=TEXT,
                    font=("Segoe UI", 11), anchor="w", padx=12, pady=10
                ).pack(fill="x", pady=4)
            tk.Label(
                body,
                text="Bu anahtarlar yalnızca simülatörün durum çubuğunu ve ayarlarını etkiler.",
                bg=BG, fg=MUTED, font=("Segoe UI", 9), wraplength=300,
                justify="left"
            ).pack(anchor="w", pady=10)
        elif self.setup_step == 2:
            tk.Label(
                body, text="Hesap ve gizlilik", bg=BG, fg=TEXT,
                font=("Segoe UI", 14, "bold")
            ).pack(anchor="w", pady=(16, 8))
            tk.Label(
                body,
                text="Bu simülatör gerçek Google hesabı bağlamaz ve hesap bilgisi istemez. "
                     "İstersen bu adımı daha sonra tamamlanacak şekilde işaretleyebilirsin.",
                bg=BG, fg=MUTED, font=("Segoe UI", 10), wraplength=300,
                justify="left"
            ).pack(anchor="w", pady=(0, 14))
            variable = tk.BooleanVar(value=self.setup_values["account_skipped"])
            self.setup_widgets["account_skipped"] = variable
            tk.Checkbutton(
                body, text="Hesap adımını şimdilik atla", variable=variable,
                bg=CARD, fg=TEXT, selectcolor=CARD,
                activebackground=CARD, activeforeground=TEXT,
                font=("Segoe UI", 10), anchor="w", padx=12, pady=10
            ).pack(fill="x")
        else:
            tk.Label(
                body, text="Cihazına bir ad ver", bg=BG, fg=MUTED,
                font=("Segoe UI", 10)
            ).pack(anchor="w", pady=(16, 5))
            name_entry = tk.Entry(
                body, bg=CARD, fg=TEXT, insertbackground=TEXT,
                relief="flat", font=("Segoe UI", 12)
            )
            name_entry.pack(fill="x", ipady=9)
            name_entry.insert(0, self.setup_values["name"])
            self.setup_widgets["name"] = name_entry
            tk.Label(
                body, text=f"Kurulacak sürüm: {release['name']}",
                bg=BG, fg=ACCENT, font=("Segoe UI", 10, "bold")
            ).pack(anchor="w", pady=16)

        actions = tk.Frame(body, bg=BG)
        actions.pack(side="bottom", fill="x", pady=(12, 0))
        if self.setup_step > 0:
            self.make_button(
                actions, "Geri", self.previous_setup_step, "#454b5c"
            ).pack(side="left", expand=True, fill="x", padx=(0, 4), ipady=8)
        next_text = "Kurulumu tamamla" if self.setup_step == 3 else "Devam"
        self.make_button(
            actions, next_text, self.next_setup_step, ACCENT
        ).pack(side="left" if self.setup_step > 0 else "right",
               expand=True, fill="x", padx=(4, 0) if self.setup_step > 0 else 0,
               ipady=8)

    def save_current_setup_step(self):
        for key in ("wifi", "bluetooth", "account_skipped"):
            if key in self.setup_widgets:
                self.setup_values[key] = self.setup_widgets[key].get()
        if "name" in self.setup_widgets:
            name = self.setup_widgets["name"].get().strip()
            if not name:
                messagebox.showwarning(
                    "Cihaz adı gerekli", "Cihazına bir ad ver.", parent=self.root
                )
                return False
            if len(name) > 24:
                messagebox.showwarning(
                    "Cihaz adı çok uzun",
                    "Cihaz adı en fazla 24 karakter olabilir.",
                    parent=self.root,
                )
                return False
            self.setup_values["name"] = name
        return True

    def next_setup_step(self):
        if not self.save_current_setup_step():
            return
        if self.setup_step < 3:
            self.setup_step += 1
            self.show_setup_step()
            return
        self.data["device"].update({
            "version": self.install_version["version"],
            "setup_complete": True,
            "name": self.setup_values["name"],
            "account_skipped": self.setup_values["account_skipped"],
        })
        self.data["settings"]["wifi"] = self.setup_values["wifi"]
        self.data["settings"]["bluetooth"] = self.setup_values["bluetooth"]
        if not self.save_data():
            self.data["device"]["setup_complete"] = False
            return
        self.install_version = None
        self.apply_android_theme(self.data["device"]["version"])
        self.show_home()

    def previous_setup_step(self):
        if not self.save_current_setup_step():
            return
        self.setup_step = max(0, self.setup_step - 1)
        self.show_setup_step()

    def cancel_device_setup(self):
        if self.install_version is None:
            self.show_store()
            return
        self.data["device"]["setup_complete"] = self.setup_previous_complete
        self.apply_android_theme(self.setup_previous_version)
        self.install_version = None
        self.show_store()

    def show_phone(self):
        body = self.app_page("Telefon")
        tk.Label(
            body, text="Numara tuşla", bg=BG, fg=MUTED,
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(2, 5))
        self.dial_entry = tk.Entry(
            body, justify="center", font=("Segoe UI", 22),
            bg=CARD, fg=TEXT, insertbackground=TEXT, relief="flat"
        )
        self.dial_entry.pack(fill="x", ipady=9, pady=(0, 12))

        keypad = tk.Frame(body, bg=BG)
        keypad.pack()
        keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "*", "0", "#"]
        for index, key in enumerate(keys):
            self.make_button(
                keypad, key, lambda value=key: self.add_digit(value),
                CARD, width=6, height=2, font=("Segoe UI", 15)
            ).grid(row=index // 3, column=index % 3, padx=5, pady=4)

        actions = tk.Frame(body, bg=BG)
        actions.pack(fill="x", pady=9)
        self.make_button(actions, "⌫ Sil", self.delete_digit, "#454b5c").pack(
            side="left", expand=True, fill="x", padx=(0, 4), ipady=8
        )
        self.make_button(actions, "Ara", self.start_call, "#35a96f").pack(
            side="left", expand=True, fill="x", padx=(4, 0), ipady=8
        )

        tk.Label(body, text="Son aramalar", bg=BG, fg=TEXT,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(8, 4))
        if not self.data["recent_calls"]:
            tk.Label(body, text="Henüz arama kaydı yok.", bg=BG, fg=MUTED,
                     font=("Segoe UI", 10)).pack(anchor="w")
        for call in reversed(self.data["recent_calls"][-4:]):
            tk.Label(
                body, text=f"☎  {call['number']}    {call['time']}    {call['duration']}",
                bg=CARD, fg=TEXT, font=("Segoe UI", 9), anchor="w", padx=10, pady=7
            ).pack(fill="x", pady=2)

    def add_digit(self, digit):
        self.dial_entry.insert("end", digit)

    def delete_digit(self):
        current = self.dial_entry.get()
        if current:
            self.dial_entry.delete(len(current) - 1, "end")

    def start_call(self, number=None):
        number = (number if number is not None else self.dial_entry.get()).strip()
        if not number:
            messagebox.showinfo("Telefon", "Aramak için bir numara gir.")
            return
        self.call_number = number
        self.call_started = time.monotonic()
        body = self.app_page("Arama")
        self.call_pulse_phase = 0
        self.call_canvas = tk.Canvas(
            body, width=128, height=128, bg=BG, highlightthickness=0
        )
        self.call_canvas.pack(pady=(40, 8))
        self.update_call_pulse()
        tk.Label(body, text="Giden arama", bg=BG, fg=MUTED,
                 font=("Segoe UI", 12)).pack(pady=(0, 8))
        contact = self.find_contact(number)
        tk.Label(
            body, text=contact["name"] if contact else number, bg=BG, fg=TEXT,
            font=("Segoe UI", 23, "bold")
        ).pack()
        if contact:
            tk.Label(body, text=number, bg=BG, fg=MUTED,
                     font=("Segoe UI", 11)).pack(pady=(2, 0))
        self.call_timer_label = tk.Label(
            body, text="00:00", bg=BG, fg=TEXT, font=("Segoe UI", 16, "bold")
        )
        self.call_timer_label.pack(pady=12)
        self.make_button(body, "Aramayı bitir", self.end_call,
                         "#d64f5d", width=20, height=2).pack(pady=24)
        tk.Label(
            body, text="Arama yalnızca bu simülatör içinde çalışır.",
            bg=BG, fg=MUTED, font=("Segoe UI", 9), wraplength=300
        ).pack()
        self.update_call_timer()

    def update_call_pulse(self):
        if self.call_started is None or not self.call_canvas.winfo_exists():
            return
        canvas = self.call_canvas
        canvas.delete("all")
        center = 64
        for offset in (0, 10, 20):
            progress = ((self.call_pulse_phase + offset) % 30) / 30
            radius = 30 + progress * 25
            color = ("#26364d", "#315569", "#3b756f")[int(progress * 3)]
            canvas.create_oval(
                center - radius, center - radius,
                center + radius, center + radius,
                outline=color, width=2,
            )
        canvas.create_oval(36, 36, 92, 92, fill="#245c53", outline="")
        canvas.create_text(
            center, center, text="☎", fill="white", font=("Segoe UI", 23, "bold")
        )
        self.call_pulse_phase += 1
        self.call_pulse_job = self.root.after(80, self.update_call_pulse)

    def update_call_timer(self):
        if self.call_started is None or not self.call_timer_label.winfo_exists():
            return
        elapsed = int(time.monotonic() - self.call_started)
        self.call_timer_label.config(text=f"{elapsed // 60:02}:{elapsed % 60:02}")
        self.root.after(1000, self.update_call_timer)

    def end_call(self):
        if self.call_started is None:
            return
        elapsed = int(time.monotonic() - self.call_started)
        self.data["recent_calls"].append({
            "number": self.call_number,
            "time": datetime.now().strftime("%d.%m %H:%M"),
            "duration": f"{elapsed // 60:02}:{elapsed % 60:02}",
        })
        self.data["recent_calls"] = self.data["recent_calls"][-50:]
        self.call_started = None
        if self.call_pulse_job is not None:
            self.root.after_cancel(self.call_pulse_job)
            self.call_pulse_job = None
        self.save_data()
        self.show_phone()

    def show_messages(self):
        body = self.app_page("Mesajlar")
        self.make_button(body, "＋  Yeni mesaj", self.new_message,
                         ACCENT, height=2).pack(fill="x", pady=(0, 10))
        conversations = self.data["conversations"]
        if not conversations:
            tk.Label(
                body, text="Henüz mesaj yok.\nYeni mesaj oluşturarak başlayabilirsin.",
                bg=BG, fg=MUTED, font=("Segoe UI", 11), justify="left"
            ).pack(anchor="w", pady=10)
            return
        for number, messages in conversations.items():
            contact = self.find_contact(number)
            title = contact["name"] if contact else number
            preview = messages[-1]["text"] if messages else "Mesaj yok"
            self.make_button(
                body, f"{title}\n{preview}", lambda n=number: self.open_conversation(n),
                CARD, justify="left", anchor="w", height=2
            ).pack(fill="x", pady=4)

    def new_message(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Yeni mesaj")
        dialog.configure(bg=BG)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        tk.Label(dialog, text="Alıcı numarası", bg=BG, fg=TEXT,
                 font=("Segoe UI", 11)).pack(anchor="w", padx=16, pady=(16, 5))
        recipient = ttk.Combobox(dialog, values=[
            f"{contact['name']} — {contact['number']}" for contact in self.data["contacts"]
        ])
        recipient.pack(fill="x", padx=16)
        tk.Label(dialog, text="Mesaj", bg=BG, fg=TEXT,
                 font=("Segoe UI", 11)).pack(anchor="w", padx=16, pady=(12, 5))
        message = tk.Entry(dialog, font=("Segoe UI", 11))
        message.pack(fill="x", padx=16)

        def send():
            recipient_text = recipient.get().strip()
            number = recipient_text.rsplit(" — ", 1)[-1].strip()
            text = message.get().strip()
            if not number or not text:
                messagebox.showwarning("Eksik bilgi", "Alıcı numarası ve mesaj gerekli.", parent=dialog)
                return
            self.data["conversations"].setdefault(number, []).append({
                "sender": "Ben",
                "text": text,
                "time": datetime.now().strftime("%d.%m %H:%M"),
            })
            self.save_data()
            dialog.destroy()
            self.open_conversation(number)

        self.make_button(dialog, "Gönder", send, "#4388dd").pack(
            fill="x", padx=16, pady=16, ipady=7
        )
        dialog.bind("<Return>", lambda _event: send())

    def open_conversation(self, number):
        contact = self.find_contact(number)
        title = contact["name"] if contact else number
        body = self.app_page(title)
        transcript = tk.Text(
            body, height=20, wrap="word", bg=CARD, fg=TEXT,
            insertbackground=TEXT, relief="flat", font=("Segoe UI", 10),
            state="normal"
        )
        transcript.pack(fill="both", expand=True, pady=(0, 8))
        for message in self.data["conversations"].get(number, []):
            transcript.insert(
                "end", f"{message['sender']}  ·  {message['time']}\n{message['text']}\n\n"
            )
        transcript.config(state="disabled")
        transcript.see("end")
        row = tk.Frame(body, bg=BG)
        row.pack(fill="x")
        entry = tk.Entry(row, font=("Segoe UI", 11), bg=CARD, fg=TEXT,
                         insertbackground=TEXT, relief="flat")
        entry.pack(side="left", fill="x", expand=True, ipady=9, padx=(0, 5))

        def send():
            text = entry.get().strip()
            if not text:
                return
            self.data["conversations"].setdefault(number, []).append({
                "sender": "Ben",
                "text": text,
                "time": datetime.now().strftime("%d.%m %H:%M"),
            })
            self.save_data()
            self.open_conversation(number)

        self.make_button(row, "Gönder", send, "#4388dd").pack(side="right", ipady=7)
        entry.bind("<Return>", lambda _event: send())

    def find_contact(self, number):
        return next(
            (contact for contact in self.data["contacts"] if contact["number"] == number),
            None,
        )

    def show_contacts(self):
        body = self.app_page("Kişiler")
        self.make_button(body, "＋  Kişi ekle", self.add_contact,
                         "#e7893e", height=2).pack(fill="x", pady=(0, 10))
        search = tk.Entry(body, font=("Segoe UI", 11), bg=CARD, fg=TEXT,
                          insertbackground=TEXT, relief="flat")
        search.pack(fill="x", ipady=8, pady=(0, 8))
        search.insert(0, "Kişilerde ara...")
        list_frame = tk.Frame(body, bg=BG)
        list_frame.pack(fill="both", expand=True)

        def render(_event=None):
            for widget in list_frame.winfo_children():
                widget.destroy()
            query = search.get().strip().casefold()
            if query == "kişilerde ara...":
                query = ""
            for index, contact in enumerate(self.data["contacts"]):
                if query not in contact["name"].casefold() and query not in contact["number"].casefold():
                    continue
                card = tk.Frame(list_frame, bg=CARD, padx=9, pady=7)
                card.pack(fill="x", pady=3)
                tk.Label(card, text=f"{contact['name']}\n{contact['number']}",
                         bg=CARD, fg=TEXT, justify="left",
                         font=("Segoe UI", 10)).pack(side="left", expand=True, anchor="w")
                self.make_button(
                    card, "Ara", lambda n=contact["number"]: self.start_call(n),
                    "#35a96f", padx=8, pady=4
                ).pack(side="right", padx=2)
                self.make_button(
                    card, "Sil", lambda i=index: self.delete_contact(i),
                    "#a74450", padx=8, pady=4
                ).pack(side="right", padx=2)
            if not self.data["contacts"]:
                tk.Label(list_frame, text="Kişi listesi boş.", bg=BG, fg=MUTED,
                         font=("Segoe UI", 10)).pack(anchor="w", pady=8)

        search.bind("<KeyRelease>", render)
        render()

    def add_contact(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Kişi ekle")
        dialog.configure(bg=BG)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        fields = {}
        for label in ("Ad", "Telefon numarası"):
            tk.Label(dialog, text=label, bg=BG, fg=TEXT,
                     font=("Segoe UI", 10)).pack(anchor="w", padx=16, pady=(12, 3))
            entry = tk.Entry(dialog, font=("Segoe UI", 11))
            entry.pack(fill="x", padx=16)
            fields[label] = entry

        def save():
            name = fields["Ad"].get().strip()
            number = fields["Telefon numarası"].get().strip()
            if not name or not number:
                messagebox.showwarning("Eksik bilgi", "Ad ve telefon numarası gerekli.", parent=dialog)
                return
            if self.find_contact(number):
                messagebox.showwarning("Kişi zaten var", "Bu numara kayıtlı.", parent=dialog)
                return
            self.data["contacts"].append({"name": name, "number": number})
            self.save_data()
            dialog.destroy()
            self.show_contacts()

        self.make_button(dialog, "Kaydet", save, "#e7893e").pack(
            fill="x", padx=16, pady=16, ipady=7
        )

    def delete_contact(self, index):
        contact = self.data["contacts"][index]
        if messagebox.askyesno("Kişiyi sil", f"{contact['name']} silinsin mi?"):
            del self.data["contacts"][index]
            self.save_data()
            self.show_contacts()

    def show_save_center(self):
        body = self.app_page("Kayıt Merkezi")
        metadata = self.data.get("save_metadata", {})
        saved_at = metadata.get("saved_at") or "Henüz kayıt alınmadı"
        counts = (
            ("Kişi", len(self.data["contacts"])),
            ("Mesaj", sum(len(items) for items in self.data["conversations"].values())),
            ("Not", len(self.data["notes"])),
            ("Etkinlik", len(self.data["events"])),
            ("Görev", len(self.data["tasks"])),
            ("Günlük", len(self.data["journal"])),
            ("Yüklü uygulama", len(self.data["installed_apps"])),
        )
        tk.Label(
            body, text="Kayıt ve yedekleme", bg=BG, fg=TEXT,
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", pady=(2, 4))
        tk.Label(
            body, text=f"Son kayıt: {saved_at}", bg=BG, fg=MUTED,
            font=("Segoe UI", 8), wraplength=310, justify="left"
        ).pack(anchor="w", pady=(0, 8))
        summary = "   ·   ".join(f"{label}: {count}" for label, count in counts)
        tk.Label(
            body, text=summary, bg=CARD, fg=TEXT,
            font=("Segoe UI", 9), wraplength=300, justify="left",
            padx=10, pady=10
        ).pack(fill="x", pady=(0, 8))
        backup_text = (
            f"Yedek mevcut: {BACKUP_FILE.name}"
            if BACKUP_FILE.exists() else "Yedek henüz oluşturulmadı."
        )
        tk.Label(
            body, text=backup_text, bg=BG, fg=MUTED,
            font=("Segoe UI", 9), wraplength=300, justify="left"
        ).pack(anchor="w", pady=(0, 10))
        self.make_button(
            body, "Şimdi kaydet ve yedekle", self.save_from_center, ACCENT
        ).pack(fill="x", pady=4, ipady=7)
        self.make_button(
            body, "Yedekten geri yükle", self.restore_backup, "#b96568"
        ).pack(fill="x", pady=4, ipady=7)
        self.make_button(
            body, "Dışa aktar…", self.export_save, "#5687c5"
        ).pack(fill="x", pady=4, ipady=7)
        self.make_button(
            body, "İçe aktar…", self.import_save, "#3b9b80"
        ).pack(fill="x", pady=4, ipady=7)
        tk.Label(
            body,
            text="Otomatik kayıt 30 saniyede bir değişiklikleri yazar. "
                 "Kapanışta da kaydedilir; önceki dosya yedekte tutulur.",
            bg=BG, fg=MUTED, font=("Segoe UI", 8), wraplength=300,
            justify="left"
        ).pack(anchor="w", pady=10)

    def save_from_center(self):
        if self.save_data():
            messagebox.showinfo("Kayıt tamamlandı", "Veriler kaydedildi ve yedek güncellendi.")
            self.show_save_center()

    def read_import_file(self, path):
        with Path(path).open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, dict):
            raise ValueError("Kayıt dosyasının kökü bir JSON nesnesi olmalı.")
        return self.normalize_data(data)

    def restore_backup(self):
        if not BACKUP_FILE.exists():
            messagebox.showinfo("Yedek bulunamadı", "Henüz geri yüklenecek bir yedek yok.")
            return
        if not messagebox.askyesno(
            "Yedekten geri yükle",
            "Mevcut veriler yedekle değiştirilecek. Devam edilsin mi?",
            parent=self.root,
        ):
            return
        try:
            restored = self.read_import_file(BACKUP_FILE)
        except (OSError, json.JSONDecodeError, ValueError) as error:
            messagebox.showerror("Yedek okunamadı", str(error), parent=self.root)
            return
        previous = self.data
        self.data = restored
        self.apply_android_theme(self.data["device"]["version"])
        if not self.save_data():
            self.data = previous
            self.apply_android_theme(self.data["device"]["version"])
            return
        self.show_home()

    def export_save(self):
        path = filedialog.asksaveasfilename(
            title="Kayıt dosyasını dışa aktar",
            defaultextension=".json",
            filetypes=[("JSON kayıt dosyası", "*.json")],
            initialfile=f"telefon-yedek-{datetime.now():%Y%m%d-%H%M%S}.json",
        )
        if not path:
            return
        try:
            with Path(path).open("w", encoding="utf-8") as file:
                json.dump(self.data, file, ensure_ascii=False, indent=2)
        except (OSError, TypeError) as error:
            messagebox.showerror("Dışa aktarılamadı", str(error), parent=self.root)
            return
        messagebox.showinfo("Dışa aktarıldı", f"Kayıt dosyası oluşturuldu:\n{path}")

    def import_save(self):
        path = filedialog.askopenfilename(
            title="Kayıt dosyasını içe aktar",
            filetypes=[("JSON kayıt dosyası", "*.json"), ("Tüm dosyalar", "*.*")],
        )
        if not path:
            return
        try:
            imported = self.read_import_file(path)
        except (OSError, json.JSONDecodeError, ValueError) as error:
            messagebox.showerror("Dosya içe aktarılamadı", str(error), parent=self.root)
            return
        if not messagebox.askyesno(
            "Kaydı içe aktar",
            "Mevcut kayıtların içe aktarılan dosyayla değiştirilecek. Devam edilsin mi?",
            parent=self.root,
        ):
            return
        previous = self.data
        self.data = imported
        self.apply_android_theme(self.data["device"]["version"])
        if not self.save_data():
            self.data = previous
            self.apply_android_theme(self.data["device"]["version"])
            return
        self.show_home()

    def show_settings(self):
        body = self.app_page("Ayarlar")
        self.make_button(
            body, "▣  Kayıt Merkezi", self.show_save_center, "#6177bd"
        ).pack(fill="x", pady=(0, 10), ipady=6)
        tk.Label(body, text="Bağlantılar ve cihaz", bg=BG, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(2, 10))
        settings = self.data["settings"]
        for key, label in (("wifi", "Wi-Fi"), ("bluetooth", "Bluetooth"), ("sound", "Ses")):
            variable = tk.BooleanVar(value=settings.get(key, False))

            def toggle(setting=key, value=variable):
                self.data["settings"][setting] = value.get()
                self.save_data()

            tk.Checkbutton(
                body, text=label, variable=variable, command=toggle,
                bg=CARD, fg=TEXT, selectcolor=CARD, activebackground=CARD,
                activeforeground=TEXT, font=("Segoe UI", 11), anchor="w",
                padx=12, pady=8
            ).pack(fill="x", pady=4)

        tk.Label(body, text="Ekran parlaklığı", bg=BG, fg=TEXT,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(18, 5))
        brightness = tk.IntVar(value=settings.get("brightness", 75))
        scale = tk.Scale(
            body, from_=0, to=100, orient="horizontal", variable=brightness,
            bg=BG, fg=TEXT, troughcolor=CARD, highlightthickness=0,
            command=lambda value: self.save_setting("brightness", int(float(value)))
        )
        scale.pack(fill="x")
        tk.Label(
            body, text="Ağ ayarları bu simülatörün gerçek cihaz bağlantılarını değiştirmez.",
            bg=BG, fg=MUTED, font=("Segoe UI", 9), wraplength=300, justify="left"
        ).pack(anchor="w", pady=18)

    def save_setting(self, key, value):
        self.data["settings"][key] = value
        self.save_data()

    def show_tasks(self):
        body = self.app_page("Yapılacaklar")
        entry = tk.Entry(
            body, bg=CARD, fg=TEXT, insertbackground=TEXT, relief="flat",
            font=("Segoe UI", 11)
        )
        entry.pack(fill="x", ipady=8, pady=(0, 6))
        entry.insert(0, "")
        self.make_button(
            body, "＋  Görev ekle", lambda: self.add_task(entry), "#3b9b80"
        ).pack(fill="x", pady=(0, 10), ipady=6)
        if not self.data["tasks"]:
            tk.Label(
                body, text="Listen boş. İlk görevini ekle.",
                bg=BG, fg=MUTED, font=("Segoe UI", 10)
            ).pack(anchor="w", pady=5)
        for index, task in enumerate(self.data["tasks"]):
            row = tk.Frame(body, bg=CARD, padx=7, pady=5)
            row.pack(fill="x", pady=3)
            completed = tk.BooleanVar(value=task.get("done", False))
            tk.Checkbutton(
                row, text=task["text"], variable=completed,
                command=lambda i=index, value=completed: self.set_task_done(i, value.get()),
                bg=CARD, fg=TEXT, selectcolor=CARD, activebackground=CARD,
                activeforeground=TEXT, font=("Segoe UI", 9), anchor="w",
                wraplength=220,
            ).pack(side="left", fill="x", expand=True)
            self.make_button(
                row, "×", lambda i=index: self.delete_task(i), "#a74450",
                padx=8, pady=3
            ).pack(side="right")
        entry.bind("<Return>", lambda _event: self.add_task(entry))

    def add_task(self, entry):
        text = entry.get().strip()
        if not text:
            messagebox.showwarning("Görev gerekli", "Önce görev açıklaması yaz.")
            return
        self.data["tasks"].append({"text": text, "done": False})
        if self.save_data():
            self.show_tasks()

    def set_task_done(self, index, done):
        self.data["tasks"][index]["done"] = done
        self.save_data()

    def delete_task(self, index):
        del self.data["tasks"][index]
        if self.save_data():
            self.show_tasks()

    def show_weather(self):
        body = self.app_page("Hava Durumu")
        tk.Label(
            body, text="Çevrimdışı demo tahmini",
            bg=BG, fg=MUTED, font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(0, 8))
        cities = {
            "İstanbul": ("☁", "18°C", "Parçalı bulutlu", "Nem %62  ·  Rüzgâr 12 km/sa"),
            "Ankara": ("☀", "16°C", "Açık", "Nem %38  ·  Rüzgâr 9 km/sa"),
            "İzmir": ("☀", "22°C", "Güneşli", "Nem %51  ·  Rüzgâr 14 km/sa"),
            "Antalya": ("🌤", "25°C", "Az bulutlu", "Nem %58  ·  Rüzgâr 11 km/sa"),
            "Bursa": ("🌧", "17°C", "Hafif yağmur", "Nem %74  ·  Rüzgâr 8 km/sa"),
        }
        selected_city = tk.StringVar(
            value=self.data["settings"].get("weather_city", "İstanbul")
        )
        city_picker = ttk.Combobox(
            body, textvariable=selected_city, values=list(cities), state="readonly"
        )
        city_picker.pack(fill="x", pady=(0, 10))
        card = tk.Frame(body, bg=CARD, padx=16, pady=18)
        card.pack(fill="x")
        icon = tk.Label(card, text="", bg=CARD, fg=ACCENT, font=("Segoe UI", 40))
        icon.pack()
        temperature = tk.Label(card, text="", bg=CARD, fg=TEXT,
                               font=("Segoe UI", 32, "bold"))
        temperature.pack()
        condition = tk.Label(card, text="", bg=CARD, fg=TEXT,
                             font=("Segoe UI", 12, "bold"))
        condition.pack(pady=(0, 5))
        detail = tk.Label(card, text="", bg=CARD, fg=MUTED,
                          font=("Segoe UI", 9))
        detail.pack()

        def update_weather(_event=None):
            city = selected_city.get()
            icon_text, degrees, status, extra = cities[city]
            icon.config(text=icon_text)
            temperature.config(text=degrees)
            condition.config(text=f"{city} · {status}")
            detail.config(text=extra)
            self.data["settings"]["weather_city"] = city
            self.save_data()

        city_picker.bind("<<ComboboxSelected>>", update_weather)
        update_weather()

    @staticmethod
    def convert_units(category, value, source, target):
        if not math.isfinite(value):
            raise ValueError("Sayı sonlu olmalı.")
        unit_groups = {
            "Uzunluk": {"mm": 0.001, "cm": 0.01, "m": 1.0, "km": 1000.0},
            "Ağırlık": {"g": 0.001, "kg": 1.0, "ton": 1000.0},
        }
        if category in unit_groups:
            factors = unit_groups[category]
            return value * factors[source] / factors[target]
        if category == "Sıcaklık":
            to_celsius = {
                "°C": lambda number: number,
                "°F": lambda number: (number - 32) * 5 / 9,
                "K": lambda number: number - 273.15,
            }
            from_celsius = {
                "°C": lambda number: number,
                "°F": lambda number: number * 9 / 5 + 32,
                "K": lambda number: number + 273.15,
            }
            return from_celsius[target](to_celsius[source](value))
        raise ValueError("Desteklenmeyen dönüştürme türü.")

    def show_converter(self):
        body = self.app_page("Birim Dönüştürücü")
        unit_options = {
            "Uzunluk": ("mm", "cm", "m", "km"),
            "Ağırlık": ("g", "kg", "ton"),
            "Sıcaklık": ("°C", "°F", "K"),
        }
        category = tk.StringVar(value="Uzunluk")
        value = tk.StringVar(value="1")
        source = tk.StringVar(value="m")
        target = tk.StringVar(value="km")
        category_box = ttk.Combobox(
            body, textvariable=category, values=list(unit_options), state="readonly"
        )
        category_box.pack(fill="x", pady=(10, 8))
        entry = tk.Entry(
            body, textvariable=value, bg=CARD, fg=TEXT,
            insertbackground=TEXT, relief="flat", font=("Segoe UI", 15)
        )
        entry.pack(fill="x", ipady=8, pady=(0, 8))
        units = tk.Frame(body, bg=BG)
        units.pack(fill="x")
        source_box = ttk.Combobox(units, textvariable=source, state="readonly", width=9)
        source_box.pack(side="left", expand=True, fill="x", padx=(0, 4))
        tk.Label(units, text="→", bg=BG, fg=MUTED, font=("Segoe UI", 14)).pack(side="left")
        target_box = ttk.Combobox(units, textvariable=target, state="readonly", width=9)
        target_box.pack(side="left", expand=True, fill="x", padx=(4, 0))
        result = tk.Label(
            body, text="", bg=CARD, fg=ACCENT,
            font=("Segoe UI", 20, "bold"), padx=10, pady=14
        )
        result.pack(fill="x", pady=12)

        def refresh_units(_event=None):
            options = unit_options[category.get()]
            source_box.configure(values=options)
            target_box.configure(values=options)
            source.set(options[0])
            target.set(options[-1])

        def convert(_event=None):
            try:
                converted = self.convert_units(
                    category.get(), float(value.get()), source.get(), target.get()
                )
            except (ValueError, KeyError, OverflowError):
                result.config(text="Geçerli bir sayı gir.", fg="#d96570")
                return
            result.config(text=f"{converted:.6g} {target.get()}", fg=ACCENT)

        category_box.bind("<<ComboboxSelected>>", refresh_units)
        self.make_button(body, "Dönüştür", convert, "#5687c5").pack(fill="x", ipady=7)
        entry.bind("<Return>", convert)
        refresh_units()
        source.set("m")
        target.set("km")
        convert()

    def show_timer(self):
        body = self.app_page("Zamanlayıcı")
        tk.Label(
            body, text="Geri sayım süresi (dakika)",
            bg=BG, fg=MUTED, font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(20, 6))
        self.timer_minutes_entry = tk.Entry(
            body, bg=CARD, fg=TEXT, insertbackground=TEXT,
            relief="flat", justify="center", font=("Segoe UI", 14)
        )
        self.timer_minutes_entry.pack(fill="x", ipady=8)
        self.timer_minutes_entry.insert(0, "1")
        self.timer_label = tk.Label(
            body, text="00:00", bg=BG, fg=TEXT,
            font=("Segoe UI", 38, "bold")
        )
        self.timer_label.pack(pady=25)
        self.timer_status = tk.Label(
            body, text="Hazır", bg=BG, fg=MUTED, font=("Segoe UI", 10)
        )
        self.timer_status.pack()
        actions = tk.Frame(body, bg=BG)
        actions.pack(fill="x", pady=16)
        self.timer_toggle_button = self.make_button(
            actions, "Başlat", self.toggle_timer, "#b96568"
        )
        self.timer_toggle_button.pack(side="left", expand=True, fill="x", padx=(0, 4), ipady=7)
        self.make_button(
            actions, "Sıfırla", self.reset_timer, "#454b5c"
        ).pack(side="left", expand=True, fill="x", padx=(4, 0), ipady=7)
        if self.timer_deadline is not None:
            self.timer_toggle_button.config(text="Duraklat")
            self.timer_status.config(text="Geri sayım sürüyor")
            self.render_timer()
            if self.timer_job is None:
                self.timer_job = self.root.after(100, self.update_timer)
        else:
            self.render_timer()

    def toggle_timer(self):
        if self.timer_deadline is not None:
            self.timer_remaining = max(0, self.timer_deadline - time.monotonic())
            self.timer_deadline = None
            if self.timer_job is not None:
                self.root.after_cancel(self.timer_job)
                self.timer_job = None
            self.timer_toggle_button.config(text="Devam")
            self.timer_status.config(text="Duraklatıldı")
            self.render_timer()
            return
        try:
            if self.timer_remaining <= 0:
                minutes = float(self.timer_minutes_entry.get())
                if minutes <= 0 or minutes > 1440:
                    raise ValueError
                self.timer_remaining = minutes * 60
        except ValueError:
            messagebox.showwarning(
                "Geçersiz süre", "0 ile 1440 arasında dakika gir.", parent=self.root
            )
            return
        self.timer_deadline = time.monotonic() + self.timer_remaining
        self.timer_toggle_button.config(text="Duraklat")
        self.timer_status.config(text="Geri sayım sürüyor")
        if self.timer_job is None:
            self.timer_job = self.root.after(100, self.update_timer)

    def update_timer(self):
        if self.timer_deadline is None:
            self.timer_job = None
            return
        self.timer_remaining = max(0, self.timer_deadline - time.monotonic())
        self.render_timer()
        if self.timer_remaining <= 0:
            self.timer_deadline = None
            self.timer_job = None
            if hasattr(self, "timer_status") and self.timer_status.winfo_exists():
                self.timer_status.config(text="Süre doldu!")
                self.timer_toggle_button.config(text="Başlat")
            if self.data["settings"].get("sound", True):
                self.root.bell()
            return
        self.timer_job = self.root.after(100, self.update_timer)

    def render_timer(self):
        if not hasattr(self, "timer_label") or not self.timer_label.winfo_exists():
            return
        seconds_left = int(self.timer_remaining + 0.999)
        minutes, seconds = divmod(seconds_left, 60)
        self.timer_label.config(text=f"{minutes:02}:{seconds:02}")

    def reset_timer(self):
        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None
        self.timer_deadline = None
        self.timer_remaining = 0
        self.timer_toggle_button.config(text="Başlat")
        self.timer_status.config(text="Hazır")
        self.render_timer()

    def show_journal(self):
        body = self.app_page("Günlük")
        self.journal_entry = tk.Text(
            body, height=5, wrap="word", bg=CARD, fg=TEXT,
            insertbackground=TEXT, relief="flat", font=("Segoe UI", 10)
        )
        self.journal_entry.pack(fill="x", pady=(0, 6))
        self.make_button(
            body, "＋  Bugünü kaydet", self.add_journal_entry, "#9a72bd"
        ).pack(fill="x", pady=(0, 8), ipady=6)
        if not self.data["journal"]:
            tk.Label(
                body, text="Henüz günlük kaydı yok.",
                bg=BG, fg=MUTED, font=("Segoe UI", 9)
            ).pack(anchor="w")
        for index, entry in enumerate(reversed(self.data["journal"][-5:])):
            actual_index = len(self.data["journal"]) - 1 - index
            row = tk.Frame(body, bg=CARD, padx=8, pady=6)
            row.pack(fill="x", pady=3)
            tk.Label(
                row, text=f"{entry['date']}\n{entry['text'][:90]}",
                bg=CARD, fg=TEXT, font=("Segoe UI", 9),
                justify="left", anchor="w", wraplength=235
            ).pack(side="left", fill="x", expand=True)
            self.make_button(
                row, "×", lambda i=actual_index: self.delete_journal_entry(i),
                "#a74450", padx=8, pady=3
            ).pack(side="right")

    def add_journal_entry(self):
        text = self.journal_entry.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showwarning("Günlük boş", "Kaydetmeden önce birkaç cümle yaz.")
            return
        self.data["journal"].append({
            "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "text": text,
        })
        if self.save_data():
            self.show_journal()

    def delete_journal_entry(self, index):
        del self.data["journal"][index]
        if self.save_data():
            self.show_journal()

    def show_password_generator(self):
        body = self.app_page("Şifre Üretici")
        tk.Label(
            body, text="Uzunluk (8–64)", bg=BG, fg=MUTED,
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(16, 5))
        length = tk.StringVar(value="16")
        ttk.Spinbox(body, from_=8, to=64, textvariable=length).pack(fill="x")
        use_upper = tk.BooleanVar(value=True)
        use_digits = tk.BooleanVar(value=True)
        use_symbols = tk.BooleanVar(value=True)
        for label, variable in (
            ("Büyük harf", use_upper),
            ("Rakam", use_digits),
            ("Sembol", use_symbols),
        ):
            tk.Checkbutton(
                body, text=label, variable=variable,
                bg=BG, fg=TEXT, selectcolor=CARD,
                activebackground=BG, activeforeground=TEXT,
                font=("Segoe UI", 10), anchor="w"
            ).pack(fill="x", pady=3)
        result = tk.Entry(
            body, bg=CARD, fg=TEXT, insertbackground=TEXT,
            relief="flat", font=("Consolas", 11), justify="center"
        )
        result.pack(fill="x", ipady=9, pady=(12, 6))

        def generate():
            try:
                size = int(length.get())
            except ValueError:
                messagebox.showwarning("Geçersiz uzunluk", "8 ile 64 arasında sayı gir.")
                return
            if not 8 <= size <= 64:
                messagebox.showwarning("Geçersiz uzunluk", "8 ile 64 arasında sayı gir.")
                return
            groups = [ascii_letters.lower()]
            if use_upper.get():
                groups.append(ascii_letters.upper())
            if use_digits.get():
                groups.append(digits)
            if use_symbols.get():
                groups.append(punctuation)
            if len(groups) > size:
                messagebox.showwarning(
                    "Uzunluk kısa", "Seçili karakter gruplarına uygun daha uzun bir şifre seç."
                )
                return
            characters = [secrets.choice(group) for group in groups]
            pool = "".join(groups)
            characters.extend(secrets.choice(pool) for _ in range(size - len(characters)))
            secrets.SystemRandom().shuffle(characters)
            result.delete(0, "end")
            result.insert(0, "".join(characters))

        def copy_password():
            password = result.get()
            if not password:
                messagebox.showinfo("Şifre yok", "Önce bir şifre üret.")
                return
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Kopyalandı", "Şifre panoya kopyalandı.")

        self.make_button(body, "Yeni şifre üret", generate, "#587c62").pack(
            fill="x", pady=5, ipady=7
        )
        self.make_button(body, "Panoya kopyala", copy_password, "#454b5c").pack(
            fill="x", pady=5, ipady=7
        )

    def show_shopping_list(self):
        body = self.app_page("Alışveriş Listesi")
        entry = tk.Entry(
            body, bg=CARD, fg=TEXT, insertbackground=TEXT, relief="flat",
            font=("Segoe UI", 11)
        )
        entry.pack(fill="x", ipady=8, pady=(0, 6))
        self.make_button(
            body, "＋  Ürün ekle", lambda: self.add_shopping_item(entry), "#c27445"
        ).pack(fill="x", pady=(0, 8), ipady=6)
        if not self.data["shopping_list"]:
            tk.Label(
                body, text="Listen boş.", bg=BG, fg=MUTED,
                font=("Segoe UI", 9)
            ).pack(anchor="w")
        for index, item in enumerate(self.data["shopping_list"]):
            row = tk.Frame(body, bg=CARD, padx=9, pady=6)
            row.pack(fill="x", pady=3)
            tk.Label(
                row, text=f"•  {item}", bg=CARD, fg=TEXT,
                font=("Segoe UI", 10), anchor="w"
            ).pack(side="left", fill="x", expand=True)
            self.make_button(
                row, "Aldım", lambda i=index: self.remove_shopping_item(i),
                "#3b9b80", padx=8, pady=4
            ).pack(side="right")
        entry.bind("<Return>", lambda _event: self.add_shopping_item(entry))

    def add_shopping_item(self, entry):
        item = entry.get().strip()
        if not item:
            messagebox.showwarning("Ürün gerekli", "Eklenecek ürünün adını yaz.")
            return
        self.data["shopping_list"].append(item)
        if self.save_data():
            self.show_shopping_list()

    def remove_shopping_item(self, index):
        del self.data["shopping_list"][index]
        if self.save_data():
            self.show_shopping_list()

    def show_calculator(self):
        body = self.app_page("Hesap Makinesi")
        value = tk.StringVar()
        display = tk.Entry(
            body, textvariable=value, justify="right", font=("Segoe UI", 24),
            state="readonly", readonlybackground=CARD, fg=TEXT, relief="flat"
        )
        display.pack(fill="x", pady=(20, 12), ipady=8)

        def press(key):
            if key == "C":
                value.set("")
            elif key == "⌫":
                value.set(value.get()[:-1])
            elif key == "=":
                try:
                    value.set(str(self.calculate(value.get())))
                except (ValueError, SyntaxError, ZeroDivisionError, OverflowError):
                    value.set("Hata")
            elif value.get() == "Hata":
                value.set(key)
            else:
                value.set(value.get() + key)

        keypad = tk.Frame(body, bg=BG)
        keypad.pack()
        keys = ["7", "8", "9", "÷", "4", "5", "6", "×",
                "1", "2", "3", "-", "C", "0", "⌫", "+", "(", ")", "=", "."]
        for index, key in enumerate(keys):
            self.make_button(
                keypad, key, lambda k=key: press({"÷": "/", "×": "*"}.get(k, k)),
                CARD, width=5, height=2, font=("Segoe UI", 14)
            ).grid(row=index // 4, column=index % 4, padx=3, pady=3)
        display.bind("<Return>", lambda _event: press("="))

    def calculate(self, expression):
        if not expression.strip():
            raise ValueError("Boş ifade")
        tree = ast.parse(expression, mode="eval")
        binary_operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod,
        }
        unary_operators = {ast.UAdd: operator.pos, ast.USub: operator.neg}

        def evaluate(node):
            if isinstance(node, ast.Expression):
                return evaluate(node.body)
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                return node.value
            if isinstance(node, ast.BinOp) and type(node.op) in binary_operators:
                left, right = evaluate(node.left), evaluate(node.right)
                if isinstance(node.op, ast.Pow) and abs(right) > 100:
                    raise ValueError("Üs çok büyük")
                return binary_operators[type(node.op)](left, right)
            if isinstance(node, ast.UnaryOp) and type(node.op) in unary_operators:
                return unary_operators[type(node.op)](evaluate(node.operand))
            raise ValueError("Desteklenmeyen işlem")

        result = evaluate(tree)
        if isinstance(result, float) and result.is_integer():
            return int(result)
        return result

    def show_notes(self):
        body = self.app_page("Notlar")
        self.make_button(body, "＋  Yeni not", lambda: self.edit_note(),
                         "#b99332", height=2).pack(fill="x", pady=(0, 10))
        if not self.data["notes"]:
            tk.Label(body, text="Henüz not yok.", bg=BG, fg=MUTED,
                     font=("Segoe UI", 10)).pack(anchor="w", pady=8)
        for index, note in enumerate(self.data["notes"]):
            self.make_button(
                body, f"{note['title']}\n{note['text'][:70]}",
                lambda i=index: self.edit_note(i), CARD,
                justify="left", anchor="w", height=2
            ).pack(fill="x", pady=4)

    def edit_note(self, index=None):
        note = self.data["notes"][index] if index is not None else {"title": "", "text": ""}
        dialog = tk.Toplevel(self.root)
        dialog.title("Not")
        dialog.configure(bg=BG)
        dialog.geometry("340x430")
        dialog.transient(self.root)
        dialog.grab_set()
        title = tk.Entry(dialog, font=("Segoe UI", 12))
        title.pack(fill="x", padx=14, pady=14, ipady=7)
        title.insert(0, note["title"])
        text = tk.Text(dialog, wrap="word", font=("Segoe UI", 11),
                       bg=CARD, fg=TEXT, insertbackground=TEXT, relief="flat")
        text.pack(fill="both", expand=True, padx=14)
        text.insert("1.0", note["text"])

        def save():
            content = {"title": title.get().strip(), "text": text.get("1.0", "end-1c").strip()}
            if not content["title"]:
                messagebox.showwarning("Başlık gerekli", "Nota bir başlık yaz.", parent=dialog)
                return
            if index is None:
                self.data["notes"].append(content)
            else:
                self.data["notes"][index] = content
            self.save_data()
            dialog.destroy()
            self.show_notes()

        actions = tk.Frame(dialog, bg=BG)
        actions.pack(fill="x", padx=14, pady=12)
        self.make_button(actions, "Kaydet", save, "#b99332").pack(
            side="left", expand=True, fill="x", padx=(0, 4), ipady=7
        )
        if index is not None:
            self.make_button(actions, "Sil", lambda: self.delete_note(index),
                             "#a74450").pack(
                side="left", expand=True, fill="x", padx=(4, 0), ipady=7
            )

    def delete_note(self, index):
        if messagebox.askyesno("Notu sil", "Bu not silinsin mi?"):
            del self.data["notes"][index]
            self.save_data()
            self.show_notes()

    def show_calendar(self):
        body = self.app_page("Takvim")
        self.make_button(body, "＋  Etkinlik ekle", self.add_event,
                         "#c34f50", height=2).pack(fill="x", pady=(0, 10))
        events = sorted(self.data["events"], key=lambda event: event["date"])
        if not events:
            tk.Label(body, text="Henüz etkinlik yok.", bg=BG, fg=MUTED,
                     font=("Segoe UI", 10)).pack(anchor="w", pady=8)
        for index, event in enumerate(events):
            row = tk.Frame(body, bg=CARD, padx=10, pady=8)
            row.pack(fill="x", pady=3)
            tk.Label(
                row, text=f"{event['date']}  {event['time']}\n{event['title']}",
                bg=CARD, fg=TEXT, justify="left", font=("Segoe UI", 10)
            ).pack(side="left", expand=True, anchor="w")
            self.make_button(
                row, "Sil", lambda e=event: self.delete_event(e),
                "#a74450", padx=8, pady=4
            ).pack(side="right")

    def add_event(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Etkinlik ekle")
        dialog.configure(bg=BG)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        fields = {}
        for label, initial in (
            ("Etkinlik adı", ""),
            ("Tarih (YYYY-AA-GG)", datetime.now().strftime("%Y-%m-%d")),
            ("Saat (SS:DD)", datetime.now().strftime("%H:%M")),
        ):
            tk.Label(dialog, text=label, bg=BG, fg=TEXT,
                     font=("Segoe UI", 10)).pack(anchor="w", padx=16, pady=(10, 3))
            entry = tk.Entry(dialog, font=("Segoe UI", 11))
            entry.pack(fill="x", padx=16)
            entry.insert(0, initial)
            fields[label] = entry

        def save():
            title_text = fields["Etkinlik adı"].get().strip()
            date_text = fields["Tarih (YYYY-AA-GG)"].get().strip()
            time_text = fields["Saat (SS:DD)"].get().strip()
            try:
                datetime.strptime(f"{date_text} {time_text}", "%Y-%m-%d %H:%M")
            except ValueError:
                messagebox.showwarning("Geçersiz tarih", "Tarih veya saat biçimini kontrol et.", parent=dialog)
                return
            if not title_text:
                messagebox.showwarning("Ad gerekli", "Etkinliğe bir ad yaz.", parent=dialog)
                return
            self.data["events"].append({
                "title": title_text, "date": date_text, "time": time_text,
            })
            self.save_data()
            dialog.destroy()
            self.show_calendar()

        self.make_button(dialog, "Kaydet", save, "#c34f50").pack(
            fill="x", padx=16, pady=16, ipady=7
        )

    def delete_event(self, event):
        self.data["events"].remove(event)
        self.save_data()
        self.show_calendar()

    def show_clock(self):
        body = self.app_page("Saat")
        self.digital_clock = tk.Label(
            body, text="", bg=BG, fg=TEXT, font=("Segoe UI", 34, "bold")
        )
        self.digital_clock.pack(pady=(50, 5))
        self.digital_date = tk.Label(body, text="", bg=BG, fg=MUTED,
                                     font=("Segoe UI", 12))
        self.digital_date.pack()
        self.refresh_digital_clock()

        tk.Label(body, text="Kronometre", bg=BG, fg=TEXT,
                 font=("Segoe UI", 14, "bold")).pack(pady=(55, 8))
        self.stopwatch_label = tk.Label(
            body, text="00:00.0", bg=BG, fg=TEXT, font=("Segoe UI", 24)
        )
        self.stopwatch_label.pack(pady=8)
        actions = tk.Frame(body, bg=BG)
        actions.pack()
        self.make_button(actions, "Başlat / Durdur", self.toggle_stopwatch,
                         "#448f98").pack(side="left", padx=4, ipady=7)
        self.make_button(actions, "Sıfırla", self.reset_stopwatch,
                         "#454b5c").pack(side="left", padx=4, ipady=7)

    def refresh_digital_clock(self):
        if not hasattr(self, "digital_clock") or not self.digital_clock.winfo_exists():
            return
        self.digital_clock.config(text=datetime.now().strftime("%H:%M:%S"))
        self.digital_date.config(text=datetime.now().strftime("%d.%m.%Y"))
        self.root.after(500, self.refresh_digital_clock)

    def toggle_stopwatch(self):
        if self.stopwatch_started is None:
            self.stopwatch_started = time.monotonic()
            self.update_stopwatch()
        else:
            self.stopwatch_elapsed += time.monotonic() - self.stopwatch_started
            self.stopwatch_started = None
            if self.stopwatch_job:
                self.root.after_cancel(self.stopwatch_job)
                self.stopwatch_job = None
            self.render_stopwatch()

    def update_stopwatch(self):
        if self.stopwatch_started is None:
            return
        self.render_stopwatch()
        self.stopwatch_job = self.root.after(100, self.update_stopwatch)

    def render_stopwatch(self):
        if hasattr(self, "stopwatch_label") and self.stopwatch_label.winfo_exists():
            elapsed = self.stopwatch_elapsed
            if self.stopwatch_started is not None:
                elapsed += time.monotonic() - self.stopwatch_started
            minutes, seconds = divmod(elapsed, 60)
            self.stopwatch_label.config(text=f"{int(minutes):02}:{seconds:04.1f}")

    def reset_stopwatch(self):
        self.stopwatch_elapsed = 0.0
        self.stopwatch_started = None
        if self.stopwatch_job:
            self.root.after_cancel(self.stopwatch_job)
            self.stopwatch_job = None
        self.render_stopwatch()

    def show_gallery(self):
        body = self.app_page("Galeri")
        self.make_button(body, "＋  Fotoğraf seç", self.choose_photos,
                         "#d9658b", height=2).pack(fill="x", pady=(0, 10))
        tk.Label(
            body, text="Seçtiğin fotoğraflar bu simülatörün galerisinde listelenir.",
            bg=BG, fg=MUTED, font=("Segoe UI", 9), wraplength=300, justify="left"
        ).pack(anchor="w", pady=(0, 8))
        self.gallery_list = tk.Frame(body, bg=BG)
        self.gallery_list.pack(fill="both", expand=True)
        self.render_gallery()

    def choose_photos(self):
        paths = filedialog.askopenfilenames(
            title="Fotoğraf seç",
            filetypes=[
                ("Görseller", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("Tüm dosyalar", "*.*"),
            ],
        )
        for path in paths:
            if path not in self.data.get("photos", []):
                self.data.setdefault("photos", []).append(path)
        if not self.save_data():
            return
        self.render_gallery()

    def render_gallery(self):
        for widget in self.gallery_list.winfo_children():
            widget.destroy()
        paths = self.data.get("photos", [])
        if not paths:
            tk.Label(self.gallery_list, text="Henüz fotoğraf seçilmedi.",
                     bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=8)
        for path in paths:
            row = tk.Frame(self.gallery_list, bg=CARD, padx=8, pady=7)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=Path(path).name, bg=CARD, fg=TEXT,
                     font=("Segoe UI", 9), anchor="w").pack(
                side="left", expand=True, fill="x"
            )
            self.make_button(
                row, "Önizle", lambda p=path: self.show_photo_preview(p),
                "#d9658b", padx=8, pady=4
            ).pack(side="right")

    def show_photo_preview(self, path):
        if not os.path.exists(path):
            messagebox.showerror(
                "Fotoğraf bulunamadı",
                f"Dosya artık mevcut değil:\n{path}",
                parent=self.root,
            )
            return
        try:
            photo = tk.PhotoImage(file=path)
        except tk.TclError:
            self.open_path(path)
            return
        scale = max(
            math.ceil(photo.width() / 700),
            math.ceil(photo.height() / 700),
            1,
        )
        if scale > 1:
            photo = photo.subsample(scale, scale)
        window = tk.Toplevel(self.root)
        window.title(Path(path).name)
        window.configure(bg=BG)
        preview = tk.Label(window, image=photo, bg=BG)
        preview.image = photo
        preview.pack(padx=12, pady=12)
        tk.Label(
            window, text=Path(path).name, bg=BG, fg=TEXT,
            font=("Segoe UI", 9)
        ).pack(padx=12, pady=(0, 10))

    def show_browser(self):
        body = self.app_page("İnternet")
        tk.Label(
            body, text="Adres veya arama kelimesi", bg=BG, fg=TEXT,
            font=("Segoe UI", 11)
        ).pack(anchor="w", pady=(8, 5))
        address = tk.Entry(body, font=("Segoe UI", 12), bg=CARD, fg=TEXT,
                           insertbackground=TEXT, relief="flat")
        address.pack(fill="x", ipady=9)
        address.bind("<Return>", lambda _event: self.open_web(address.get()))
        self.make_button(body, "Aç", lambda: self.open_web(address.get()),
                         "#4182a7", height=2).pack(fill="x", pady=8)
        tk.Label(
            body, text="İnternet sayfaları bilgisayarındaki varsayılan tarayıcıda açılır.",
            bg=BG, fg=MUTED, font=("Segoe UI", 9), wraplength=300, justify="left"
        ).pack(anchor="w", pady=8)

    def open_web(self, address):
        address = address.strip()
        if not address:
            messagebox.showinfo("İnternet", "Bir web adresi veya arama kelimesi yaz.")
            return
        if " " in address or "." not in address:
            url = "https://www.google.com/search?q=" + quote_plus(address)
        else:
            url = address if "://" in address else "https://" + address
        if not webbrowser.open(url):
            messagebox.showerror("İnternet", "Varsayılan tarayıcı açılamadı.")

    def show_files(self):
        body = self.app_page("Dosyalar")
        self.make_button(body, "Klasör seç", self.choose_directory,
                         "#598c53", height=2).pack(fill="x", pady=(0, 8))
        self.directory_label = tk.Label(
            body, text="", bg=BG, fg=MUTED, font=("Segoe UI", 9),
            wraplength=300, justify="left"
        )
        self.directory_label.pack(anchor="w", pady=(0, 8))
        self.file_list = tk.Listbox(
            body, bg=CARD, fg=TEXT, selectbackground=ACCENT,
            font=("Segoe UI", 10), relief="flat"
        )
        self.file_list.pack(fill="both", expand=True)
        self.file_list.bind("<Double-Button-1>", self.open_selected_file)
        self.render_files()

    def choose_directory(self):
        selected = filedialog.askdirectory(title="Klasör seç")
        if selected:
            self.current_directory = Path(selected)
            self.render_files()

    def render_files(self):
        self.directory_label.config(text=str(self.current_directory))
        self.file_list.delete(0, "end")
        try:
            self.visible_files = sorted(
                self.current_directory.iterdir(), key=lambda path: (not path.is_dir(), path.name.casefold())
            )
        except OSError as error:
            messagebox.showerror("Klasör açılamadı", str(error))
            self.visible_files = []
        for path in self.visible_files:
            prefix = "[Klasör] " if path.is_dir() else ""
            self.file_list.insert("end", prefix + path.name)

    def open_selected_file(self, _event=None):
        selection = self.file_list.curselection()
        if not selection:
            return
        path = self.visible_files[selection[0]]
        if path.is_dir():
            self.current_directory = path
            self.render_files()
        else:
            self.open_path(str(path))

    def open_path(self, path):
        if not os.path.exists(path):
            messagebox.showerror("Dosya bulunamadı", f"Dosya artık mevcut değil:\n{path}")
            return
        try:
            os.startfile(path)
        except OSError as error:
            messagebox.showerror("Dosya açılamadı", str(error))


if __name__ == "__main__":
    root = tk.Tk()
    PhoneSimulator(root)
    root.mainloop()
