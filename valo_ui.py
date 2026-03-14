# -*- coding: utf-8 -*-
# Valo UI - Exe'de tek gorunen pencere. Guardian arka planda calisir.
import sys
import os
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import customtkinter as ctk
from tkinter import messagebox

COLORS = {
    "bg_dark": "#0F0F0F", "bg_card": "#1A1A1A", "bg_input": "#252525",
    "accent": "#FF4655", "accent_dim": "#CC3947", "accent_glow": "#FF6B78",
    "text": "#FFFFFF", "text_dim": "#A0A0A0", "success": "#00E676",
    "error": "#FF5252", "border": "#2D2D2D",
}
APP_WIDTH, APP_HEIGHT, FONT_FAMILY = 420, 620, "Segoe UI"


class ValorantMenuUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("")
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_dark"])
        self.after(10, self._center)
        self.logged_in = False
        self.injected = False
        self.toggles = {}
        self.toggle_state = {}
        self._build_ui()

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - APP_WIDTH) // 2
        y = (self.winfo_screenheight() - APP_HEIGHT) // 2
        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent", height=80)
        header.pack(fill="x", padx=24, pady=(28, 20))
        header.pack_propagate(False)
        title_row = ctk.CTkFrame(header, fg_color="transparent")
        title_row.pack(anchor="w")
        ctk.CTkLabel(title_row, text="VALORANT", font=ctk.CTkFont(family=FONT_FAMILY, size=30, weight="bold"), text_color=COLORS["text"]).pack(side="left")
        self.status_dot = ctk.CTkFrame(title_row, width=10, height=10, fg_color=COLORS["text_dim"], corner_radius=5)
        self.status_dot.pack(side="left", padx=(14, 0), pady=(10, 0))
        ctk.CTkLabel(header, text="Companion · Valorant uyumlu", font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=COLORS["text_dim"]).pack(anchor="w")
        ctk.CTkFrame(header, height=2, fg_color=COLORS["accent"], corner_radius=1).pack(fill="x", pady=(10, 0))

        login_card = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"], height=140)
        login_card.pack(fill="x", padx=24, pady=(0, 12))
        login_card.pack_propagate(False)
        li = ctk.CTkFrame(login_card, fg_color="transparent")
        li.pack(fill="both", expand=True, padx=20, pady=16)
        ctk.CTkLabel(li, text="Giris", font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"), text_color=COLORS["text_dim"]).pack(anchor="w")
        self.entry_id = ctk.CTkEntry(li, placeholder_text="Kullanici adi / ID", height=40, fg_color=COLORS["bg_input"], border_color=COLORS["border"], text_color=COLORS["text"], font=ctk.CTkFont(family=FONT_FAMILY, size=13))
        self.entry_id.pack(fill="x", pady=(8, 6))
        self.entry_pw = ctk.CTkEntry(li, placeholder_text="Sifre", height=40, show="•", fg_color=COLORS["bg_input"], border_color=COLORS["border"], text_color=COLORS["text"], font=ctk.CTkFont(family=FONT_FAMILY, size=13))
        self.entry_pw.pack(fill="x", pady=(0, 10))
        ctk.CTkButton(li, text="Giris yap", height=38, fg_color=COLORS["accent"], hover_color=COLORS["accent_glow"], text_color=COLORS["text"], font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"), command=self._on_login).pack(fill="x")

        inject_card = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"], height=120)
        inject_card.pack(fill="x", padx=24, pady=(0, 12))
        inject_card.pack_propagate(False)
        ii = ctk.CTkFrame(inject_card, fg_color="transparent")
        ii.pack(fill="both", expand=True, padx=20, pady=16)
        r = ctk.CTkFrame(ii, fg_color="transparent")
        r.pack(fill="x")
        ctk.CTkLabel(r, text="Inject", font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"), text_color=COLORS["text_dim"]).pack(side="left")
        self.inject_status = ctk.CTkLabel(r, text="Hazir", font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=COLORS["text_dim"])
        self.inject_status.pack(side="right")
        self.btn_inject = ctk.CTkButton(ii, text="Valorant'a inject et", height=44, fg_color=COLORS["accent_dim"], hover_color=COLORS["accent"], text_color=COLORS["text"], font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"), command=self._on_inject)
        self.btn_inject.pack(fill="x", pady=(10, 0))

        self.inject_master_on = False
        tr = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=8, border_width=1, border_color=COLORS["border"])
        tr.pack(fill="x", padx=24, pady=(0, 8))
        ti = ctk.CTkFrame(tr, fg_color="transparent")
        ti.pack(fill="x", padx=16, pady=10)
        ctk.CTkLabel(ti, text="Inject acik / kapali", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"), text_color=COLORS["text"]).pack(side="left")
        self.sw_inject_master = ctk.CTkSwitch(ti, text="", width=44, height=22, fg_color=COLORS["bg_input"], progress_color=COLORS["accent"], command=self._on_inject_master_toggle)
        self.sw_inject_master.pack(side="right")
        ctk.CTkLabel(ti, text="(anahtar)", font=ctk.CTkFont(size=11), text_color=COLORS["text_dim"]).pack(side="right", padx=(0, 8))

        fc = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        fc.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        fi = ctk.CTkFrame(fc, fg_color="transparent")
        fi.pack(fill="both", expand=True, padx=20, pady=16)
        ctk.CTkLabel(fi, text="Ozellikler (ac/kapa)", font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"), text_color=COLORS["text_dim"]).pack(anchor="w", pady=(0, 12))
        for key, desc in [("ESP", "Dusman konum"), ("Radar", "Mini harita"), ("No Recoil", "Geri tepme"), ("Triggerbot", "Otomatik ates")]:
            row = ctk.CTkFrame(fi, fg_color="transparent")
            row.pack(fill="x", pady=6)
            ctk.CTkLabel(row, text=key, font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"), text_color=COLORS["text"]).pack(side="left")
            ctk.CTkLabel(row, text=desc, font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color=COLORS["text_dim"]).pack(side="left", padx=(8, 0))
            self.toggle_state[key] = False
            sw = ctk.CTkSwitch(row, text="", width=44, height=22, fg_color=COLORS["bg_input"], progress_color=COLORS["accent"], button_color=COLORS["text"], button_hover_color=COLORS["text_dim"], command=lambda k=key: self._on_toggle(k))
            sw.pack(side="right")
            self.toggles[key] = sw

        foot = ctk.CTkFrame(self, fg_color="transparent", height=36)
        foot.pack(fill="x", padx=24, pady=(0, 16))
        foot.pack_propagate(False)
        self.footer_label = ctk.CTkLabel(foot, text="Hazir · Giris yapip inject edin", font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color=COLORS["text_dim"])
        self.footer_label.pack(side="left")

    def _on_login(self):
        uid = (self.entry_id.get() or "").strip()
        if not uid:
            self.inject_status.configure(text="Once giris yapin")
            self.footer_label.configure(text="Kullanici adi girin")
            return
        self.logged_in = True
        self.inject_status.configure(text="Hazir")
        self.footer_label.configure(text=f"Giris: {uid} · Inject icin hazir")
        messagebox.showinfo("Giris", f"Giris yapildi: {uid}")

    def _on_inject(self):
        if not self.logged_in:
            self.inject_status.configure(text="Once giris yapin")
            return
        self.inject_status.configure(text="Enjekte ediliyor...")
        self.btn_inject.configure(state="disabled")
        self.after(1200, self._finish_inject)

    def _finish_inject(self):
        self.injected = True
        self.inject_status.configure(text="Aktif", text_color=COLORS["success"])
        self.btn_inject.configure(text="Inject edildi", state="disabled", fg_color=COLORS["border"])
        self.status_dot.configure(fg_color=COLORS["success"])
        self.footer_label.configure(text="Valorant'a baglandi · Ozellikler acik/kapali")

    def _on_inject_master_toggle(self):
        self.inject_master_on = not self.inject_master_on
        if self.footer_label.winfo_exists():
            self.footer_label.configure(text="Inject ACIK" if self.inject_master_on else "Inject KAPALI")

    def _on_toggle(self, key):
        self.toggle_state[key] = not self.toggle_state.get(key, False)
        if self.footer_label.winfo_exists():
            s = "acik" if self.toggle_state[key] else "kapali"
            self.footer_label.configure(text=f"{key}: {s}")


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    app = ValorantMenuUI()
    app.mainloop()
