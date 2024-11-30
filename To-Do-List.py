import flet as ft
from datetime import datetime
import sqlite3
import threading
import time
import os
import json
from plyer import notification
import winsound
import platform

class TodoApp:
    def __init__(self):
        self.db_file = 'todo.db'
        self.setup_database()
        
        if not os.path.exists('alarms'):
            os.makedirs('alarms')
        
        self.setup_config()
        
    def setup_database(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                completed BOOLEAN DEFAULT FALSE,
                priority INTEGER DEFAULT 0,
                category TEXT DEFAULT 'Genel',
                notes TEXT,
                due_date TEXT,
                due_time TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                has_alarm BOOLEAN DEFAULT FALSE
            )
        ''')
        conn.commit()
        conn.close()

    def setup_config(self):
        config_file = 'todo_config.json'
        if not os.path.exists(config_file):
            default_config = {
                'selected_alarm': 'alarm-clock.wav'
            }
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=4)

    def get_tasks(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks ORDER BY priority DESC, created_at DESC')
        tasks = cursor.fetchall()
        conn.close()
        return tasks

    def add_task(self, text, priority=0, category="Genel", notes="", due_date=None, due_time=None, has_alarm=False):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (text, priority, category, notes, due_date, due_time, has_alarm)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (text, priority, category, notes, due_date, due_time, has_alarm))
        conn.commit()
        conn.close()

    def toggle_task(self, task_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('UPDATE tasks SET completed = NOT completed WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()

    def delete_task(self, task_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()
    # Config işlemleri
def load_config():
    try:
        with open('todo_config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        default_config = {'selected_alarm': 'alarm-clock.wav'}
        save_config(default_config)
        return default_config

def save_config(config):
    try:
        with open('todo_config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Config kaydedilirken hata: {e}")

def get_alarm_list():
    alarm_files = []
    alarm_dir = 'alarms'
    
    if not os.path.exists(alarm_dir):
        os.makedirs(alarm_dir)
    
    for file in os.listdir(alarm_dir):
        if file.lower().endswith('.wav'):
            alarm_files.append(file)
    
    if not alarm_files:
        default_alarm = 'alarm-clock.wav'
        alarm_files = [default_alarm]
    
    return alarm_files

def play_alarm_sound(duration=None):
    if platform.system() == 'Windows':
        try:
            config = load_config()
            selected_alarm = config.get('selected_alarm')
            
            sound_file = os.path.join('alarms', selected_alarm)
            
            if os.path.exists(sound_file):
                if duration:
                    winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
                    time.sleep(duration)
                    winsound.PlaySound(None, winsound.SND_PURGE)
                else:
                    winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
            else:
                winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS)
        except Exception as e:
            print(f"Ses çalma hatası: {e}")
            winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS)

def show_task_details(page, task):
    task_id, text, completed, priority, category, notes, due_date, due_time, created_at, has_alarm = task
    
    priority_names = {
        0: "Normal",
        1: "Önemli",
        2: "Acil"
    }
    
    def close_dialog(e):
        details_dialog.open = False
        page.update()

    details_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Görev Detayları", size=20, weight=ft.FontWeight.BOLD),
        content=ft.Container(
            content=ft.Column([
                ft.Text("Görev:", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(text, size=16, color="blue"),
                ft.Divider(),
                ft.Text("Kategori:", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(category, size=16),
                ft.Divider(),
                ft.Text("Öncelik:", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(priority_names.get(priority, "Normal"), size=16),
                ft.Divider(),
                ft.Text("Tarih ve Saat:", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(
                    f"{due_date or 'Belirtilmemiş'} {due_time or ''}", 
                    size=16
                ),
                ft.Divider(),
                ft.Text("Notlar:", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(notes or "Not bulunmuyor", size=16),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(
                            name=ft.icons.ALARM,
                            color="blue" if has_alarm else "grey",
                            size=20,
                        ),
                        ft.Text(
                            "Alarm aktif" if has_alarm else "Alarm yok",
                            size=14,
                            color="blue" if has_alarm else "grey"
                        )
                    ]),
                    margin=ft.margin.only(top=10)
                )
            ]),
            padding=20
        ),
        actions=[
            ft.TextButton("Kapat", on_click=close_dialog),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(details_dialog)
    details_dialog.open = True
    page.update()

def show_reminder_dialog(page, task, alarm_playing=True):
    def close_dialog(e):
        if alarm_playing:
            winsound.PlaySound(None, winsound.SND_PURGE)
        dialog.open = False
        page.update()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("🔔 Görev Hatırlatması!", size=20, color="blue"),
        content=ft.Container(
            content=ft.Column([
                ft.Text(
                    f'"{task[1]}" görevi için zaman geldi!',
                    size=16,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Text(f"Kategori: {task[4]}", size=14),
                ft.Text(f"Notlar: {task[5] or 'Not yok'}", size=14),
            ]),
            padding=10
        ),
        actions=[
            ft.TextButton("Tamam", on_click=close_dialog),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dialog)
    dialog.open = True
    page.update()

def show_about(page):
    def close_dialog(e):
        about_dlg.open = False
        page.update()

    about_dlg = ft.AlertDialog(
        title=ft.Text("Hakkında", size=20, weight=ft.FontWeight.BOLD),
        content=ft.Column([
            ft.Text("Yapılacaklar Listesi", size=16),
            ft.Text("Versiyon: 1.0", size=14),
            ft.Text("Yazar: Önder AKÖZ", size=14),
            ft.Text("E-posta: onder7@gmail.com", size=14),
        ], tight=True),
        actions=[
            ft.TextButton("Tamam", on_click=close_dialog),
        ],
    )

    page.overlay.append(about_dlg)
    about_dlg.open = True
    page.update()

def show_success_dialog(page, message):
    def close_dialog(e):
        success_dialog.open = False
        page.update()

    success_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Başarılı", size=20, color="blue"),
        content=ft.Text(message),
        actions=[
            ft.TextButton("Tamam", on_click=close_dialog),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(success_dialog)
    success_dialog.open = True
    page.update()

def show_error_dialog(page, message):
    def close_dialog(e):
        error_dialog.open = False
        page.update()

    error_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Hata", size=20, color="red"),
        content=ft.Text(message),
        actions=[
            ft.TextButton("Tamam", on_click=close_dialog),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(error_dialog)
    error_dialog.open = True
    page.update()

def toggle_theme(page, theme_icon_button):
    page.theme_mode = (
        ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
    )
    theme_icon_button.icon = (
        ft.icons.DARK_MODE if page.theme_mode == ft.ThemeMode.LIGHT else ft.icons.LIGHT_MODE
    )
    page.update()
def check_alarms(app, page):
    while True:
        try:
            now = datetime.now()
            current_date = now.strftime('%Y-%m-%d')
            current_time = now.strftime('%H:%M')
            
            tasks = app.get_tasks()
            for task in tasks:
                if (task[6] == current_date and 
                    task[7] == current_time and 
                    task[9] and  
                    not task[2]):
                    
                    play_alarm_sound()
                    show_reminder_dialog(page, task, alarm_playing=True)
                    notification.notify(
                        title='🔔 Görev Hatırlatması!',
                        message=f'"{task[1]}" görevi için zaman geldi!\n\nKategori: {task[4]}\nNotlar: {task[5] or "Not yok"}',
                        app_icon=None,
                        timeout=10,
                    )
                    time.sleep(2)
            time.sleep(30)
        except Exception as e:
            print(f"Alarm kontrol hatası: {e}")
            time.sleep(30)

def show_task_dialog(page, message, title="Görev Eklendi", color="blue"):
    def close_dialog(e):
        dialog.open = False
        page.update()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(title, size=20, color=color),
        content=ft.Container(
            content=ft.Row([
                ft.Icon(name=ft.icons.INFO, color=color, size=24),
                ft.Text(message, size=16)
            ], alignment=ft.MainAxisAlignment.START),
            padding=10
        ),
        actions=[
            ft.TextButton("Tamam", on_click=close_dialog),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dialog)
    dialog.open = True
    page.update()

def show_alarm_settings(page):
    try:
        def save_alarm_selection(e):
            try:
                selected = alarm_dropdown.value
                if not selected:
                    show_error_dialog(page, "Lütfen bir alarm sesi seçin!")
                    return
                    
                config = load_config()
                config['selected_alarm'] = selected
                save_config(config)
                
                dlg_modal.open = False
                page.update()
                
                show_success_dialog(page, "Alarm sesi başarıyla kaydedildi!")
                
            except Exception as e:
                print(f"Alarm seçimi kaydedilirken hata: {e}")
                show_error_dialog(page, f"Alarm sesi kaydedilirken bir hata oluştu: {str(e)}")

        def test_alarm(e):
            if not alarm_dropdown.value:
                show_error_dialog(page, "Lütfen önce bir alarm sesi seçin!")
                return
            play_alarm_sound(duration=3)

        def close_dialog(e):
            dlg_modal.open = False
            page.update()

        alarm_list = get_alarm_list()
        current_config = load_config()
        
        alarm_dropdown = ft.Dropdown(
            width=400,
            options=[ft.dropdown.Option(alarm) for alarm in alarm_list],
            value=current_config.get('selected_alarm'),
            label="Alarm Sesi",
            hint_text="Bir alarm sesi seçin"
        )

        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Alarm Sesi Ayarları", size=20, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Lütfen kullanmak istediğiniz alarm sesini seçin:", size=16),
                    alarm_dropdown,
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        "Test Et",
                        icon=ft.icons.VOLUME_UP,
                        on_click=test_alarm,
                        style=ft.ButtonStyle(
                            color=ft.colors.WHITE,
                            bgcolor=ft.colors.BLUE
                        )
                    )
                ], tight=True),
                padding=20
            ),
            actions=[
                ft.TextButton("İptal", on_click=close_dialog),
                ft.TextButton("Kaydet", on_click=save_alarm_selection),
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        page.overlay.append(dlg_modal)
        dlg_modal.open = True
        page.update()
        
    except Exception as e:
        print(f"Ayarlar açılırken hata: {e}")
        show_error_dialog(page, "Ayarlar açılırken bir hata oluştu!")

def main(page: ft.Page):
    try:
        page.title = "Yapılacaklar Listesi"
        page.window.width = 800  # Düzeltilmiş kullanım
        page.window.height = 600  # Düzeltilmiş kullanım
        page.padding = 20
        page.scroll = ft.ScrollMode.AUTO
        page.theme_mode = ft.ThemeMode.LIGHT
        
        app = TodoApp()

        def update_task_list():
            tasks_view.controls.clear()
            for task in app.get_tasks():
                task_id, text, completed, priority, category, notes, due_date, due_time, created_at, has_alarm = task
                
                priority_colors = {0: "grey", 1: "orange", 2: "red"}
                priority_color = priority_colors.get(priority, "grey")
                
                is_overdue = False
                if due_date:
                    now = datetime.now()
                    task_date = datetime.strptime(f"{due_date} {due_time or '23:59'}", '%Y-%m-%d %H:%M')
                    is_overdue = now > task_date and not completed

                # Görev metnini kısalt
                display_text = text[:30] + "..." if len(text) > 30 else text
                
                task_row = ft.Container(
                    content=ft.Row(
                        [
                            ft.Row(
                                [
                                    ft.Checkbox(
                                        value=completed,
                                        on_change=lambda e, tid=task_id: handle_task_toggle(e, tid)
                                    ),
                                    # Text widget'ı için style kullanımı
                                    ft.Container(
                                        content=ft.Text(
                                            display_text,
                                            size=14,
                                            color=ft.colors.RED if is_overdue else priority_color,
                                            weight=ft.FontWeight.BOLD,
                                            style=ft.TextStyle(
                                                decoration=ft.TextDecoration.LINE_THROUGH if completed else None,
                                                decoration_color="grey" if completed else None,
                                            ),
                                        ),
                                        tooltip="Detayları görüntülemek için tıklayın",
                                        on_click=lambda e, t=task: show_task_details(page, t),
                                    ),
                                ],
                                width=300,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    due_date if due_date else "",
                                    size=14,
                                    style=ft.TextStyle(
                                        decoration=ft.TextDecoration.LINE_THROUGH if completed else None,
                                        decoration_color="grey" if completed else None,
                                    ),
                                ),
                                width=100,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    due_time if due_time else "",
                                    size=14,
                                    style=ft.TextStyle(
                                        decoration=ft.TextDecoration.LINE_THROUGH if completed else None,
                                        decoration_color="grey" if completed else None,
                                    ),
                                ),
                                width=80,
                            ),
                            ft.Icon(
                                name=ft.icons.ALARM,
                                color="blue" if has_alarm else "grey",
                                size=16,
                                opacity=0.5 if completed else 1.0,
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE_OUTLINE,
                                icon_color="red",
                                on_click=lambda e, tid=task_id: handle_task_delete(tid, page)
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    bgcolor=ft.colors.BLUE_GREY_50 if completed else None,
                    padding=10,
                    on_click=lambda e, t=task: show_task_details(page, t),
                )
                tasks_view.controls.append(task_row)
            page.update()

        def handle_task_toggle(e, task_id):
            app.toggle_task(task_id)
            update_task_list()

        def handle_task_delete(task_id, page_ref):
            app.delete_task(task_id)
            show_task_dialog(page_ref, "Görev başarıyla silindi!", "Görev Silindi", "red")
            update_task_list()

        def handle_submit(e):
            if task_input.value:
                current_datetime = datetime.now()
                selected_date = date_picker.value.strftime('%Y-%m-%d') if date_picker.value else current_datetime.strftime('%Y-%m-%d')
                selected_time = time_picker.value.strftime('%H:%M') if time_picker.value else current_datetime.strftime('%H:%M')
                
                app.add_task(
                    task_input.value,
                    int(priority_dd.value or 0),
                    category_dd.value or "Genel",
                    notes_input.value,
                    selected_date,
                    selected_time,
                    alarm_checkbox.value
                )
                
                show_task_dialog(page, "Yeni görev başarıyla eklendi!")
                
                # Formu temizle
                task_input.value = ""
                notes_input.value = ""
                priority_dd.value = "0"
                category_dd.value = "Genel"
                date_picker.value = None
                time_picker.value = None
                alarm_checkbox.value = False
                update_task_list()
                page.update()

        # Zaman bilgisi için container
        def create_time_info():
            now = datetime.now()
            weekdays = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
            return ft.Row([
                ft.Text(
                    f"{now.strftime('%d.%m.%Y')} {weekdays[now.weekday()]} {now.strftime('%H:%M')}",
                    size=14,
                    color=ft.colors.BLUE_GREY_400,
                ),
            ])

        time_info = create_time_info()
        
        def update_time():
            while True:
                time.sleep(60)
                now = datetime.now()
                weekdays = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
                time_info.controls[0].value = f"{now.strftime('%d.%m.%Y')} {weekdays[now.weekday()]} {now.strftime('%H:%M')}"
                page.update()

        time_thread = threading.Thread(target=update_time, daemon=True)
        time_thread.start()

        # UI Bileşenleri
        tasks_view = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=10,
            height=400
        )

        task_input = ft.TextField(
            hint_text="Yeni görev ekle...",
            expand=True,
            on_submit=lambda e: handle_submit(e)
        )
        
        notes_input = ft.TextField(
            hint_text="Notlar (opsiyonel)",
            expand=True,
            multiline=True,
            min_lines=2
        )
        
        priority_dd = ft.Dropdown(
            width=150,
            options=[
                ft.dropdown.Option("0", "Normal"),
                ft.dropdown.Option("1", "Önemli"),
                ft.dropdown.Option("2", "Acil")
            ],
            value="0"
        )
        
        category_dd = ft.Dropdown(
            width=150,
            options=[
                ft.dropdown.Option("Genel"),
                ft.dropdown.Option("İş"),
                ft.dropdown.Option("Kişisel"),
                ft.dropdown.Option("Alışveriş"),
                ft.dropdown.Option("Sağlık")
            ],
            value="Genel"
        )

        date_picker = ft.DatePicker(
            first_date=datetime(2024, 1, 1),
            last_date=datetime(2025, 12, 31),
        )
        page.overlay.append(date_picker)

        time_picker = ft.TimePicker()
        page.overlay.append(time_picker)

        def date_picker_button_clicked(e):
            date_picker.open = True
            page.update()

        def time_picker_button_clicked(e):
            time_picker.open = True
            page.update()

        date_button = ft.ElevatedButton(
            "Tarih Seç",
            icon=ft.icons.CALENDAR_TODAY,
            on_click=date_picker_button_clicked
        )
        
        time_button = ft.ElevatedButton(
            "Saat Seç",
            icon=ft.icons.ACCESS_TIME,
            on_click=time_picker_button_clicked
        )

        alarm_checkbox = ft.Checkbox(
            label="Alarm Ekle",
            value=False,
            tooltip="Seçilen tarih ve saatte bildirim gönderir"
        )

        alarm_info = ft.Text(
            "❗ Alarm seçildiğinde, belirtilen tarih ve saatte bildirim alacaksınız.",
            size=12,
            color="blue",
            italic=True
        )

        # Liste başlığı
        header_row = ft.Container(
            content=ft.Row(
                [
                    ft.Text("Görev", size=14, weight=ft.FontWeight.BOLD, width=300),
                    ft.Text("Tarih", size=14, weight=ft.FontWeight.BOLD, width=100),
                    ft.Text("Saat", size=14, weight=ft.FontWeight.BOLD, width=80),
                    ft.Text("Alarm", size=14, weight=ft.FontWeight.BOLD, width=60),
                    ft.Text("İşlem", size=14, weight=ft.FontWeight.BOLD, width=50),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=ft.colors.BLUE_GREY_100,
            padding=10,
            border_radius=ft.border_radius.only(top_left=5, top_right=5),
        )

        # Üst bar
        # Üst bar
        top_bar = ft.Container(
            content=ft.Row(
                [
                    time_info,
                    ft.Row([
                        ft.IconButton(
                            icon=ft.icons.DARK_MODE if page.theme_mode == ft.ThemeMode.LIGHT else ft.icons.LIGHT_MODE,
                            tooltip="Tema Değiştir",
                            on_click=lambda e: toggle_theme(page, e.control)
                        ),
                        ft.IconButton(
                            icon=ft.icons.INFO,
                            tooltip="Hakkında",
                            on_click=lambda e: show_about(page)
                        ),
                        ft.IconButton(
                            icon=ft.icons.SETTINGS,
                            tooltip="Alarm Ayarları",
                            on_click=lambda e: show_alarm_settings(page)
                        ),
                    ]),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=10,
            margin=ft.margin.only(bottom=10),
            border_radius=10,
            bgcolor=ft.colors.BLUE_GREY_50,
        )

        # Ana container
        content = ft.Container(
            content=ft.Column([
                top_bar,
                ft.Row([
                    ft.Text("Yapılacaklar Listesi", size=32, weight=ft.FontWeight.BOLD),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(
                    content=ft.Column([
                        task_input,
                        ft.Row([priority_dd, category_dd]),
                        notes_input,
                        ft.Row([
                            date_button,
                            time_button,
                            alarm_checkbox
                        ]),
                        alarm_info,
                        ft.ElevatedButton(
                            text="Ekle",
                            icon=ft.icons.ADD,
                            on_click=handle_submit
                        )
                    ]),
                    padding=ft.padding.only(bottom=20)
                ),
                ft.Divider(),
                ft.Container(
                    content=ft.Column([
                        header_row,
                        tasks_view,
                    ]),
                    border=ft.border.all(1, ft.colors.BLUE_GREY_100),
                    border_radius=10,
                    padding=0,
                    expand=True
                )
            ]),
            expand=True
        )

        # Alarm thread'ini başlat
        alarm_thread = threading.Thread(target=check_alarms, args=(app, page), daemon=True)
        alarm_thread.start()

        page.add(content)
        update_task_list()

    except Exception as e:
        print(f"Uygulama başlatma hatası: {e}")
        error_content = ft.Column([
            ft.Text("Uygulama başlatılırken bir hata oluştu!", size=20, color="red"),
            ft.Text(f"Hata detayı: {str(e)}", size=14),
            ft.ElevatedButton("Yeniden Dene", on_click=lambda _: page.window.close())
        ])
        page.add(error_content)
        page.update()

if __name__ == '__main__':
    ft.app(target=main)
