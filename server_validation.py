# -*- coding: utf-8 -*-
"""
Server-Side Validation: integrity + davranis raporu; offline cache ve zorunlu uyari.
"""
import os
import json
import requests
from datetime import datetime

def _cache_path():
    try:
        from config import VALIDATION_CACHE_FILE
        return VALIDATION_CACHE_FILE
    except Exception:
        return "validation_cache.json"

def _save_success():
    path = _cache_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"last_success": datetime.now().isoformat(), "ok": True}, f)
    except OSError:
        pass

def _load_cache():
    path = _cache_path()
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def send_integrity_report(entries, server_url=None):
    from config import VALIDATION_SERVER
    server_url = server_url or VALIDATION_SERVER
    payload = {
        "type": "integrity",
        "timestamp": datetime.now().isoformat(),
        "entries": [{"path": e["path"], "hash": e.get("hash"), "status": e["status"]} for e in entries],
    }
    try:
        r = requests.post(f"{server_url}/validate", json=payload, timeout=5)
        return r.status_code, r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text
    except requests.RequestException as e:
        return None, str(e)

def send_behavior_alerts(alerts, server_url=None):
    from config import VALIDATION_SERVER
    server_url = server_url or VALIDATION_SERVER
    payload = {
        "type": "behavior",
        "timestamp": datetime.now().isoformat(),
        "alerts": [
            {"type": a["type"], "match": a["match"], "pid": a["process"].get("pid"), "name": a["process"].get("name")}
            for a in alerts
        ],
    }
    try:
        r = requests.post(f"{server_url}/validate", json=payload, timeout=5)
        return r.status_code, r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text
    except requests.RequestException as e:
        return None, str(e)

def run_validation_flow(required=None):
    """Integrity + davranis topla, sunucuya gonder. required=True ise ulasilamazsa uyari."""
    from integrity_checks import run_integrity_scan
    from behavioral_analysis import analyze_behavior
    from config import VALIDATION_SERVER
    try:
        from config import VALIDATION_REQUIRED
    except ImportError:
        VALIDATION_REQUIRED = False
    required = required if required is not None else VALIDATION_REQUIRED

    print("\n--- Server-Side Validation ---")
    print("Integrity ve davranis verisi toplaniyor...")
    entries = run_integrity_scan()
    _, alerts = analyze_behavior()
    print(f"Sunucu: {VALIDATION_SERVER}")
    code, body = send_integrity_report(entries)
    if code is None:
        print(f"Baglanti hatasi: {body}")
        if required:
            print("[UYARI] Validation zorunlu; sunucu ulasilamiyor.")
        print("(Sunucu calismiyor olabilir; validation_server.py ile baslatin.)")
        return False
    _save_success()
    print(f"Integrity raporu gonderildi: HTTP {code}")
    if alerts:
        code2, body2 = send_behavior_alerts(alerts)
        print(f"Davranis uyarilari gonderildi: HTTP {code2}")
    else:
        print("Davranis uyarisi yok.")
    return True
