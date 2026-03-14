# -*- coding: utf-8 -*-
"""
Honeypot: decoy klasor/dosyalar, sahte port, watchdog ile dosya erisim loglama.
Erisimler tarih + tip + path (ve mumkunse process bilgisi) ile loglanir.
"""
import os
import socket
import time
from datetime import datetime

def ensure_honeypot_files():
    """Decoy klasor ve dosyalari olusturur (yoksa)."""
    from config import HONEYPOT_DIR, HONEYPOT_FILES
    os.makedirs(HONEYPOT_DIR, exist_ok=True)
    for name in HONEYPOT_FILES:
        path = os.path.join(HONEYPOT_DIR, name)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write("# Decoy file - do not use\n# Created: " + datetime.now().isoformat())
            print(f"  Decoy olusturuldu: {path}")
    print(f"Honeypot dizini: {HONEYPOT_DIR}")


def log_honeypot_event(kind, detail):
    """Honeypot olaylarini loglar (tarih | tip | detay)."""
    log_path = "honeypot_events.log"
    line = f"{datetime.now().isoformat()} | {kind} | {detail}\n"
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line)
        print(f"  [LOG] {kind}: {detail}")
    except OSError:
        pass


def watch_honeypot_dir():
    """Decoy olusturur; dosya izleme watchdog ile ayrica calistirilabilir."""
    ensure_honeypot_files()
    print("Decoy dosyalar hazir. (Dosya erisim izleme: 3 ile baslat.)")


def run_fake_listener(port=None, timeout_sec=30):
    """Sahte port dinleyici: baglananlari loglar."""
    from config import HONEYPOT_PORT
    port = port or HONEYPOT_PORT
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1.0)
    try:
        sock.bind(("0.0.0.0", port))
        sock.listen(5)
        print(f"\nHoneypot port {port} dinleniyor (~{timeout_sec}s veya Ctrl+C)...")
        end = time.time() + timeout_sec
        while time.time() < end:
            try:
                conn, addr = sock.accept()
                log_honeypot_event("PORT_CONNECT", f"remote={addr[0]}:{addr[1]} port={port}")
                conn.close()
            except socket.timeout:
                continue
            except Exception as e:
                log_honeypot_event("ERROR", str(e))
    except OSError as e:
        print(f"Port {port} acilamadi: {e}")
    finally:
        sock.close()


def run_honeypot_file_watcher(timeout_sec=60):
    """Watchdog ile honeypot dizininde dosya erisimini izler; her olayi loglar."""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print("watchdog yuklu degil: pip install watchdog")
        return
    from config import HONEYPOT_DIR
    ensure_honeypot_files()

    class Handler(FileSystemEventHandler):
        def on_any_event(self, event):
            path = getattr(event, "src_path", "") or getattr(event, "dest_path", "")
            log_honeypot_event("FILE_ACCESS", f"path={path} event={event.event_type}")

    observer = Observer()
    observer.schedule(Handler(), HONEYPOT_DIR, recursive=False)
    observer.start()
    print(f"Honeypot dosya izleme basladi ({timeout_sec}s). Dizine erisimler loglanacak.")
    try:
        time.sleep(timeout_sec)
    except KeyboardInterrupt:
        pass
    observer.stop()
    observer.join()


def run_honeypot_menu():
    """Honeypot alt menusu."""
    print("\n--- Honeypot ---")
    print("1) Decoy dosya/klasor olustur")
    print("2) Sahte port dinleyici (30 sn)")
    print("3) Dosya erisim izleme (watchdog, 60 sn)")
    print("0) Geri")
    choice = input("Secim: ").strip()
    if choice == "1":
        watch_honeypot_dir()
    elif choice == "2":
        run_fake_listener(timeout_sec=30)
    elif choice == "3":
        run_honeypot_file_watcher(timeout_sec=60)
    elif choice != "0":
        print("Gecersiz secim.")
