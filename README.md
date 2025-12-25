#  Auto Time Sync (Windows)

A lightweight, automated utility to synchronize Windows System Time with accurate atomic clocks (NTP), specifically designed for systems with hardware failures (CMOS/RTC issues).

## 🛑 The Problem
My laptop's CMOS battery failed, meaning the system clock resets every time the power is cut. Manually syncing the time after every reboot was inefficient and broke SSL certificates/browsing.

## ⚡ The Solution
I engineered a Python-based background service that:
1.  **Connects** to high-precision NTP servers (Network Time Protocol).
2.  **Bypasses** the broken hardware clock.
3.  **Injects** the correct time directly into the Windows Kernel using `ctypes`.
4.  **Runs Silently** as a standalone executable.

## 🛠️ Tech Stack
* **Language:** Python 3.12
* **OS Interaction:** `ctypes` (Win32 API)
* **Networking:** Raw Sockets (NTP Packet handling)
* **Build:** PyInstaller (Compiled to standalone `.exe`)

## 🚀 How to Use
1.  Go to the **[Releases](link-to-your-releases)** section on the right.
2.  Download `fix_time.exe`.
3.  Set it in **Task Scheduler** to run "At Log On" with Admin privileges.