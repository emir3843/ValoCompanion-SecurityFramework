# -*- coding: utf-8 -*-
"""
Valo UI'yi korumak icin arka planda calisan guardian.
Integrity, davranis analizi, validation periyodik ve sessizce calisir; sadece log dosyasina yazar.
"""
import os
import sys
import time
import threading

APP_DIR = os.path.dirname(os.path.abspath(__file__))
if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)

LOG_FILE = os.path.join(APP_DIR, "guardian.log")
INTERVAL_INTEGRITY = 300   # 5 dk
INTERVAL_BEHAVIOR = 180   # 3 dk
INTERVAL_VALIDATION = 600 # 10 dk


def _log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {msg}\n")
    except OSError:
        pass


def _run_integrity():
    try:
        import config
        config.APP_ROOT = APP_DIR
        import json
        import glob
        from integrity_checks import file_hash
        baseline = os.path.join(APP_DIR, "baseline_self.json")
        if not os.path.isfile(baseline):
            return
        with open(baseline, encoding="utf-8") as f:
            data = json.load(f)
        entries = {os.path.normpath(e["path"]): e.get("hash") for e in data.get("entries", []) if e.get("path")}
        paths = [sys.executable] if getattr(sys, "frozen", False) else []
        if not paths:
            for ext in ("*.py", "*.json"):
                for f in glob.glob(os.path.join(APP_DIR, ext)):
                    if os.path.isfile(f) and "baseline" not in os.path.basename(f).lower():
                        paths.append(f)
        for path in paths:
            norm = os.path.normpath(path)
            old = entries.get(norm)
            cur = file_hash(path)
            if cur is not None and old is not None and cur != old:
                _log(f"INTEGRITY: degisiklik tespit edildi: {path}")
                return
    except Exception as e:
        _log(f"INTEGRITY error: {e}")


def _run_behavior():
    try:
        import config
        config.APP_ROOT = APP_DIR
        from behavioral_analysis import analyze_behavior
        tree, alerts = analyze_behavior()
        if alerts:
            _log(f"BEHAVIOR: {len(alerts)} uyari - {[a.get('type') for a in alerts[:5]]}")
    except Exception as e:
        _log(f"BEHAVIOR error: {e}")


def _run_validation():
    try:
        import config
        config.APP_ROOT = APP_DIR
        from server_validation import run_validation_flow
        if run_validation_flow(required=False):
            _log("VALIDATION: rapor gonderildi")
    except Exception as e:
        _log(f"VALIDATION error: {e}")


def guardian_loop(stop_event):
    t0 = time.time()
    last_integrity = last_behavior = last_validation = 0
    while not stop_event.is_set():
        try:
            now = time.time()
            if now - last_integrity >= INTERVAL_INTEGRITY:
                _run_integrity()
                last_integrity = now
            if now - last_behavior >= INTERVAL_BEHAVIOR:
                _run_behavior()
                last_behavior = now
            if now - last_validation >= INTERVAL_VALIDATION:
                _run_validation()
                last_validation = now
        except Exception:
            pass
        stop_event.wait(30)


def start_guardian():
    stop = threading.Event()
    t = threading.Thread(target=guardian_loop, args=(stop,), daemon=True)
    t.start()
    return stop
