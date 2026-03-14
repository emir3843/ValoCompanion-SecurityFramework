# Secure Companion – Güvenlik izleme + Companion UI

Tek giriş noktasından **güvenlik modülleri** (Test Test) ve **Companion UI** bir arada; kendi bütünlük kontrolü (self-integrity), güncelleme ve exe derleme desteklenir.

---

## Ne var?

- **Launcher** (`launcher.py`): Açılışta self-integrity, menü ile Test Test / Companion UI / Validation / Güncelleme.
- **Test Test**: Davranış analizi, bütünlük kontrolü, donanım telemetrisi, honeypot, server-side validation.
- **Companion UI**: Valorant tarzı menü (login, inject demo, on/off) – `game_memory_reader` klasöründe.
- **Self-integrity**: Uygulama kendi exe/.py dosyasının hash’ini baseline ile karşılaştırır.
- **Güncelleme**: Uzak `version.txt` ve `app.zip` ile otomatik güncelleme.
-**AI Kullanımı**: Projenin çoğu öğrenmek amacıyla yapılmış ve yapay zeka kullanılmıştır.

---

## Kurulum

```bash
cd test_test_security
pip install -r requirements.txt
```

---

## Çalıştırma

**Önerilen (birleşik menü):**

```bash
python launcher.py
```

- **1** – Test Test (güvenlik menüsü)
- **2** – Companion UI aç
- **3** – Server-Side Validation gönder
- **4** – Güncellemeyi kontrol et
- **5** – Self-integrity baseline kaydet
- **0** – Çıkış

Eski tek menü:

```bash
python main.py
```

Validation sunucusu (ayrı terminal):

```bash
python validation_server.py
```

---

## Exe’ye dönüştürme (PyInstaller)

### 1. PyInstaller kurulumu

```bash
pip install pyinstaller
```

### 2. Tek klasör (güncelleme için uygun)

```bash
cd test_test_security
python -m PyInstaller build_exe.spec
```

*Not: `pyinstaller` komutu taninmiyorsa `python -m PyInstaller` kullanin (PyInstaller yuklu olmali).*

Çıktı: **`dist/SecureCompanion/`** içinde `SecureCompanion.exe` ve kütüphane dosyaları.

### 3. Updater helper (güncelleme için)

Güncelleme akışı `updater_helper` ile çalışır. Exe kullanacaksanız onu da exe yapın:

```bash
python -m PyInstaller --onefile --name updater_helper updater_helper.py
```

Oluşan **`dist/updater_helper.exe`** dosyasını **`dist/SecureCompanion/`** klasörüne kopyalayın. Böylece güncelleme sırasında bu exe çalışır.

### 4. Tek exe (onefile, güncelleme yok)

Sadece tek .exe istiyorsanız:

```bash
python -m PyInstaller --onefile --name SecureCompanion launcher.py
```

Bu durumda “Güncellemeyi kontrol et” ile exe’nin kendisi güncellenemez; güncelleme için **onedir** (build_exe.spec) kullanın.

### 5. Sadece Valo UI exe (tek pencere, konsol yok)

Kullanici yalnizca Valorant menu penceresini gorur; guvenlik (integrity, davranis, validation) arka planda sessizce calisir.

```bash
cd test_test_security
python -m PyInstaller build_valo_only.spec
```

Cikti: **`dist/ValoCompanion/ValoCompanion.exe`**. Konsol acilmaz; guardian loglari ayni klasorde `guardian.log` dosyasina yazilir.

### 6. Çalıştırma

- **Klasör sürümü:** `dist/SecureCompanion/SecureCompanion.exe` veya `dist/ValoCompanion/ValoCompanion.exe` calistirin.
- Bu klasoru kullaniciya tasiyabilir veya kurulum dizini olarak kullanabilirsiniz.

---

## Sürekli güncelleme (kendini güncelleme)

Uygulama, `config.py` içindeki **`UPDATE_BASE_URL`** adresine göre güncelleme arar.

### Sunucuda olması gerekenler

1. **version.txt**  
   Tek satır, sürüm numarası (örn. `1.0.1`).

2. **app.zip**  
   Güncel sürümün **tüm dosyaları** (exe + kütüphaneler).  
   Örnek: `dist/SecureCompanion/` içeriğini zip’leyin (içinde doğrudan exe ve dosyalar olsun, üst klasör adı olmasın):

   ```bash
   cd dist/SecureCompanion
   # Windows: Explorer ile tum dosyalari secip sag tik -> Sıkıştırılmış klasör
   # veya PowerShell: Compress-Archive -Path * -DestinationPath ..\app.zip
   ```

Bu iki dosyayı `UPDATE_BASE_URL` ile erişilebilir yere koyun (örn. web sunucu veya GitHub Releases / raw).

### config.py ayarı

```python
VERSION = "1.0.0"
UPDATE_BASE_URL = "https://your-server.com/releases"
```

`VERSION`’ı her yeni sürümde artırın (örn. `1.0.1`). Sunucudaki `version.txt` de aynı değeri içermeli.

### Akış

1. Kullanıcı menüden **“4) Güncellemeyi kontrol et”** seçer.
2. Uygulama `UPDATE_BASE_URL/version.txt` indirir; sayı mevcut `VERSION`’dan büyükse güncelleme var demektir.
3. `UPDATE_BASE_URL/app.zip` indirilir.
4. `updater_helper.exe` (veya `updater_helper.py`) çalıştırılır; ana uygulama kapanır.
5. Helper, zip’i `SecureCompanion` klasörüne açar (üzerine yazar), sonra `SecureCompanion.exe`’yi tekrar başlatır.

Böylece her güncellemede sürüm ve veriler (config, baseline vb.) güncel kalır; uygulama kendini bu URL’den güncelleyebilir.

---

## Yapılandırma (config.py)

- **VERSION**, **UPDATE_BASE_URL**: Güncelleme için.
- **INTEGRITY_PATHS**: Bütünlük kontrolü yapılacak kritik dosyalar.
- **HONEYPOT_***: Honeypot klasörü, decoy dosyalar, port.
- **VALIDATION_SERVER**: Validation API adresi.

---

## Güvenlik notları

- Kernel seviyesi izleme için imzalı sürücü gerekir; uygulama user-mode’da çalışır.
- Self-integrity: İlk kurulumda menüden **“5) Self-integrity baseline kaydet”** ile baseline oluşturun; sonraki açılışlarda exe/dosya değişirse uyarı verilir.
- Güncelleme zip’ini güvenilir bir sunucudan sunun; mümkünse HTTPS kullanın.
