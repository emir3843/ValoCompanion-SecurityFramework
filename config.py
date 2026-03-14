# --- Uygulama ve guncelleme ---
import os
VERSION = "1.0.0"
# Guncelleme: sunucuda version.txt (tek satir: 1.0.1) ve app.zip olmali
UPDATE_BASE_URL = "https://raw.githubusercontent.com/your-repo/secure-companion/main/releases"
# Uygulama kok dizini (launcher tarafindan ayarlanabilir; exe iken sys.executable dir)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# Kritik izlenecek yollar (okunabilir dosyalar) - genis kapsam
INTEGRITY_PATHS = [
    "C:\\Windows\\System32\\drivers\\etc\\hosts",
]
# Ek yollar (varsa; erisim red olursa atlanir)
INTEGRITY_PATHS_EXTRA = [
    os.path.expandvars("%APPDATA%\\..\\Local\\hosts"),
    os.path.join(os.path.expanduser("~"), ".ssh", "config") if os.path.exists(os.path.join(os.path.expanduser("~"), ".ssh")) else None,
]
INTEGRITY_PATHS_EXTRA = [p for p in INTEGRITY_PATHS_EXTRA if p]

# Honeypot decoy dosya/klasör (kullanıcı dizininde)
HONEYPOT_DIR = "C:\\Users\\emoca\\Documents\\confidential_backup"
HONEYPOT_FILES = ["passwords.txt", "credentials.xlsx", "vpn_config.ini"]
HONEYPOT_PORT = 4444  # Dinlenecek sahte port

# Validation server (localhost ornek)
VALIDATION_SERVER = "http://127.0.0.1:5000"
# True ise sunucu ulasilamazsa uyari verilir
VALIDATION_REQUIRED = False
VALIDATION_CACHE_FILE = "validation_cache.json"
# True ise launcher her acilista guncelleme kontrolu yapar; yeni surum varsa indirir ve yeniden baslar
CHECK_UPDATE_AT_STARTUP = True
