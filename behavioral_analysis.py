# -*- coding: utf-8 -*-
"""
Davranis analizi: process, ag, cmdline kurallari, anomali tespiti.
Genisletilmis kurallar ve ag sinyalleri ile sinirlari azaltan katman.
"""
import os
import sys
import re
import psutil
from datetime import datetime

# Suspheli isim/cmdline kurallari (genisletilmis)
SUSPICIOUS_NAMES = {
    "mimikatz", "procdump", "pwdump", "psexec", "cachedump", "wce",
    "nmap", "netcat", "nc.exe", "ncat", "keylogger", "hook", "inject",
}
SUSPICIOUS_CMDLINE = {
    "-e ", "invoke-mimikatz", "sekurlsa", "lsass", "dump",
    "-enc ", "-encodedcommand", "invoke-expression", "iex ",
    "bypass", "-executionpolicy", "hidden", "windowstyle hidden",
    "add-type", "reflection", "virtualalloc", "createthread",
    "openprocess", "readprocessmemory", "writeprocessmemory",
}
# Base64 benzeri uzun blok (obfuscated script)
B64_PATTERN = re.compile(r"[A-Za-z0-9+/]{50,}={0,2}")


def get_process_tree():
    """Tum process'leri parent-child ile listeler."""
    result = []
    for p in psutil.process_iter(["pid", "name", "ppid", "create_time", "cmdline"]):
        try:
            pinfo = p.info.copy()
            cmd = " ".join(pinfo.get("cmdline") or [])[:300]
            pinfo["cmdline"] = cmd
            result.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return result


def get_connection_counts_by_pid():
    """PID basina ESTABLISHED baglanti sayisi (ag anomali icin)."""
    try:
        conns = psutil.net_connections(kind="inet")
        by_pid = {}
        for c in conns:
            if c.status == "ESTABLISHED" and c.pid:
                by_pid[c.pid] = by_pid.get(c.pid, 0) + 1
        return by_pid
    except (psutil.AccessDenied, psutil.Error):
        return {}


def analyze_behavior():
    """Process + ag sinyalleri ile genisletilmis analiz."""
    tree = get_process_tree()
    conn_counts = get_connection_counts_by_pid()
    alerts = []

    for p in tree:
        name = (p.get("name") or "").lower()
        cmd = (p.get("cmdline") or "").lower()
        pid = p.get("pid")

        for bad in SUSPICIOUS_NAMES:
            if bad in name or bad in cmd:
                alerts.append({"type": "suspicious_name", "process": p, "match": bad})
        for bad in SUSPICIOUS_CMDLINE:
            if bad in cmd:
                alerts.append({"type": "suspicious_cmdline", "process": p, "match": bad})
        if B64_PATTERN.search(cmd) and len(cmd) > 100:
            alerts.append({"type": "obfuscated_cmdline", "process": p, "match": "long_encoded_block"})

        # Ag anomali: bir process cok fazla baglanti
        if pid and conn_counts.get(pid, 0) > 25:
            alerts.append({"type": "network_anomaly", "process": p, "match": f"conn_count={conn_counts[pid]}"})

    return tree, alerts


def run_behavior_scan():
    """Tek seferlik davranis taramasi."""
    print("\n--- Davranis Analizi (Genisletilmis) ---")
    print("Process ve ag sinyalleri taranıyor...")
    tree, alerts = analyze_behavior()
    print(f"Toplam process: {len(tree)}")
    if alerts:
        print(f"\n[UYARI] {len(alerts)} süpheli davranis tespit edildi:")
        for a in alerts:
            p = a["process"]
            print(f"  - {a['type']}: PID={p['pid']} {p['name']} | {a['match']}")
    else:
        print("Süpheli process tespit edilmedi.")
    print("\nIlk 15 process:")
    for p in sorted(tree, key=lambda x: x.get("create_time") or 0)[:15]:
        print(f"  PID {p['pid']:6} PPID {p['ppid']:6} {p['name']}")
    return tree, alerts
