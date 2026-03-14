# -*- coding: utf-8 -*-
"""
Guncelleme yardimcisi: ana uygulama kapandiktan sonra calisir.
Argumanlar: app_dir, zip_path, pid_beklenecek, exe_yolu_tekrar_baslat
"""
import os
import sys
import zipfile
import time
import subprocess

def main():
    if len(sys.argv) < 5:
        print("Kullanim: updater_helper.py <app_dir> <zip_path> <pid> <exe_yolu>")
        return
    app_dir = sys.argv[1]
    zip_path = sys.argv[2]
    try:
        pid = int(sys.argv[3])
    except ValueError:
        pid = 0
    exe_path = sys.argv[4]
    if not os.path.isdir(app_dir):
        print("App dizini yok:", app_dir)
        return
    if not os.path.isfile(zip_path):
        print("Zip dosyasi yok:", zip_path)
        return
    # Pid'in kapanmasini bekle (en fazla 15 sn)
    for _ in range(30):
        try:
            os.kill(pid, 0)
        except (OSError, ProcessLookupError):
            break
        time.sleep(0.5)
    time.sleep(0.5)
    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            names = z.namelist()
            # Tek ust klasor varsa (ornegin "SecureCompanion/config.py") cikar
            prefix = None
            if names:
                first = names[0].replace("\\", "/")
                if "/" in first and all(n.replace("\\", "/").startswith(first.split("/")[0] + "/") for n in names if "/" in n):
                    prefix = first.split("/")[0] + "/"
            for raw_name in names:
                if raw_name.startswith("__") or "/__" in raw_name:
                    continue
                name = raw_name[len(prefix):] if (prefix and raw_name.startswith(prefix)) else raw_name
                name = name.replace("\\", "/")
                if not name or name == "/":
                    continue
                dest = os.path.join(app_dir, name)
                if name.endswith("/"):
                    os.makedirs(dest, exist_ok=True)
                else:
                    parent = os.path.dirname(dest)
                    if parent:
                        os.makedirs(parent, exist_ok=True)
                    with z.open(raw_name) as src:
                        with open(dest, "wb") as out:
                            out.write(src.read())
    except Exception as e:
        print("Zip acilamadi:", e)
        return
    try:
        os.remove(zip_path)
    except Exception:
        pass
    # Uygulamayi tekrar baslat
    if os.path.isfile(exe_path):
        subprocess.Popen([exe_path], cwd=app_dir)
    print("Guncelleme tamamlandi, uygulama yeniden baslatildi.")


if __name__ == "__main__":
    main()
