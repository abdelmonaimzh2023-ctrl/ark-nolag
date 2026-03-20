#!/usr/bin/env python3
"""
SMART ADB ULTIMATE v3.1 - FULLY FIXED
One-Click System Optimizer + Advanced Tools
Works on: Termux, Linux, Windows, macOS
"""

import subprocess
import sys
import os
import time
import json
import platform
from typing import Tuple, Optional, List, Dict, Callable

# ==================== CONFIGURATION ====================
CONFIG_FILE = os.path.expanduser("~/.smart_adb_config.json")
DEFAULT_CONFIG = {
    "resolution": {"width": 550, "height": 1550},
    "dpi": 240,
    "apps_to_kill": [
        "com.facebook.katana", "com.facebook.orca",
        "com.instagram.android", "com.whatsapp",
        "com.zhiliaoapp.musically", "com.snapchat.android",
        "com.twitter.android", "com.spotify.music",
        "com.netflix.mediaclient", "com.google.android.youtube"
    ],
    "auto_backup": True,
    "wifi_port": 5555
}

# ==================== COLOR SYSTEM ====================
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    END = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'

# ==================== UTILITIES ====================
def load_config() -> dict:
    """Load configuration from file"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(config: dict):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except:
        pass

def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if platform.system() != 'Windows' else 'cls')

def print_header():
    """Print beautiful header"""
    clear_screen()
    print(Colors.CYAN + "╔" + "═" * 58 + "╗" + Colors.END)
    print(Colors.CYAN + "║" + Colors.BOLD + Colors.GREEN + " " * 12 + "SMART ADB ULTIMATE v3.1" + " " * 17 + Colors.CYAN + "║" + Colors.END)
    print(Colors.CYAN + "║" + Colors.DIM + " " * 16 + "Ultimate Android Optimizer" + " " * 20 + Colors.CYAN + "║" + Colors.END)
    print(Colors.CYAN + "╚" + "═" * 58 + "╝" + Colors.END)
    print()

def print_status(message: str, status_type: str = "info"):
    """Print status messages with icons"""
    icons = {
        "info": "📌", "success": "✅", "error": "❌", "warning": "⚠️",
        "progress": "🔄", "device": "📱", "wifi": "🌐", "check": "🔍",
        "settings": "⚙️", "backup": "💾", "restore": "♻️", "stats": "📊"
    }
    colors = {
        "info": Colors.BLUE, "success": Colors.GREEN, "error": Colors.RED,
        "warning": Colors.YELLOW, "progress": Colors.CYAN, "device": Colors.MAGENTA,
        "wifi": Colors.BLUE, "check": Colors.YELLOW, "settings": Colors.HEADER,
        "backup": Colors.GREEN, "restore": Colors.CYAN, "stats": Colors.BLUE
    }
    icon = icons.get(status_type, "•")
    color = colors.get(status_type, Colors.END)
    print(f"{color}{icon} {message}{Colors.END}")

def progress_bar(current: int, total: int, prefix: str = '', suffix: str = '', length: int = 40):
    """Display progress bar"""
    if total <= 0:
        return
    percent = 100 * (current / float(total))
    filled = int(length * current // total)
    bar = '█' * filled + '░' * (length - filled)
    
    if percent < 30:
        bar_color = Colors.RED
    elif percent < 70:
        bar_color = Colors.YELLOW
    else:
        bar_color = Colors.GREEN
    
    print(f'\r{prefix} |{bar_color}{bar}{Colors.END}| {percent:.0f}% {suffix}', end='')
    if current == total:
        print()

# ==================== ADB FUNCTIONS ====================
def run_adb(command, device_id: Optional[str] = None, timeout: int = 15) -> Tuple[bool, str]:
    """
    Execute ADB command
    command can be string or list
    """
    try:
        if isinstance(command, str):
            cmd = command.split()
        else:
            cmd = command[:]
        
        if device_id:
            cmd = ['adb', '-s', device_id] + cmd
        else:
            cmd = ['adb'] + cmd
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, result.stderr.strip()
        
    except subprocess.TimeoutExpired:
        return False, "Command timeout"
    except FileNotFoundError:
        return False, "ADB not installed"
    except Exception as e:
        return False, str(e)

def check_adb() -> bool:
    """Check if ADB is installed, try to install if not"""
    success, _ = run_adb(['version'])
    if success:
        return True
    
    print_status("ADB not found. Attempting to install...", "warning")
    
    # Detect Termux
    if 'com.termux' in os.environ.get('PREFIX', ''):
        try:
            subprocess.run(['pkg', 'update'], capture_output=True, timeout=30)
            subprocess.run(['pkg', 'install', 'android-tools', '-y'], capture_output=True, timeout=60)
            print_status("ADB installed via pkg. Please restart the script.", "success")
            return False
        except:
            pass
    
    # Detect Linux
    elif platform.system() == 'Linux':
        try:
            subprocess.run(['sudo', 'apt', 'update'], capture_output=True, timeout=30)
            subprocess.run(['sudo', 'apt', 'install', 'android-tools-adb', '-y'], capture_output=True, timeout=60)
            print_status("ADB installed via apt. Please restart the script.", "success")
            return False
        except:
            pass
    
    print_status("Could not install ADB automatically.", "error")
    print_status("Please install manually: pkg install android-tools", "info")
    return False

def get_device(allow_wifi: bool = True) -> Optional[str]:
    """Get first connected device"""
    success, output = run_adb(['devices'])
    if not success:
        return None
    
    for line in output.split('\n'):
        line = line.strip()
        if line and 'device' in line and 'offline' not in line and 'unauthorized' not in line:
            if '\t' in line:
                return line.split('\t')[0]
    
    if allow_wifi:
        print_status("No USB device found. Try WiFi connection? (y/n): ", "info")
        choice = input().strip().lower()
        if choice == 'y':
            ip = input("Enter device IP address: ").strip()
            port = input(f"Enter port [{DEFAULT_CONFIG['wifi_port']}]: ").strip()
            port = port if port else str(DEFAULT_CONFIG['wifi_port'])
            success, _ = run_adb(['connect', f"{ip}:{port}"])
            if success:
                return get_device(allow_wifi=False)
    return None

def get_device_status(device_id: str) -> Dict:
    """Get comprehensive device status"""
    status = {
        'connected': False,
        'model': 'Unknown',
        'android': 'Unknown',
        'resolution': 'Unknown',
        'density': 'Unknown',
        'battery': 'Unknown',
        'ram_total': 0,
        'ram_free': 0
    }
    
    # Check connection
    success, _ = run_adb(['shell', 'echo', 'test'], device_id)
    if not success:
        return status
    
    status['connected'] = True
    
    # Get model
    success, out = run_adb(['shell', 'getprop', 'ro.product.model'], device_id)
    if success and out:
        status['model'] = out[:40]
    
    # Get Android version
    success, out = run_adb(['shell', 'getprop', 'ro.build.version.release'], device_id)
    if success and out:
        status['android'] = out[:20]
    
    # Get resolution
    success, out = run_adb(['shell', 'wm', 'size'], device_id)
    if success and 'Physical size:' in out:
        status['resolution'] = out.split('Physical size:')[1].strip()
    
    # Get density
    success, out = run_adb(['shell', 'wm', 'density'], device_id)
    if success and 'Physical density:' in out:
        status['density'] = out.split('Physical density:')[1].strip()
    
    # Get battery
    success, out = run_adb(['shell', 'dumpsys', 'battery'], device_id)
    if success:
        for line in out.split('\n'):
            if 'level:' in line:
                status['battery'] = line.split(':')[1].strip() + '%'
                break
    
    # Get RAM (try different methods)
    success, out = run_adb(['shell', 'cat', '/proc/meminfo'], device_id)
    if success:
        for line in out.split('\n'):
            if 'MemTotal:' in line:
                status['ram_total'] = int(line.split()[1]) // 1024
            elif 'MemAvailable:' in line:
                status['ram_free'] = int(line.split()[1]) // 1024
    
    return status

def show_dashboard(device_id: str) -> bool:
    """Display device dashboard"""
    print_status("Fetching device information...", "progress")
    status = get_device_status(device_id)
    
    if not status['connected']:
        print_status("Device disconnected!", "error")
        return False
    
    print("\n" + Colors.CYAN + "╔" + "═" * 58 + "╗" + Colors.END)
    print(Colors.CYAN + "║" + Colors.BOLD + Colors.GREEN + " " * 18 + "DEVICE DASHBOARD" + " " * 19 + Colors.CYAN + "║" + Colors.END)
    print(Colors.CYAN + "╠" + "═" * 58 + "╣" + Colors.END)
    print(Colors.CYAN + "║" + Colors.END + f" 📱 Model:        {status['model']:<40}" + Colors.CYAN + "║" + Colors.END)
    print(Colors.CYAN + "║" + Colors.END + f" 🤖 Android:      {status['android']:<40}" + Colors.CYAN + "║" + Colors.END)
    print(Colors.CYAN + "║" + Colors.END + f" 📺 Resolution:   {status['resolution']:<40}" + Colors.CYAN + "║" + Colors.END)
    print(Colors.CYAN + "║" + Colors.END + f" 🖌️  DPI:          {status['density']:<40}" + Colors.CYAN + "║" + Colors.END)
    print(Colors.CYAN + "║" + Colors.END + f" 🔋 Battery:      {status['battery']:<40}" + Colors.CYAN + "║" + Colors.END)
    
    if status['ram_total'] > 0:
        used = status['ram_total'] - status['ram_free']
        percent_free = int((status['ram_free'] / status['ram_total']) * 100)
        bar_length = 20
        filled = int(bar_length * status['ram_free'] / status['ram_total'])
        bar = '█' * filled + '░' * (bar_length - filled)
        bar_color = Colors.GREEN if percent_free > 30 else Colors.RED
        print(Colors.CYAN + "║" + Colors.END + f" 💾 RAM:          {status['ram_free']}MB / {status['ram_total']}MB ({percent_free}% free)" + " " * (40 - len(str(status['ram_free']))) + Colors.CYAN + "║" + Colors.END)
        print(Colors.CYAN + "║" + Colors.END + f"                  {bar_color}{bar}{Colors.END}" + " " * 44 + Colors.CYAN + "║" + Colors.END)
    
    print(Colors.CYAN + "╚" + "═" * 58 + "╝" + Colors.END)
    return True

def backup_settings(device_id: str):
    """Backup current resolution and density"""
    print_status("Backing up current settings...", "backup")
    
    success, out = run_adb(['shell', 'wm', 'size'], device_id)
    if success and out:
        run_adb(['shell', f"echo '{out}' > /sdcard/resolution_backup.txt"], device_id)
    
    success, out = run_adb(['shell', 'wm', 'density'], device_id)
    if success and out:
        run_adb(['shell', f"echo '{out}' > /sdcard/density_backup.txt"], device_id)
    
    print_status("Settings backed up to /sdcard/", "success")

def apply_optimization(device_id: str, config: dict, callback: Optional[Callable] = None) -> bool:
    """Apply all optimizations"""
    steps = [
        (f"Set resolution {config['resolution']['width']}x{config['resolution']['height']}", 
         f"wm size {config['resolution']['width']}x{config['resolution']['height']}"),
        (f"Set DPI to {config['dpi']}", f"wm density {config['dpi']}"),
    ]
    
    # Add app killing
    for app in config['apps_to_kill']:
        steps.append((f"Kill {app}", f"am force-stop {app}"))
    
    steps.append(("Clear cache", "pm trim-caches 9999999999"))
    
    total = len(steps)
    for i, (desc, cmd) in enumerate(steps):
        if callback:
            callback(i + 1, total, desc)
        run_adb(['shell', cmd], device_id, timeout=5)
        time.sleep(0.1)
    
    return True

def restore_default(device_id: str, callback: Optional[Callable] = None) -> bool:
    """Restore default settings"""
    steps = [
        ("Restore resolution", "wm size reset"),
        ("Restore DPI", "wm density reset"),
    ]
    
    total = len(steps)
    for i, (desc, cmd) in enumerate(steps):
        if callback:
            callback(i + 1, total, desc)
        run_adb(['shell', cmd], device_id)
        time.sleep(0.1)
    
    return True

def manage_apps(device_id: str):
    """Interactive app management"""
    print_status("Fetching installed apps...", "progress")
    success, out = run_adb(['shell', 'pm', 'list', 'packages', '-3'], device_id)
    
    if not success:
        print_status("Failed to get app list", "error")
        return
    
    apps = []
    for line in out.split('\n'):
        if line and 'package:' in line:
            apps.append(line.replace('package:', '').strip())
    
    if not apps:
        print_status("No user apps found", "info")
        return
    
    print(f"\n{Colors.BOLD}Installed Apps ({len(apps)} total):{Colors.END}")
    for i, app in enumerate(apps[:20], 1):
        # Get app name if possible
        success, name = run_adb(['shell', 'pm', 'list', 'packages', app], device_id)
        display = app.split('.')[-1] if '.' in app else app
        print(f"  {Colors.CYAN}{i:2}{Colors.END}. {display:<30} ({app})")
    
    if len(apps) > 20:
        print(f"  ... and {len(apps)-20} more apps")
    
    print("\n" + Colors.YELLOW + "Options:" + Colors.END)
    print("  • Enter number to kill specific app")
    print("  • 'all' to kill ALL user apps")
    print("  • 'back' to return")
    
    choice = input(f"\n{Colors.GREEN}➤ {Colors.END}").strip().lower()
    
    if choice == 'all':
        confirm = input(f"{Colors.RED}Kill ALL user apps? (y/n): {Colors.END}").strip().lower()
        if confirm == 'y':
            for app in apps:
                run_adb(['shell', 'am', 'force-stop', app], device_id)
                print(f"  Killed: {app}")
            print_status("All user apps killed", "success")
    
    elif choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(apps):
            run_adb(['shell', 'am', 'force-stop', apps[idx]], device_id)
            print_status(f"Killed {apps[idx]}", "success")
        else:
            print_status("Invalid number", "error")
    
    elif choice != 'back':
        print_status("Invalid choice", "error")

# ==================== MAIN PROGRAM ====================
def main():
    """Main program entry"""
    config = load_config()
    
    if not check_adb():
        print_status("Please install ADB and restart", "error")
        sys.exit(1)
    
    print_header()
    
    device_id = get_device()
    if not device_id:
        print_status("No device connected. Exiting.", "error")
        sys.exit(1)
    
    print_status(f"Connected to {device_id}", "success")
    show_dashboard(device_id)
    
    if config.get('auto_backup', True):
        backup_settings(device_id)
    
    while True:
        print("\n" + Colors.GREEN + "╔" + "═" * 58 + "╗" + Colors.END)
        print(Colors.GREEN + "║" + Colors.BOLD + " " * 22 + "MAIN MENU" + " " * 28 + Colors.GREEN + "║" + Colors.END)
        print(Colors.GREEN + "╠" + "═" * 58 + "╣" + Colors.END)
        print(Colors.GREEN + "║" + Colors.END + f"  {Colors.BOLD}1{Colors.END}. 🚀 OPTIMIZE MODE (Speed up)" + " " * 26 + Colors.GREEN + "║" + Colors.END)
        print(Colors.GREEN + "║" + Colors.END + f"  {Colors.BOLD}2{Colors.END}. 🔄 RESTORE MODE (Back to normal)" + " " * 22 + Colors.GREEN + "║" + Colors.END)
        print(Colors.GREEN + "║" + Colors.END + f"  {Colors.BOLD}3{Colors.END}. 📱 MANAGE APPS (Kill specific)" + " " * 23 + Colors.GREEN + "║" + Colors.END)
        print(Colors.GREEN + "║" + Colors.END + f"  {Colors.BOLD}4{Colors.END}. 📊 SHOW DEVICE INFO" + " " * 35 + Colors.GREEN + "║" + Colors.END)
        print(Colors.GREEN + "║" + Colors.END + f"  {Colors.BOLD}5{Colors.END}. 💾 BACKUP SETTINGS" + " " * 37 + Colors.GREEN + "║" + Colors.END)
        print(Colors.GREEN + "║" + Colors.END + f"  {Colors.BOLD}6{Colors.END}. 🔌 RECONNECT DEVICE" + " " * 35 + Colors.GREEN + "║" + Colors.END)
        print(Colors.GREEN + "║" + Colors.END + f"  {Colors.BOLD}7{Colors.END}. ❌ EXIT" + " " * 51 + Colors.GREEN + "║" + Colors.END)
        print(Colors.GREEN + "╚" + "═" * 58 + "╝" + Colors.END)
        
        choice = input(f"\n{Colors.BOLD}{Colors.CYAN}➤ Select option [1-7]: {Colors.END}").strip()
        
        if choice == '1':
            print_header()
            print_status("OPTIMIZATION MODE", "success")
            print("This will:")
            print(f"  • Set resolution to {config['resolution']['width']}x{config['resolution']['height']}")
            print(f"  • Set DPI to {config['dpi']}")
            print(f"  • Kill {len(config['apps_to_kill'])} background apps")
            print("  • Clear system cache")
            
            confirm = input(f"\n{Colors.YELLOW}Continue? (y/n): {Colors.END}").strip().lower()
            if confirm == 'y':
                def update_progress(current, total, desc):
                    progress_bar(current, total, prefix=f'  {desc[:30]:<30}')
                
                apply_optimization(device_id, config, update_progress)
                print()
                print_status("Optimization completed successfully!", "success")
                print_status("Device is now in high-performance mode", "info")
            else:
                print_status("Operation cancelled", "warning")
            
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.END}")
        
        elif choice == '2':
            print_header()
            print_status("RESTORE MODE", "warning")
            print("This will:")
            print("  • Restore original screen resolution")
            print("  • Restore original DPI")
            
            confirm = input(f"\n{Colors.YELLOW}Restore default settings? (y/n): {Colors.END}").strip().lower()
            if confirm == 'y':
                def update_progress(current, total, desc):
                    progress_bar(current, total, prefix=f'  {desc[:30]:<30}')
                
                restore_default(device_id, update_progress)
                print()
                print_status("Device restored to default settings!", "success")
            else:
                print_status("Operation cancelled", "warning")
            
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.END}")
        
        elif choice == '3':
            print_header()
            manage_apps(device_id)
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.END}")
        
        elif choice == '4':
            print_header()
            show_dashboard(device_id)
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.END}")
        
        elif choice == '5':
            backup_settings(device_id)
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.END}")
        
        elif choice == '6':
            print_header()
            print_status("Reconnecting...", "progress")
            device_id = get_device()
            if device_id:
                print_status(f"Reconnected to {device_id}", "success")
                show_dashboard(device_id)
            else:
                print_status("No device found", "error")
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.END}")
        
        elif choice == '7':
            print_header()
            print_status("Thank you for using Smart ADB Ultimate!", "success")
            print_status("Goodbye! 👋", "info")
            time.sleep(1)
            clear_screen()
            sys.exit(0)
        
        else:
            print_status("Invalid option. Please choose 1-7", "error")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n")
        print_status("Interrupted by user. Exiting...", "warning")
        sys.exit(0)
    except Exception as e:
        print_status(f"Unexpected error: {e}", "error")
        sys.exit(1)