# -*- coding: utf-8 -*-
"""
Test Test - Guvenlik izleme uygulamasi
Menu: Behavioral analysis, Integrity checks, Hardware telemetry, Honeypot, Server validation
"""
import sys
import os
import io

# Windows konsolunda Turkce karakter icin UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Proje koku
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main_menu():
    while True:
        print("\n" + "=" * 50)
        print("  TEST TEST - Guvenlik Izleme")
        print("=" * 50)
        print("  1) Davranış analizi (Behavioral analysis)")
        print("  2) Bütünlük kontrolü (Integrity checks)")
        print("  3) Donanım / sistem telemetrisi")
        print("  4) Honeypot (decoy + sahte port)")
        print("  5) Server-Side Validation")
        print("  0) Cikis")
        print("=" * 50)
        choice = input("Seçim: ").strip()

        if choice == "0":
            print("Cikis yapiliyor.")
            break
        if choice == "1":
            from behavioral_analysis import run_behavior_scan
            run_behavior_scan()
        elif choice == "2":
            from integrity_checks import run_integrity_scan, save_baseline, load_and_compare
            print("\n  a) Tarama yap")
            print("  b) Baseline kaydet")
            print("  c) Baseline ile karşılaştır")
            sub = input("Alt seçim: ").strip().lower()
            if sub == "a":
                run_integrity_scan()
            elif sub == "b":
                res = run_integrity_scan()
                save_baseline(res)
            elif sub == "c":
                changes = load_and_compare()
                if changes:
                    print("Değişen dosyalar:")
                    for c in changes:
                        print(f"  {c['path']}")
                else:
                    print("Değişiklik yok.")
            else:
                print("Gecersiz alt secim.")
        elif choice == "3":
            from hardware_telemetry import run_telemetry
            run_telemetry()
        elif choice == "4":
            from honeypot import run_honeypot_menu
            run_honeypot_menu()
        elif choice == "5":
            from server_validation import run_validation_flow
            run_validation_flow()
        else:
            print("Gecersiz secim.")


if __name__ == "__main__":
    main_menu()
