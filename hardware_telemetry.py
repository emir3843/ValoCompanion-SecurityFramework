# -*- coding: utf-8 -*-
"""
Sistem / donanım telemetrisi: CPU, bellek, disk, process sayısı, ağ, USB (WMI ile).
Kernel seviyesi değil ama donanım ve sistem bilgisi için işe yarar.
"""
import platform
import psutil

def get_cpu_info():
    """CPU kullanımı ve temel bilgi."""
    return {
        "percent": psutil.cpu_percent(interval=1),
        "count": psutil.cpu_count(),
        "freq_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else None,
    }


def get_memory_info():
    """Bellek kullanımı."""
    v = psutil.virtual_memory()
    return {
        "total_gb": round(v.total / (1024**3), 2),
        "used_gb": round(v.used / (1024**3), 2),
        "percent": v.percent,
    }


def get_disk_info():
    """Disk bölümleri ve kullanım."""
    result = []
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            result.append({
                "device": part.device,
                "mountpoint": part.mountpoint,
                "total_gb": round(usage.total / (1024**3), 2),
                "used_percent": usage.percent,
            })
        except (PermissionError, OSError):
            continue
    return result


def get_usb_devices():
    """WMI ile USB cihazları (Windows)."""
    try:
        import wmi
        c = wmi.WMI()
        devices = []
        for usb in c.Win32_USBControllerDevice():
            try:
                dev = c.Win32_PnPEntity(DeviceID=usb.Dependent.DeviceID)[0]
                devices.append({"name": dev.Caption, "device_id": dev.DeviceID})
            except (IndexError, AttributeError):
                continue
        return devices[:30]  # İlk 30
    except Exception as e:
        return [{"error": str(e)}]


def get_network_connections():
    """Aktif ağ bağlantıları (kısa özet)."""
    conns = []
    for c in psutil.net_connections(kind="inet"):
        if c.status == "ESTABLISHED" and c.raddr:
            conns.append({
                "laddr": f"{c.laddr.ip}:{c.laddr.port}",
                "raddr": f"{c.raddr.ip}:{c.raddr.port}",
                "pid": c.pid,
            })
    return conns[:20]


def run_telemetry():
    """Tüm telemetriyi toplar ve yazdırır."""
    print("\n--- Donanım / Sistem Telemetrisi ---")
    print(f"Sistem: {platform.system()} {platform.release()}")
    cpu = get_cpu_info()
    print(f"CPU: {cpu['count']} çekirdek, kullanım %{cpu['percent']}, frekans: {cpu['freq_mhz']} MHz")
    mem = get_memory_info()
    print(f"Bellek: {mem['used_gb']} / {mem['total_gb']} GB (%{mem['percent']})")
    print("Disk:")
    for d in get_disk_info():
        print(f"  {d['mountpoint']}: %{d['used_percent']} kullanım")
    print("USB cihazları (WMI):")
    for u in get_usb_devices():
        if "error" in u:
            print(f"  WMI hatası: {u['error']}")
            break
        print(f"  - {u.get('name', '?')}")
    print("Aktif bağlantılar (ilk 10):")
    for c in get_network_connections()[:10]:
        print(f"  {c['laddr']} -> {c['raddr']} (PID {c['pid']})")
    return {
        "cpu": cpu,
        "memory": mem,
        "disk": get_disk_info(),
        "usb": get_usb_devices(),
        "connections": get_network_connections(),
    }
