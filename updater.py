# -*- coding: utf-8 -*-
"""
Guncelleme: uzak version.txt ile karsilastirir; yeni surum varsa indirir ve updater_helper'i calistirir.
Sunucuda: UPDATE_BASE_URL/version.txt (tek satir: 1.0.1) ve UPDATE_BASE_URL/app.zip
"""
import os
import sys
import zipfile
import urllib.request
import subprocess
import tempfile

# Launcher'dan cagrildiginda APP_DIR launcher tarafindan ayarlanmis olabilir
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)


def get_local_version():
    try:
        import config
        return config.VERSION.strip()
    except Exception:
        return "0.0.0"


def parse_version(s):
    """1.0.1 -> (1,0,1) karsilastirma icin."""
    parts = []
    for x in (s or "0").strip().split("."):
        try:
            parts.append(int(x))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def get_remote_version(base_url):
    """version.txt icerigini dondurur."""
    url = base_url.rstrip("/") + "/version.txt"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SecureCompanion/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.read().decode("utf-8", errors="ignore").strip()
    except Exception as e:
        return None, str(e)


def download_file(url, dest_path):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SecureCompanion/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            with open(dest_path, "wb") as f:
                f.write(r.read())
        return True
    except Exception:
        return False


def check_and_update():
    """Guncelleme kontrolu; yeni surum varsa indirir ve updater_helper'i baslatir, sonra cikar."""
    import config
    global APP_DIR
    if getattr(config, "APP_ROOT", None):
        APP_DIR = config.APP_ROOT
    base_url = (config.UPDATE_BASE_URL or "").rstrip("/")
    if not base_url or "your-repo" in base_url:
        print("Guncelleme URL ayarlanmamis. config.py icinde UPDATE_BASE_URL guncelleyin.")
        return
    local = get_local_version()
    remote = get_remote_version(base_url)
    if isinstance(remote, tuple):
        print("Uzak surum alinamadi:", remote[1])
        return
    if parse_version(remote) <= parse_version(local):
        print("Zaten guncel: {} (uzak: {})".format(local, remote))
        return
    print("Yeni surum: {} -> {}. Indiriliyor...".format(local, remote))
    zip_url = base_url + "/app.zip"
    tmp = tempfile.gettempdir()
    zip_path = os.path.join(tmp, "secure_companion_update.zip")
    if not download_file(zip_url, zip_path):
        print("Indirme basarisiz:", zip_url)
        return
    pid = os.getpid()
    exe = sys.executable
    helper_exe = os.path.join(APP_DIR, "updater_helper.exe")
    helper_py = os.path.join(APP_DIR, "updater_helper.py")
    if os.path.isfile(helper_exe):
        helper_cmd = [helper_exe, APP_DIR, zip_path, str(pid), exe]
    elif os.path.isfile(helper_py):
        helper_cmd = [sys.executable, helper_py, APP_DIR, zip_path, str(pid), exe]
    else:
        print("updater_helper.exe / updater_helper.py bulunamadi.")
        return
    subprocess.Popen(helper_cmd, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
    print("Guncelleme baslatildi. Uygulama kapanacak ve yeniden acilacak.")
    sys.exit(0)


if __name__ == "__main__":
    check_and_update()
