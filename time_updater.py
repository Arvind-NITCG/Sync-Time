import sys
import socket
import struct
import time
import ctypes
import datetime

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_ntp_time(server="pool.ntp.org"):
    
    NTP_EPOCH_DELTA = 2208988800
    
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(5)
    
    data = b'\x1b' + 47 * b'\0'
    
    try:
        print(f" Connecting to {server}...")
        client.sendto(data, (server, 123))
        data, address = client.recvfrom(1024)
        if data:
            
            t = struct.unpack('!12I', data)[10]
            t -= NTP_EPOCH_DELTA
            return t
    except Exception as e:
        print(f" Error fetching time: {e}")
        return None

def set_system_time(timestamp):
    
    utc_time = datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc)

    class SYSTEMTIME(ctypes.Structure):
        _fields_ = [
            ("wYear", ctypes.c_ushort),
            ("wMonth", ctypes.c_ushort),
            ("wDayOfWeek", ctypes.c_ushort),
            ("wDay", ctypes.c_ushort),
            ("wHour", ctypes.c_ushort),
            ("wMinute", ctypes.c_ushort),
            ("wSecond", ctypes.c_ushort),
            ("wMilliseconds", ctypes.c_ushort),
        ]

    st = SYSTEMTIME()
    st.wYear = utc_time.year
    st.wMonth = utc_time.month
    st.wDayOfWeek = utc_time.weekday()
    st.wDay = utc_time.day
    st.wHour = utc_time.hour
    st.wMinute = utc_time.minute
    st.wSecond = utc_time.second
    st.wMilliseconds = 0

    result = ctypes.windll.kernel32.SetSystemTime(ctypes.byref(st))
    if result:
        print(f" Success! Time updated to: {time.ctime(timestamp)}")
    else:
        print(" Failed to set system time. (Check permissions?)")

if __name__ == "__main__":
    if not is_admin():
        print("⚠️  This script requires Administrator privileges to set the clock.")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        print(" Checking Internet Time...")
        # Try Indian NTP pool first, then global
        servers = ["in.pool.ntp.org", "pool.ntp.org", "time.google.com"]
        
        for server in servers:
            ts = get_ntp_time(server)
            if ts:
                set_system_time(ts)
                break
            else:
                print(f"⚠️  Could not reach {server}, trying next...")
        
        time.sleep(3)