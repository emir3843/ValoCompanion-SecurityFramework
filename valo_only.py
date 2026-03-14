# -*- coding: utf-8 -*-
"""
Exe icin tek giris: Sadece Valo UI gorunur; integrity, davranis, validation arka planda sessizce calisir (guardian).
Konsol acilmaz; tum guvenlik ozellikleri Valo UI'yi korumak icin aktif.
"""
import sys
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))
if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)

sys.path.insert(0, APP_DIR)
os.chdir(APP_DIR)

# Config ve guardian icin APP_ROOT
try:
    import config
    config.APP_ROOT = APP_DIR
except Exception:
    pass

# Arka planda guardian baslat (integrity, davranis, validation periyodik)
try:
    from guardian import start_guardian
    start_guardian()
except Exception:
    pass

# Sadece Valo UI goster
from valo_ui import main
main()
