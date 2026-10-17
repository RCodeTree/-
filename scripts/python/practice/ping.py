import subprocess, sys

def ping_ok(host, count=1):
    cmd = ["ping", "-n" if sys.platform == "win32" else "-c", str(count), host]
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=5)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False

def main():
    for h in ["127.0.0.1", "10.255.255.1"]:  # 第二个故意不通 10.255.255.1 是私网地址
        print(f"{h}: {'可达' if ping_ok(h) else '不可达'}")
    pass

if __name__ == "__main__":
    main()

