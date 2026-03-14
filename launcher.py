# -*- coding: utf-8 -*-
"""
Birlesik giris noktasi: self-integrity, guvenlik menu, Companion UI, validation, guncelleme.
Exe olarak calistirildiginda veya python launcher.py ile acilir.
"""
import sys
import os
import io
import subprocess

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)

# Exe (PyInstaller) ile calisirken uygulama dizini
if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)


def get_app_dir():
    return APP_DIR


def run_self_integrity():
    """Uygulama kendi dosyalarinin hash'lerini kontrol eder (baseline varsa)."""
    from integrity_checks import file_hash
    import glob
    import json
    baseline_path = os.path.join(APP_DIR, "baseline_self.json")
    if not os.path.isfile(baseline_path):
        return True, "Baseline yok; ilk calistirma. Menu'den '5) Self-integrity baseline kaydet' ile kaydedin."
    paths = []
    if getattr(sys, "frozen", False):
        paths = [sys.executable]
    else:
        for ext in ("*.py", "*.json"):
            for f in glob.glob(os.path.join(APP_DIR, ext)):
                if os.path.isfile(f) and "baseline" not in os.path.basename(f).lower():
                    paths.append(f)
    if not paths:
        return True, "Kontrol edilecek dosya yok."
    import json
    try:
        with open(baseline_path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return True, "Baseline okunamadi."
    entries = {}
    for e in data.get("entries", []):
        p = e.get("path")
        if p:
            entries[os.path.normpath(p)] = e.get("hash")
    changes = []
    for path in paths:
        norm = os.path.normpath(path)
        old = entries.get(norm)
        cur = file_hash(path)
        if cur is not None and old is not None and cur != old:
            changes.append(path)
    if changes:
        return False, f"Degisiklik tespit edildi: {len(changes)} dosya"
    return True, "Kendi dosyalariniz degismedi (OK)"


def save_self_baseline():
    """Uygulama dizinindeki kritik dosyalar icin baseline kaydeder (exe veya .py)."""
    from integrity_checks import file_hash, save_baseline
    import glob
    paths = []
    if getattr(sys, "frozen", False):
        paths = [sys.executable]
    else:
        for ext in ("*.py", "*.json"):
            for f in glob.glob(os.path.join(APP_DIR, ext)):
                if os.path.isfile(f) and "baseline" not in os.path.basename(f).lower():
                    paths.append(f)
    results = []
    for path in paths:
        h = file_hash(path)
        results.append({"path": os.path.normpath(path), "status": "ok" if h else "access_denied", "hash": h})
    save_baseline(results, os.path.join(APP_DIR, "baseline_self.json"))


def launch_companion_ui():
    """Game Companion (Valorant menu) UI'i acar."""
    ui_path = os.path.join(os.path.dirname(APP_DIR), "game_memory_reader", "ui_app.py")
    if not os.path.isfile(ui_path):
        ui_path = os.path.join(APP_DIR, "game_memory_reader", "ui_app.py")
    if not os.path.isfile(ui_path):
        print("Companion UI bulunamadi:", ui_path)
        return
    subprocess.Popen([sys.executable, ui_path], cwd=os.path.dirname(ui_path))
    print("Companion UI acildi.")


def main_menu():
    import config
    config.APP_ROOT = APP_DIR
    VERSION = config.VERSION
    # Istege bagli: her acilista guncelleme kontrolu (yeni surum varsa indirir ve cikar)
    if getattr(config, "CHECK_UPDATE_AT_STARTUP", False):
        try:
            from updater import check_and_update
            check_and_update()
        except Exception:
            pass
    # Baslangicta kisa self-integrity (baseline varsa)
    ok, msg = run_self_integrity()
    if not ok:
        print("\n[UYARI] " + msg)
    else:
        print("\n[OK] " + msg)

    while True:
        print("\n" + "=" * 54)
        print("  SECURE COMPANION  (v{}) - Guvenlik + Companion".format(VERSION))
        print("=" * 54)
        print("  1) Test Test - Guvenlik izleme (davranis, integrity, honeypot, vb.)")
        print("  2) Companion UI ac (Valorant menu)")
        print("  3) Server-Side Validation gonder")
        print("  4) Guncellemeyi kontrol et")
        print("  5) Self-integrity baseline kaydet (mevcut dosyalar)")
        print("  0) Cikis")
        print("=" * 54)
        choice = input("Secim: ").strip()

        if choice == "0":
            print("Cikis yapiliyor.")
            break
        if choice == "1":
            from main import main_menu as security_menu
            security_menu()
        elif choice == "2":
            launch_companion_ui()
        elif choice == "3":
            from server_validation import run_validation_flow
            run_validation_flow()
        elif choice == "4":
            from updater import check_and_update
            check_and_update()
        elif choice == "5":
            save_self_baseline()
            print("Self-integrity baseline kaydedildi.")
        else:
            print("Gecersiz secim.")


if __name__ == "__main__":
    main_menu()
