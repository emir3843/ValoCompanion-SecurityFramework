# -*- coding: utf-8 -*-
"""
Bütünlük kontrolleri: kritik dosyaların hash'leri, değişiklik tespiti.
Memory "integrity" yerine dosya tabanlı integrity (pratik ve işe yarar).
"""
import os
import hashlib
from datetime import datetime

def file_hash(path, algo="sha256"):
    """Dosyanın hash'ini hesaplar."""
    if not os.path.isfile(path):
        return None
    h = hashlib.new(algo)
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except (PermissionError, OSError):
        return None


def run_integrity_scan(paths=None):
    """Verilen dosya listesi icin hash hesaplar; degisiklik icin baseline ile karsilastirilabilir."""
    import config as _cfg
    paths = paths or (_cfg.INTEGRITY_PATHS + list(getattr(_cfg, "INTEGRITY_PATHS_EXTRA", [])))
    print("\n--- Bütünlük Kontrolü (Integrity Check) ---")
    results = []
    for path in paths:
        if not os.path.exists(path):
            results.append({"path": path, "status": "not_found", "hash": None})
            print(f"  [YOK] {path}")
            continue
        if os.path.isdir(path):
            results.append({"path": path, "status": "is_dir", "hash": None})
            print(f"  [DIR] {path} (atlanıyor)")
            continue
        h = file_hash(path)
        if h is None:
            results.append({"path": path, "status": "access_denied", "hash": None})
            print(f"  [ERİŞİM RED] {path}")
        else:
            results.append({"path": path, "status": "ok", "hash": h})
            print(f"  [OK] {path}")
            print(f"       SHA256: {h}")
    return results


def save_baseline(results, filepath="baseline_integrity.json"):
    """Mevcut hash'leri baseline olarak kaydeder."""
    import json
    data = {
        "created": datetime.now().isoformat(),
        "entries": [{"path": r["path"], "hash": r["hash"], "status": r["status"]} for r in results]
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Baseline kaydedildi: {filepath}")


def load_and_compare(baseline_path="baseline_integrity.json"):
    """Baseline ile şimdiki hash'leri karşılaştırır."""
    import json
    if not os.path.isfile(baseline_path):
        print("Baseline dosyası yok. Önce integrity scan yapıp baseline kaydedin.")
        return []
    with open(baseline_path, encoding="utf-8") as f:
        data = json.load(f)
    changes = []
    for entry in data.get("entries", []):
        path, old_hash = entry.get("path"), entry.get("hash")
        if not path or old_hash is None:
            continue
        current = file_hash(path)
        if current is not None and current != old_hash:
            changes.append({"path": path, "old": old_hash, "new": current})
    return changes
