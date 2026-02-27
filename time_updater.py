import sys
import os
import socket
import struct
import time
import datetime
import platform
import tkinter as tk
from tkinter import messagebox
import subprocess

def check_privileges():
    """Dynamically checks for Admin/Root based on the OS."""
    current_os = platform.system()
    if current_os == "Windows":
        import ctypes
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    else:
        return os.geteuid() == 0

def get_ntp_time(server="pool.ntp.org"):
    """Fetches atomic time from NTP server."""
    NTP_EPOCH_DELTA = 2208988800
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(5)
    data = b'\x1b' + 47 * b'\0'
    try:
        client.sendto(data, (server, 123))
        data, address = client.recvfrom(1024)
        if data:
            t = struct.unpack('!12I', data)[10]
            return t - NTP_EPOCH_DELTA
    except Exception as e:
        return None

def set_system_time(timestamp):
    """Routes the hardware clock update to the correct OS Kernel."""
    current_os = platform.system()
    
    if current_os == "Windows":
        import ctypes
        utc_time = datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc)
        class SYSTEMTIME(ctypes.Structure):
            _fields_ = [("wYear", ctypes.c_ushort), ("wMonth", ctypes.c_ushort),
                        ("wDayOfWeek", ctypes.c_ushort), ("wDay", ctypes.c_ushort),
                        ("wHour", ctypes.c_ushort), ("wMinute", ctypes.c_ushort),
                        ("wSecond", ctypes.c_ushort), ("wMilliseconds", ctypes.c_ushort)]
        st = SYSTEMTIME()
        st.wYear, st.wMonth, st.wDayOfWeek, st.wDay = utc_time.year, utc_time.month, utc_time.weekday(), utc_time.day
        st.wHour, st.wMinute, st.wSecond, st.wMilliseconds = utc_time.hour, utc_time.minute, utc_time.second, 0
        
        return ctypes.windll.kernel32.SetSystemTime(ctypes.byref(st)) != 0

    elif current_os == "Linux":
        try:
            time.clock_settime(time.CLOCK_REALTIME, float(timestamp))
            return True
        except AttributeError:
            return subprocess.call(['date', '-s', f'@{timestamp}']) == 0

    elif current_os == "Darwin":  
        return subprocess.call(['date', '-f', '%s', str(timestamp)]) == 0
        
    return False

class TimeSyncGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Atomic Time Sync")
        self.root.geometry("350x200")
        self.root.eval('tk::PlaceWindow . center')

        os_name = platform.system()
        tk.Label(root, text=f"Detected OS: {os_name}", font=("Helvetica", 10, "bold")).pack(pady=10)

        self.status_label = tk.Label(root, text="Ready to sync...", fg="gray")
        self.status_label.pack(pady=10)

        self.sync_btn = tk.Button(root, text="Sync Hardware Clock", command=self.run_sync, bg="#4CAF50", fg="white", font=("Helvetica", 12))
        self.sync_btn.pack(pady=20)

    def run_sync(self):
        self.status_label.config(text="Fetching atomic time...", fg="blue")
        self.root.update()

        servers = ["in.pool.ntp.org", "pool.ntp.org", "time.google.com"]
        for server in servers:
            ts = get_ntp_time(server)
            if ts:
                success = set_system_time(ts)
                if success:
                    local_time = time.ctime(ts)
                    self.status_label.config(text=f"Success! \n{local_time}", fg="green")
                    messagebox.showinfo("System Clock Updated", f"Hardware clock successfully aligned to {server}.")
                    return
                else:
                    self.status_label.config(text="Failed to set OS time.", fg="red")
                    return
        self.status_label.config(text="Network Error. Could not reach NTP.", fg="red")

if __name__ == "__main__":
    if not check_privileges():
        current_os = platform.system()
        if current_os == "Windows":
            import ctypes
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        else:
            print("Please run this script with 'sudo' on Linux/macOS.")
            sys.exit(1)
    else:
        app = tk.Tk()
        gui = TimeSyncGUI(app)
        app.mainloop()