#  Atomic Time Sync (Cross-Platform OS Utility)

A lightweight, hardware-agnostic utility designed to dynamically synchronize the system wall-clock with atomic NTP servers. Originally engineered to bypass a physical hardware failure (a depleted CMOS/RTC battery), this project evolved into a scalable, cross-platform system utility with an automated CI/CD distribution pipeline.

##  The Hardware Problem
When a motherboard's CMOS battery fails, the system loses its Real-Time Clock (RTC) state upon power loss. This hardware limitation cascades into severe software failures:
* **Cryptography:** TLS/SSL certificates instantly invalidate, breaking secure web browsing.
* **OS Scheduling:** Completely Fair Scheduler (CFS) and background chron jobs fail due to corrupted `vruntime` and system tick data.
* **Filesystems:** Log files and file modification timestamps become severely corrupted.

##  The Engineering Solution
Instead of a manual fix, I engineered a Python-based GUI application that bypasses the broken hardware clock by fetching true atomic time and injecting it directly into the OS Kernel. 

The architecture handles low-level OS mechanics across Windows, Linux, and macOS:
1.  **Network I/O & Interrupts:** Opens a raw UDP socket (`SOCK_DGRAM`) on Port 123. The process voluntarily enters the **Blocked/Waiting Queue** until the physical NIC receives the 48-byte NTP packet and fires a hardware interrupt to wake the process.
2.  **Dynamic Privilege Escalation:** Checks the Process Control Block (PCB). It evaluates Windows UAC access tokens via `shell32.dll` or queries the Effective User ID (`EUID == 0`) on POSIX systems to ensure Kernel-level write permissions.
3.  **Cross-Platform System Calls:** * **Windows:** Uses Python's `ctypes` to map a 16-byte C-structure (`SYSTEMTIME`) and passes a memory pointer to the Win32 API (`kernel32.SetSystemTime`), crossing from User Mode to Kernel Mode.
    * **Linux/macOS:** Dynamically detects the environment and routes the update through POSIX-standard system calls (`clock_settime`) or root-level binary executions.

##  Tech Stack & Architecture
* **Language:** Python 3 (Object-Oriented GUI via `tkinter`)
* **Low-Level Interfaces:** `ctypes`, Win32 API, POSIX System Calls
* **Networking:** Raw UDP Sockets, Big-Endian to Little-Endian bitwise translation.
* **DevOps (CI/CD):** GitHub Actions

##  CI/CD Pipeline & Distribution
This project utilizes **Infrastructure as Code (YAML)** to automate compilation. 
Upon every push to the `main` branch, a GitHub Actions Matrix Strategy simultaneously spins up three isolated cloud environments (`windows-latest`, `ubuntu-latest`, `macos-latest`). It installs `PyInstaller` and natively compiles the high-level Python script into standalone executables for all three major operating systems.

##  How to Use
1.  Navigate to the **[Actions](../../releases/latest)** section of this repository and download the required artifacts for your operating system.
2.  Download the compiled binary for your specific OS:
    * **Windows:** `TimeSync-windows.exe`
    * **Linux:** `TimeSync-linux` (ELF Binary)
    * **macOS:** `TimeSync-macos.app`
3.  Run the application (Requires Administrator / `sudo` privileges to execute the Kernel-level system calls).
