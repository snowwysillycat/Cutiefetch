import os, platform, psutil, socket, yaml, subprocess

try:
    from ASCII import get_logo, COLORS
except ImportError:
    COLORS = {'dark_pink': '\033[38;5;197m', 'white': '\033[97m', 'gray': '\033[90m', 'reset': '\033[0m', 'bold': '\033[1m'}
    def get_logo(n): return [" [!] Logo Missing "]

def run(cmd):
    try: return subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode().strip()
    except: return "None"

def parse(text):
    cmap = {'&p': COLORS['dark_pink'], '&w': COLORS['white'], '&gray': COLORS['gray'], '&0': COLORS['reset'], '&L': COLORS['bold']}
    for code, value in cmap.items(): text = text.replace(code, value)
    return text

def get_data():
    mem = psutil.virtual_memory()
    batt = psutil.sensors_battery()
    
    pkgs = []
    if os.path.exists("/usr/bin/pacman"): pkgs.append(f"{run('pacman -Qq | wc -l')} (pacman)")
    if os.path.exists("/usr/bin/dnf"): pkgs.append(f"{run('rpm -qa | wc -l')} (rpm)")
    if os.path.exists("/usr/bin/flatpak"): pkgs.append(f"{run('flatpak list | wc -l')} (flatpak)")

    gpu_raw = run("lspci | grep -i 'vga\\|3d' | cut -d: -f3")
    gpus = [g.strip() for g in gpu_raw.split('\n') if g.strip()]

    return {
        "os": run("grep '^NAME=' /etc/os-release | cut -d'=' -f2 | tr -d '\"'") or "Linux",
        "host": run("cat /sys/class/dmi/id/product_name 2>/dev/null") or "PC",
        "kernel": platform.release(),
        "uptime": run("uptime -p | sed 's/up //'"),
        "pkgs": " • ".join(pkgs) if pkgs else "None",
        "shell": os.environ.get("SHELL", "bash").split("/")[-1],
        "cpu": run("grep -m1 'model name' /proc/cpuinfo | cut -d: -f2").strip() or "CPU",
        "gpu": gpus[0] if gpus else "None",
        "mem": f"{mem.used/(1024**3):.2f} / {mem.total/(1024**3):.2f} GiB",
        "batt": f"{batt.percent}% [{'AC' if batt.power_plugged else 'Bat'}]" if batt else "Desktop"
    }

def display():
    # Try to load config.yml or use defaults
    try:
        with open('config.yml', 'r') as f: cfg = yaml.safe_load(f)
    except:
        cfg = {'colors': {'primary_label': '&p', 'primary_info': '&w'}, 'modules': [
            {'id': 'os', 'label': 'OS'}, {'id': 'host', 'label': 'Host'}, {'id': 'kernel', 'label': 'Kernel'},
            {'id': 'uptime', 'label': 'Uptime'}, {'id': 'pkgs', 'label': 'Packages'}, {'id': 'shell', 'label': 'Shell'},
            {'id': 'cpu', 'label': 'CPU'}, {'id': 'gpu', 'label': 'GPU'}, {'id': 'mem', 'label': 'Memory'}, {'id': 'batt', 'label': 'Power'}
        ]}

    stats = get_data()
    logo = get_logo("custom")
    l_col = cfg['colors'].get('primary_label', '&p')
    i_col = cfg['colors'].get('primary_info', '&w')

    user_host = f"{os.getlogin()}@{socket.gethostname()}"
    lines = [
        parse(f"{l_col}&L{user_host}&0"),
        parse(f"&gray{'-' * len(user_host)}&0"),
        ""
    ]

    for mod in cfg.get('modules', []):
        lines.append(f"{parse(l_col + mod['label'] + '&0')}: {parse(i_col + str(stats.get(mod['id'], 'N/A')) + '&0')}")

    # Color bar at the bottom
    lines.append("")
    lines.append("".join([f"\033[48;5;{c}m  " for c in [213, 219, 117, 159, 141, 255]]) + "\033[0m")

    # Display Side-by-Side
    max_h = max(len(logo), len(lines))
    for i in range(max_h):
        l_part = parse(f"{l_col}{logo[i]}") if i < len(logo) else " " * len(logo[0])
        r_part = lines[i] if i < len(lines) else ""
        # Adding extra spacing for the large block logo
        print(f"  {l_part}   {r_part}")

if __name__ == "__main__":
    display()