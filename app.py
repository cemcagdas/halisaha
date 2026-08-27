import io
import itertools
import json
import os
import shutil
import urllib.parse
import webbrowser
from datetime import datetime
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

DATA_FILE = "oyuncular.json"
MACLAR_FILE = "maclar.json"
BACKUP_DIR = "Yedekler"
EXPORT_DIR = "Kadro_Gorselleri"

FONT_FAMILY = "Segoe UI"

DEFAULT_LOKASYON = "ATAPARK HALISAHA"
DEFAULT_GUN = "Çarşamba"
DEFAULT_SAAT = "21:00 / 22:00"

def tr_temizle(metin):
    if not metin:
        return ""
    donusum = {
        'İ': 'I', 'ı': 'i', 'Ş': 'S', 'ş': 's', 
        'Ğ': 'G', 'ğ': 'g', 'Ü': 'U', 'ü': 'u', 
        'Ö': 'O', 'ö': 'o', 'Ç': 'C', 'ç': 'c'
    }
    sonuc = str(metin)
    for k, v in donusum.items():
        sonuc = sonuc.replace(k, v)
    return sonuc

VARSAYILAN_OYUNCULAR = [
    {"isim": "Askin", "mevki": "Defans", "ana_puan": 8.8, "ek_puan": 0.0, "telefon": "", "mac": 10, "galibiyet": 5, "beraberlik": 0, "maglubiyet": 5, "gelmedigi_hafta": 0},
    {"isim": "Aykut", "mevki": "Forvet", "ana_puan": 8.3, "ek_puan": 0.0, "telefon": "", "mac": 10, "galibiyet": 5, "beraberlik": 0, "maglubiyet": 5, "gelmedigi_hafta": 0},
    {"isim": "Cagdas", "mevki": "Defans", "ana_puan": 6.6, "ek_puan": 0.0, "telefon": "", "mac": 10, "galibiyet": 5, "beraberlik": 0, "maglubiyet": 5, "gelmedigi_hafta": 0},
    {"isim": "Caglar", "mevki": "Ortasaha", "ana_puan": 6.0, "ek_puan": 0.0, "telefon": "", "mac": 10, "galibiyet": 5, "beraberlik": 0, "maglubiyet": 5, "gelmedigi_hafta": 0},
    {"isim": "Erdal", "mevki": "Defans", "ana_puan": 5.8, "ek_puan": 0.0, "telefon": "", "mac": 10, "galibiyet": 5, "beraberlik": 0, "maglubiyet": 5, "gelmedigi_hafta": 0},
    {"isim": "Erkan", "mevki": "Defans", "ana_puan": 6.0, "ek_puan": 0.0, "telefon": "", "mac": 10, "galibiyet": 5, "beraberlik": 0, "maglubiyet": 5, "gelmedigi_hafta": 0},
    {"isim": "Gorkem", "mevki": "Kale", "ana_puan": 6.6, "ek_puan": 0.0, "telefon": "", "mac": 10, "galibiyet": 5, "beraberlik": 0, "maglubiyet": 5, "gelmedigi_hafta": 0},
    {"isim": "Kenan Komutan", "mevki": "Ortasaha", "ana_puan": 6.0, "ek_puan": 0.0, "telefon": "", "mac": 10, "galibiyet": 5, "beraberlik": 0, "maglubiyet": 5, "gelmedigi_hafta": 0},
    {"isim": "Muammer", "mevki": "Defans", "ana_puan": 6.9, "ek_puan": 0.0, "telefon": "", "mac": 10, "galibiyet": 5, "beraberlik": 0, "maglubiyet": 5, "gelmedigi_hafta": 0},
    {"isim": "Inan", "mevki": "Forvet", "ana_puan": 7.0, "ek_puan": 0.0, "telefon": "", "mac": 10, "galibiyet": 5, "beraberlik": 0, "maglubiyet": 5, "gelmedigi_hafta": 0},
    {"isim": "Ozay", "mevki": "Ortasaha", "ana_puan": 5.1, "ek_puan": 0.0, "telefon": "", "mac": 10, "galibiyet": 5, "beraberlik": 0, "maglubiyet": 5, "gelmedigi_hafta": 0},
    {"isim": "Semih", "mevki": "Ortasaha", "ana_puan": 8.4, "ek_puan": 0.0, "telefon": "", "mac": 10, "galibiyet": 5, "beraberlik": 0, "maglubiyet": 5, "gelmedigi_hafta": 0},
    {"isim": "Serci", "mevki": "Ortasaha", "ana_puan": 7.3, "ek_puan": 0.0, "telefon": "", "mac": 10, "galibiyet": 5, "beraberlik": 0, "maglubiyet": 5, "gelmedigi_hafta": 0},
    {"isim": "Sakir", "mevki": "Defans", "ana_puan": 6.9, "ek_puan": 0.0, "telefon": "", "mac": 10, "galibiyet": 5, "beraberlik": 0, "maglubiyet": 5, "gelmedigi_hafta": 0},
    {"isim": "Sevko", "mevki": "Kale", "ana_puan": 6.6, "ek_puan": 0.0, "telefon": "", "mac": 10, "galibiyet": 5, "beraberlik": 0, "maglubiyet": 5, "gelmedigi_hafta": 0},
    {"isim": "Tacettin", "mevki": "Ortasaha", "ana_puan": 6.3, "ek_puan": 0.0, "telefon": "", "mac": 10, "galibiyet": 5, "beraberlik": 0, "maglubiyet": 5, "gelmedigi_hafta": 0},
    {"isim": "Tolga", "mevki": "Ortasaha", "ana_puan": 6.1, "ek_puan": 0.0, "telefon": "", "mac": 10, "galibiyet": 5, "beraberlik": 0, "maglubiyet": 5, "gelmedigi_hafta": 0},
    {"isim": "Ugurcan", "mevki": "Ortasaha", "ana_puan": 5.9, "ek_puan": 0.0, "telefon": "", "mac": 10, "galibiyet": 5, "beraberlik": 0, "maglubiyet": 5, "gelmedigi_hafta": 0},
    {"isim": "Umutcan", "mevki": "Forvet", "ana_puan": 7.0, "ek_puan": 0.0, "telefon": "", "mac": 10, "galibiyet": 5, "beraberlik": 0, "maglubiyet": 5, "gelmedigi_hafta": 0},
    {"isim": "Zafer", "mevki": "Defans", "ana_puan": 6.7, "ek_puan": 0.0, "telefon": "", "mac": 10, "galibiyet": 5, "beraberlik": 0, "maglubiyet": 5, "gelmedigi_hafta": 0},
    {"isim": "Zeynel Evrim", "mevki": "Forvet", "ana_puan": 6.6, "ek_puan": 0.0, "telefon": "", "mac": 10, "galibiyet": 5, "beraberlik": 0, "maglubiyet": 5, "gelmedigi_hafta": 0},
    {"isim": "Zeynel Sonbahar", "mevki": "Defans", "ana_puan": 6.8, "ek_puan": 0.0, "telefon": "", "mac": 10, "galibiyet": 5, "beraberlik": 0, "maglubiyet": 5, "gelmedigi_hafta": 0}
]

def tr_sort_key(m):
    return str(m).lower()

class HaliSahaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hali Saha Kadro & 52 Haftalik Sezon Yonetim Sistemi")
        self.geometry("1480x950")
        
        self.klasorleri_olustur()
        self.oyuncular = self.verileri_yukle()
        self.maclar = self.maclari_yukle()
        self.oyunculari_sirala()
        
        self.row_widgets = []
        self.takim1 = []
        self.takim2 = []
        self.gecerli_kombinasyonlar = []
        self.kombinasyon_indeksi = 0
        self.son_secili_oyuncular = set()
        
        self.sort_column = "toplam_puan"
        self.sort_reverse = True
        
        self.arayuz_olustur()

    def klasorleri_olustur(self):
        for d in [BACKUP_DIR, EXPORT_DIR]:
            if not os.path.exists(d):
                os.makedirs(d)

    def otomatik_yedekle(self):
        try:
            zaman_damgasi = datetime.now().strftime("%Y%m%d_%H%M%S")
            if os.path.exists(DATA_FILE):
                shutil.copy(DATA_FILE, os.path.join(BACKUP_DIR, f"oyuncular_{zaman_damgasi}.json"))
            if os.path.exists(MACLAR_FILE):
                shutil.copy(MACLAR_FILE, os.path.join(BACKUP_DIR, f"maclar_{zaman_damgasi}.json"))
            
            for prefix in ["oyuncular_", "maclar_"]:
                dosyalar = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith(prefix)])
                if len(dosyalar) > 20:
                    for silinecek in dosyalar[:-20]:
                        os.remove(os.path.join(BACKUP_DIR, silinecek))
        except Exception:
            pass

    def verileri_yukle(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    veriler = json.load(f)
                    for p in veriler:
                        if "ana_puan" not in p and "puan" in p:
                            p["ana_puan"] = p["puan"]
                        if "ek_puan" not in p:
                            p["ek_puan"] = 0.0
                        if "telefon" not in p:
                            p["telefon"] = p.get("etiket", "")
                        if "beraberlik" not in p:
                            p["beraberlik"] = 0
                        if "maglubiyet" not in p:
                            p["maglubiyet"] = max(0, p.get("mac", 0) - p.get("galibiyet", 0) - p.get("beraberlik", 0))
                        if "gelmedigi_hafta" not in p:
                            p["gelmedigi_hafta"] = 0
                    return veriler
            except Exception:
                pass
        return VARSAYILAN_OYUNCULAR

    def maclari_yukle(self):
        sezon_52 = {str(i): {"oynandi": False, "skor_girildi": False, "tarih": "", "lokasyon": "", "gun": "", "saat": "", "skor1": "", "skor2": "", "takim1": [], "takim2": []} for i in range(1, 53)}
        if os.path.exists(MACLAR_FILE):
            try:
                with open(MACLAR_FILE, "r", encoding="utf-8") as f:
                    kayitli = json.load(f)
                    if isinstance(kayitli, dict):
                        for k, v in kayitli.items():
                            sezon_52[str(k)] = v
            except Exception:
                pass
        return sezon_52

    def verileri_kaydet(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.oyuncular, f, ensure_ascii=False, indent=2)
        self.otomatik_yedekle()

    def maclari_kaydet(self):
        with open(MACLAR_FILE, "w", encoding="utf-8") as f:
            json.dump(self.maclar, f, ensure_ascii=False, indent=2)
        self.otomatik_yedekle()

    def net_puan(self, p):
        return round(p.get("ana_puan", 6.0) + p.get("ek_puan", 0.0), 2)

    def galibiyet_orani(self, p):
        m = p.get("mac", 0)
        g = p.get("galibiyet", 0)
        return int((g / m) * 100) if m > 0 else 0

    def form_durumu_al(self, oyuncu_adi):
        sonuclar = []
        for i in range(1, 53):
            mac = self.maclar.get(str(i), {})
            if mac.get("skor_girildi", False):
                t1 = [p["isim"] for p in mac.get("takim1", [])]
                t2 = [p["isim"] for p in mac.get("takim2", [])]
                try:
                    s1 = int(mac.get("skor1", 0))
                    s2 = int(mac.get("skor2", 0))
                except ValueError:
                    continue

                if oyuncu_adi in t1:
                    if s1 > s2: sonuclar.append("G")
                    elif s2 > s1: sonuclar.append("M")
                    else: sonuclar.append("B")
                elif oyuncu_adi in t2:
                    if s2 > s1: sonuclar.append("G")
                    elif s1 > s2: sonuclar.append("M")
                    else: sonuclar.append("B")
        
        return sonuclar[-10:] if len(sonuclar) >= 10 else sonuclar

    def form_skoru_hesapla(self, oyuncu_adi):
        son_10 = self.form_durumu_al(oyuncu_adi)
        puan = 0
        for r in son_10:
            if r == "G": puan += 3
            elif r == "B": puan += 1
        return puan

    def kimya_istatistiklerini_hesapla(self):
        """Geçmiş maçlardan tüm ikili ortaklıkları ve kazanma oranlarını çıkarır."""
        ciftler = {}
        for i in range(1, 53):
            mac = self.maclar.get(str(i), {})
            if mac.get("skor_girildi", False):
                t1 = [p["isim"] for p in mac.get("takim1", [])]
                t2 = [p["isim"] for p in mac.get("takim2", [])]
                try:
                    s1 = int(mac.get("skor1", 0))
                    s2 = int(mac.get("skor2", 0))
                except ValueError:
                    continue

                for takim, kazandi, berabere in [(t1, s1 > s2, s1 == s2), (t2, s2 > s1, s1 == s2)]:
                    for p1, p2 in itertools.combinations(takim, 2):
                        cift_key = tuple(sorted([p1, p2]))
                        if cift_key not in ciftler:
                            ciftler[cift_key] = {"mac": 0, "galibiyet": 0, "beraberlik": 0, "maglubiyet": 0}
                        ciftler[cift_key]["mac"] += 1
                        if kazandi:
                            ciftler[cift_key]["galibiyet"] += 1
                        elif berabere:
                            ciftler[cift_key]["beraberlik"] += 1
                        else:
                            ciftler[cift_key]["maglubiyet"] += 1
        return ciftler

    def oyunculari_sirala(self):
        self.oyuncular.sort(key=lambda x: tr_sort_key(x.get("isim", "")))

    def akilli_baslangic_haftasi_bul(self):
        for i in range(1, 53):
            mac = self.maclar.get(str(i), {})
            if len(mac.get("takim1", [])) > 0 and not mac.get("skor_girildi", False):
                return f"{i}. Hafta"
        for i in range(1, 53):
            mac = self.maclar.get(str(i), {})
            if not mac.get("skor_girildi", False) and len(mac.get("takim1", [])) == 0:
                return f"{i}. Hafta"
        return "1. Hafta"

    def kadro_olustur(self):
        gelenler = [p for p in self.oyuncular if p.get("secili", False)]
        if len(gelenler) != 14:
            self.secili_sayisi_label.configure(text=f"HATA: Tam 14 kisi secilmeli! (Mevcut: {len(gelenler)})", text_color="#e74c3c")
            return

        suanki_isimler = set(p["isim"] for p in gelenler)
        
        if suanki_isimler != self.son_secili_oyuncular or not self.gecerli_kombinasyonlar:
            self.son_secili_oyuncular = suanki_isimler
            self.kombinasyon_indeksi = 0
            
            mevkiler = {}
            for p in gelenler:
                mevkiler.setdefault(p["mevki"], []).append(p)

            olasi_kadrolar = []
            for t1 in itertools.combinations(gelenler, 7):
                t2 = [p for p in gelenler if p not in t1]
                mevki_uygun = True
                for mvk, liste in mevkiler.items():
                    t1_sayi = sum(1 for p in t1 if p["mevki"] == mvk)
                    hedef = len(liste) // 2
                    if abs(t1_sayi - hedef) > (1 if len(liste) % 2 != 0 else 0):
                        mevki_uygun = False
                        break
                if mevki_uygun:
                    fark = abs(sum(self.net_puan(p) for p in t1) - sum(self.net_puan(p) for p in t2))
                    olasi_kadrolar.append((fark, list(t1), t2))

            olasi_kadrolar.sort(key=lambda x: x[0])
            self.gecerli_kombinasyonlar = olasi_kadrolar[:20]

        if not self.gecerli_kombinasyonlar:
            self.secili_sayisi_label.configure(text="Uygun mevki dengesinde kadro bulunamadi!", text_color="#e74c3c")
            return

        secilen = self.gecerli_kombinasyonlar[self.kombinasyon_indeksi % len(self.gecerli_kombinasyonlar)]
        fark, self.takim1, self.takim2 = secilen
        
        varyasyon_no = (self.kombinasyon_indeksi % len(self.gecerli_kombinasyonlar)) + 1
        toplam_varyasyon = len(self.gecerli_kombinasyonlar)
        self.kombinasyon_indeksi += 1

        self.son_varyasyon_no = varyasyon_no
        self.toplam_varyasyon_sayisi = toplam_varyasyon
        self.son_fark = fark

        self.kadro_tablosu_ciz(varyasyon_no, toplam_varyasyon, fark)
        self.kadro_kaydet_btn.configure(state="normal")
        self.mac_kaydet_btn.configure(state="normal")
        self.wp_metin_btn.configure(state="normal")
        self.wp_paylas_btn.configure(state="normal")

    def arayuz_olustur(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_kadro = self.tabview.add("Kadro Kurucu & Dengeleme")
        self.tab_istatistik = self.tabview.add("Oyuncu Istatistikleri")
        self.tab_kimya = self.tabview.add("Kimya & Sinerji Analizi")
        self.tab_sezon = self.tabview.add("Sezon Fiksturu (52 Hafta)")

        self.kadro_sekmesi_olustur()
        self.istatistik_sekmesi_olustur()
        self.kimya_sekmesi_olustur()
        self.sezon_sekmesi_olustur()

    def kadro_sekmesi_olustur(self):
        self.sol_panel = ctk.CTkFrame(self.tab_kadro, width=640)
        self.sol_panel.pack(side="left", fill="both", expand=False, padx=5, pady=5)
        ctk.CTkLabel(self.sol_panel, text="Oyuncu Havuzu", font=(FONT_FAMILY, 14, "bold")).pack(pady=5)

        baslik_frame = ctk.CTkFrame(self.sol_panel, fg_color="transparent")
        baslik_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(baslik_frame, text="Tik", width=40, font=(FONT_FAMILY, 11, "bold")).pack(side="left")
        ctk.CTkLabel(baslik_frame, text="Isim", width=120, font=(FONT_FAMILY, 11, "bold")).pack(side="left", padx=2)
        ctk.CTkLabel(baslik_frame, text="Mevki", width=95, font=(FONT_FAMILY, 11, "bold")).pack(side="left", padx=2)
        ctk.CTkLabel(baslik_frame, text="Sabit", width=55, font=(FONT_FAMILY, 11, "bold")).pack(side="left", padx=2)
        ctk.CTkLabel(baslik_frame, text="Ek", width=45, font=(FONT_FAMILY, 11, "bold")).pack(side="left", padx=2)
        ctk.CTkLabel(baslik_frame, text="Toplam", width=60, font=(FONT_FAMILY, 11, "bold"), text_color="#f1c40f").pack(side="left", padx=2)
        ctk.CTkLabel(baslik_frame, text="Tel / No", width=125, font=(FONT_FAMILY, 11, "bold"), text_color="#2ecc71").pack(side="left", padx=2)
        ctk.CTkLabel(baslik_frame, text="Sil", width=30, font=(FONT_FAMILY, 11, "bold")).pack(side="left", padx=2)

        self.liste_frame = ctk.CTkScrollableFrame(self.sol_panel, width=610, height=430)
        self.liste_frame.pack(fill="both", expand=True, padx=5, pady=5)

        alt_bar = ctk.CTkFrame(self.sol_panel, fg_color="transparent")
        alt_bar.pack(fill="x", padx=5, pady=4)
        self.yeni_isim_ent = ctk.CTkEntry(alt_bar, placeholder_text="Yeni Isim", width=110, font=(FONT_FAMILY, 11))
        self.yeni_isim_ent.pack(side="left", padx=2)
        self.yeni_mevki_opt = ctk.CTkOptionMenu(alt_bar, values=["Kale", "Defans", "Ortasaha", "Forvet"], width=95, font=(FONT_FAMILY, 11))
        self.yeni_mevki_opt.pack(side="left", padx=2)
        self.yeni_puan_ent = ctk.CTkEntry(alt_bar, placeholder_text="Sabit (6.0)", width=75, font=(FONT_FAMILY, 11))
        self.yeni_puan_ent.pack(side="left", padx=2)
        self.yeni_tel_ent = ctk.CTkEntry(alt_bar, placeholder_text="Tel / No", width=115, font=(FONT_FAMILY, 11))
        self.yeni_tel_ent.pack(side="left", padx=2)
        self.ekle_btn = ctk.CTkButton(alt_bar, text="+ Ekle", width=65, command=self.yeni_oyuncu_ekle, fg_color="#2980b9", hover_color="#1f618d", font=(FONT_FAMILY, 11, "bold"))
        self.ekle_btn.pack(side="left", padx=4)

        sifirla_bar = ctk.CTkFrame(self.sol_panel, fg_color="transparent")
        sifirla_bar.pack(fill="x", padx=5, pady=3)
        
        btn_ek_sifirla = ctk.CTkButton(sifirla_bar, text="Ek Puanlari Sifirla (0.0)", command=self.onayli_ek_puan_sifirla, fg_color="#7f8c8d", hover_color="#636e72", font=(FONT_FAMILY, 11, "bold"), height=26)
        btn_ek_sifirla.pack(side="left", fill="x", expand=True, padx=2)

        btn_ist_sifirla = ctk.CTkButton(sifirla_bar, text="Istatistikleri Sifirla", command=self.onayli_istatistik_sifirla, fg_color="#c0392b", hover_color="#962d22", font=(FONT_FAMILY, 11, "bold"), height=26)
        btn_ist_sifirla.pack(side="right", fill="x", expand=True, padx=2)

        self.secili_sayisi_label = ctk.CTkLabel(self.sol_panel, text="Secili Oyuncu: 0 / 14", font=(FONT_FAMILY, 13, "bold"), text_color="#3498db")
        self.secili_sayisi_label.pack(pady=2)
        
        self.kadro_butonu = ctk.CTkButton(self.sol_panel, text="KADRO KUR (7 vs 7)", command=self.kadro_olustur, fg_color="#27ae60", hover_color="#219150", font=(FONT_FAMILY, 13, "bold"), height=35)
        self.kadro_butonu.pack(fill="x", padx=5, pady=4)

        # Sağ Panel
        self.sag_panel = ctk.CTkFrame(self.tab_kadro)
        self.sag_panel.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        self.sonuc_frame = ctk.CTkFrame(self.sag_panel)
        self.sonuc_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.mac_sonu_frame = ctk.CTkFrame(self.sag_panel, fg_color="#1a1a1a")
        self.mac_sonu_frame.pack(fill="x", padx=5, pady=5)

        ust_satir = ctk.CTkFrame(self.mac_sonu_frame, fg_color="transparent")
        ust_satir.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(ust_satir, text="Hafta Sec:", font=(FONT_FAMILY, 11, "bold")).pack(side="left", padx=(5, 2))
        haftalar = [f"{i}. Hafta" for i in range(1, 53)]
        self.hafta_secim_opt = ctk.CTkOptionMenu(ust_satir, values=haftalar, width=105, font=(FONT_FAMILY, 11), command=self.hafta_degisti)
        
        baslangic_haftasi = self.akilli_baslangic_haftasi_bul()
        self.hafta_secim_opt.set(baslangic_haftasi)
        self.hafta_secim_opt.pack(side="left", padx=4)

        ctk.CTkLabel(ust_satir, text="Tarih:", font=(FONT_FAMILY, 11, "bold")).pack(side="left", padx=(10, 2))
        self.tarih_ent = ctk.CTkEntry(ust_satir, width=95, font=(FONT_FAMILY, 11))
        self.tarih_ent.insert(0, datetime.now().strftime("%d.%m.%Y"))
        self.tarih_ent.pack(side="left", padx=2)

        detay_satir = ctk.CTkFrame(self.mac_sonu_frame, fg_color="transparent")
        detay_satir.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(detay_satir, text="Lokasyon:", font=(FONT_FAMILY, 11, "bold")).pack(side="left", padx=(5, 2))
        self.lokasyon_ent = ctk.CTkEntry(detay_satir, placeholder_text="Saha Adi", width=145, font=(FONT_FAMILY, 11))
        self.lokasyon_ent.insert(0, DEFAULT_LOKASYON)
        self.lokasyon_ent.pack(side="left", padx=2)

        ctk.CTkLabel(detay_satir, text="Gun:", font=(FONT_FAMILY, 11, "bold")).pack(side="left", padx=(8, 2))
        self.gun_ent = ctk.CTkEntry(detay_satir, placeholder_text="Gun", width=85, font=(FONT_FAMILY, 11))
        self.gun_ent.insert(0, DEFAULT_GUN)
        self.gun_ent.pack(side="left", padx=2)

        ctk.CTkLabel(detay_satir, text="Saat:", font=(FONT_FAMILY, 11, "bold")).pack(side="left", padx=(8, 2))
        self.saat_ent = ctk.CTkEntry(detay_satir, placeholder_text="Saat", width=105, font=(FONT_FAMILY, 11))
        self.saat_ent.insert(0, DEFAULT_SAAT)
        self.saat_ent.pack(side="left", padx=2)

        skor_satir = ctk.CTkFrame(self.mac_sonu_frame, fg_color="transparent")
        skor_satir.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(skor_satir, text="Turuncu Skor:", font=(FONT_FAMILY, 11, "bold"), text_color="#f39c12").pack(side="left", padx=(5, 2))
        self.t1_skor_ent = ctk.CTkEntry(skor_satir, width=45, placeholder_text="0", font=(FONT_FAMILY, 11))
        self.t1_skor_ent.pack(side="left", padx=2)

        ctk.CTkLabel(skor_satir, text="-", font=(FONT_FAMILY, 14, "bold")).pack(side="left", padx=4)

        self.t2_skor_ent = ctk.CTkEntry(skor_satir, width=45, placeholder_text="0", font=(FONT_FAMILY, 11))
        self.t2_skor_ent.pack(side="left", padx=2)
        ctk.CTkLabel(skor_satir, text=":Siyah Skor", font=(FONT_FAMILY, 11, "bold"), text_color="#ecf0f1").pack(side="left", padx=2)

        btn_butonlar_bar = ctk.CTkFrame(self.mac_sonu_frame, fg_color="transparent")
        btn_butonlar_bar.pack(fill="x", padx=5, pady=2)

        self.kadro_kaydet_btn = ctk.CTkButton(btn_butonlar_bar, text="KADROYU FIKSTURE KAYDET (Mac Onu)", command=self.sadece_kadro_kaydet, fg_color="#2980b9", hover_color="#1f618d", font=(FONT_FAMILY, 11, "bold"), height=30, state="disabled")
        self.kadro_kaydet_btn.pack(side="left", fill="x", expand=True, padx=2)

        self.mac_kaydet_btn = ctk.CTkButton(btn_butonlar_bar, text="SKORU VE ISTATISTIKLERI ISLE (Mac Sonu)", command=self.mac_ve_skor_kaydet, fg_color="#d35400", hover_color="#ba4a00", font=(FONT_FAMILY, 11, "bold"), height=30, state="disabled")
        self.mac_kaydet_btn.pack(side="right", fill="x", expand=True, padx=2)

        wp_bar = ctk.CTkFrame(self.mac_sonu_frame, fg_color="transparent")
        wp_bar.pack(fill="x", padx=5, pady=2)

        self.wp_metin_btn = ctk.CTkButton(wp_bar, text="📋 Sadece Metni Kopyala", command=self.whatsapp_metni_kopyala, fg_color="#34495e", hover_color="#2c3e50", text_color="#ecf0f1", font=(FONT_FAMILY, 11, "bold"), height=28, state="disabled")
        self.wp_metin_btn.pack(side="left", fill="x", expand=True, padx=2)

        self.wp_paylas_btn = ctk.CTkButton(wp_bar, text="🚀 WhatsApp'ta Paylas (Metin + Gorsel)", command=self.whatsapp_dogrudan_paylas, fg_color="#25D366", hover_color="#1EBE5D", text_color="#111111", font=(FONT_FAMILY, 11, "bold"), height=28, state="disabled")
        self.wp_paylas_btn.pack(side="right", fill="x", expand=True, padx=2)

        self.oyuncu_listesini_ciz()
        self.hafta_degisti(baslangic_haftasi)

    def metin_olustur(self):
        hafta = self.hafta_secim_opt.get()
        tarih = self.tarih_ent.get().strip() or datetime.now().strftime("%d.%m.%Y")
        lokasyon = self.lokasyon_ent.get().strip() or DEFAULT_LOKASYON
        gun = self.gun_ent.get().strip() or DEFAULT_GUN
        saat = self.saat_ent.get().strip() or DEFAULT_SAAT

        t1_satirlar = [f"• {p['isim']} ({p['mevki']})" for p in self.takim1]
        t2_satirlar = [f"• {p['isim']} ({p['mevki']})" for p in self.takim2]

        zaman_bilgi = f"{gun} - {saat}"

        return (
            f"⚽ *{hafta.upper()} HALI SAHA MAC DUYURUSU*\n"
            f"📍 *Lokasyon:* {lokasyon}\n"
            f"🗓 *Tarih & Saat:* {tarih} | {zaman_bilgi}\n\n"
            f"🟠 *TURUNCU TAKIM:*\n" + "\n".join(t1_satirlar) + "\n\n"
            f"⚫ *SIYAH TAKIM:*\n" + "\n".join(t2_satirlar) + "\n\n"
            f"🏆 Herkese keyifli ve sakatliksiz maclar dileriz!"
        )

    def whatsapp_metni_kopyala(self):
        if not self.takim1 or not self.takim2:
            return
        metin = self.metin_olustur()
        self.clipboard_clear()
        self.clipboard_append(metin)
        self.secili_sayisi_label.configure(text="WhatsApp duyuru metni panoya kopyalandi!", text_color="#2ecc71")

    def whatsapp_dogrudan_paylas(self):
        if not self.takim1 or not self.takim2:
            return

        kayit_yolu = self.kadro_gorseli_olustur_dosya()
        metin = self.metin_olustur()
        encoded_metin = urllib.parse.quote(metin)
        wp_url = f"https://web.whatsapp.com/send?text={encoded_metin}"
        webbrowser.open(wp_url)

        if kayit_yolu and os.path.exists(kayit_yolu):
            try:
                os.system(f'explorer /select,"{os.path.abspath(kayit_yolu)}"')
            except Exception:
                pass

        self.secili_sayisi_label.configure(text="WhatsApp acildi! Gorseli sohbete surukleyip birakabilirsiniz.", text_color="#2ecc71")

    def kadro_gorseli_olustur_dosya(self):
        if not PIL_AVAILABLE:
            return None

        hafta = tr_temizle(self.hafta_secim_opt.get())
        tarih = self.tarih_ent.get().strip() or datetime.now().strftime("%d.%m.%Y")
        lokasyon = tr_temizle(self.lokasyon_ent.get().strip() or DEFAULT_LOKASYON)
        gun = tr_temizle(self.gun_ent.get().strip() or DEFAULT_GUN)
        saat = self.saat_ent.get().strip() or DEFAULT_SAAT
        
        detay_str = f"{hafta}  |  {gun}  |  Saat: {saat}  |  Saha: {lokasyon}"
        fark = abs(sum(self.net_puan(p) for p in self.takim1) - sum(self.net_puan(p) for p in self.takim2))

        img_w, img_h = 1200, 780
        img = Image.new("RGB", (img_w, img_h), color="#131c26")
        draw = ImageDraw.Draw(img)

        draw.rounded_rectangle([25, 20, img_w - 25, 75], radius=8, fill="#17202a")
        draw.text((45, 47), detay_str, fill="#e67e22", anchor="lm", font_size=19)
        draw.rounded_rectangle([img_w - 210, 29, img_w - 45, 66], radius=6, fill="#27ae60" if fark < 0.5 else "#e67e22")
        draw.text((img_w - 127, 47), f"Puan Farki: {fark:.2f}", fill="#ffffff", anchor="mm", font_size=15)

        mevki_renkleri = {"Kale": "#e74c3c", "Defans": "#3498db", "Ortasaha": "#2ecc71", "Forvet": "#f39c12"}
        sira = {"Kale": 1, "Defans": 2, "Ortasaha": 3, "Forvet": 4}

        def ciz_takim_karti(x1, y1, x2, y2, takim_adi, takim_puan, takim_listesi, kart_renk, kenar_renk, forma_renk):
            draw.rounded_rectangle([x1, y1, x2, y2], radius=10, fill="#1c2833", outline=kenar_renk, width=2)
            draw.rounded_rectangle([x1 + 10, y1 + 10, x2 - 10, y1 + 55], radius=8, fill=kart_renk)
            draw.text((x1 + 25, y1 + 32), takim_adi, fill="#ffffff", anchor="lm", font_size=17)
            
            draw.rounded_rectangle([x2 - 105, y1 + 16, x2 - 20, y1 + 48], radius=6, fill="#1c2833")
            draw.text((x2 - 62, y1 + 32), f"{takim_puan:.1f} P", fill="#f1c40f", anchor="mm", font_size=15)

            list_y = y1 + 65
            for idx, p in enumerate(sorted(takim_listesi, key=lambda x: sira.get(x["mevki"], 5))):
                row_y = list_y + (idx * 34)
                draw.rounded_rectangle([x1 + 10, row_y, x2 - 10, row_y + 30], radius=5, fill="#273746")
                
                m_renk = mevki_renkleri.get(p["mevki"], "#7f8c8d")
                draw.rounded_rectangle([x1 + 15, row_y + 3, x1 + 65, row_y + 27], radius=4, fill=m_renk)
                draw.text((x1 + 40, row_y + 15), tr_temizle(p["mevki"][:3].upper()), fill="#ffffff", anchor="mm", font_size=11)
                
                draw.text((x1 + 75, row_y + 15), tr_temizle(p["isim"]), fill="#ffffff", anchor="lm", font_size=14)
                draw.text((x2 - 25, row_y + 15), f"{self.net_puan(p):.1f} P", fill="#f1c40f" if "TURUNCU" in takim_adi else "#ecf0f1", anchor="rm", font_size=13)

            saha_x1 = x1 + 15
            saha_x2 = x2 - 15
            saha_y1 = y1 + 315
            saha_y2 = y2 - 15
            saha_w = saha_x2 - saha_x1
            saha_h = saha_y2 - saha_y1

            side_inset = saha_w * 0.08
            p_top_y = saha_y1 + saha_h * 0.06
            p_bot_y = saha_y1 + saha_h * 0.88
            depth_3d = saha_h * 0.05

            draw.polygon([
                (saha_x1 + side_inset, p_bot_y),
                (saha_x2 - side_inset, p_bot_y),
                (saha_x2 - side_inset, p_bot_y + depth_3d),
                (saha_x1 + side_inset, p_bot_y + depth_3d)
            ], fill="#0a3818")

            draw.polygon([
                (saha_x2 - side_inset, p_top_y),
                (saha_x2 - side_inset, p_bot_y),
                (saha_x2 - side_inset, p_bot_y + depth_3d),
                (saha_x2 - side_inset, p_top_y + depth_3d)
            ], fill="#0d421d")

            draw.polygon([
                (saha_x1 + side_inset, p_top_y),
                (saha_x2 - side_inset, p_top_y),
                (saha_x2 - side_inset, p_bot_y),
                (saha_x1 + side_inset, p_bot_y)
            ], fill="#157335", outline="#7bed9f", width=2)

            def s_xy(u, v):
                cur_y = p_top_y + (p_bot_y - p_top_y) * v
                cur_xl = saha_x1 + side_inset
                cur_xr = saha_x2 - side_inset
                cur_x = cur_xl + (cur_xr - cur_xl) * u
                return cur_x, cur_y

            tl = s_xy(0.03, 0.03)
            tr = s_xy(0.97, 0.03)
            br = s_xy(0.97, 0.97)
            bl = s_xy(0.03, 0.97)
            draw.polygon([tl, tr, br, bl], fill=None, outline="#ffffff", width=2)

            ml = s_xy(0.03, 0.52)
            mr = s_xy(0.97, 0.52)
            draw.line([ml, mr], fill="#ffffff", width=2)

            cx, cy = s_xy(0.5, 0.52)
            draw.ellipse([cx - saha_w*0.13, cy - saha_h*0.05, cx + saha_w*0.13, cy + saha_h*0.05], outline="#ffffff", width=2)

            k1, k2, k3, k4 = s_xy(0.28, 0.03), s_xy(0.72, 0.03), s_xy(0.72, 0.20), s_xy(0.28, 0.20)
            draw.polygon([k1, k2, k3, k4], fill=None, outline="#ffffff", width=2)

            a1, a2, a3, a4 = s_xy(0.28, 0.97), s_xy(0.72, 0.97), s_xy(0.72, 0.80), s_xy(0.28, 0.80)
            draw.polygon([a1, a2, a3, a4], fill=None, outline="#ffffff", width=2)

            fw = 18
            fh = 18
            def ciz_forma_img(px, py, isim, no, f_col, kollar_beyaz=True):
                if kollar_beyaz:
                    draw.polygon([(px - fw*0.6, py - fh*0.4), (px - fw*1.0, py - fh*0.05), (px - fw*0.7, py + fh*0.35), (px - fw*0.4, py + fh*0.05)], fill="#ffffff", outline="#222222")
                    draw.polygon([(px + fw*0.6, py - fh*0.4), (px + fw*1.0, py - fh*0.05), (px + fw*0.7, py + fh*0.35), (px + fw*0.4, py + fh*0.05)], fill="#ffffff", outline="#222222")
                
                draw.polygon([(px - fw*0.6, py - fh*0.4), (px + fw*0.6, py - fh*0.4), (px + fw*0.5, py + fh*0.5), (px - fw*0.5, py + fh*0.5)], fill=f_col, outline="#111111")
                draw.text((px, py + 1), str(no), fill="#ffffff", anchor="mm", font_size=10)

                isim_k = tr_temizle(isim.split()[0][:8])
                bw = max(42, len(isim_k) * 7 + 10)
                bh = 14
                draw.rectangle([px - bw/2, py + fh*0.5 + 2, px + bw/2, py + fh*0.5 + 2 + bh], fill="#ffffff", outline="#000000")
                draw.text((px, py + fh*0.5 + 9), isim_k, fill="#000000", anchor="mm", font_size=10)

            mevkiler = {"Kale": [], "Defans": [], "Ortasaha": [], "Forvet": []}
            for p in takim_listesi:
                mevkiler.setdefault(p.get("mevki", "Ortasaha"), []).append(p)

            f_no = 1
            for p in mevkiler.get("Kale", []):
                px, py = s_xy(0.5, 0.06)
                ciz_forma_img(px, py, p["isim"], f_no, "#2ecc71", kollar_beyaz=False)
                f_no += 1

            for mvk_adi, v_oran in [("Defans", 0.28), ("Ortasaha", 0.54), ("Forvet", 0.80)]:
                m_list = mevkiler.get(mvk_adi, [])
                for i, p in enumerate(m_list):
                    u_pos = (i + 1) / (len(m_list) + 1)
                    px, py = s_xy(u_pos, v_oran)
                    ciz_forma_img(px, py, p["isim"], f_no, forma_renk, kollar_beyaz=True)
                    f_no += 1

        t1_toplam = sum(self.net_puan(p) for p in self.takim1)
        t2_toplam = sum(self.net_puan(p) for p in self.takim2)

        ciz_takim_karti(25, 90, 585, 750, "TURUNCU TAKIM", t1_toplam, self.takim1, "#e67e22", "#e67e22", "#e67e22")
        ciz_takim_karti(615, 90, 1175, 750, "SIYAH TAKIM", t2_toplam, self.takim2, "#34495e", "#5d6d7e", "#2c3e50")

        dosya_adi = f"Kadro_{hafta.replace(' ', '_').replace('.', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        kayit_yolu = os.path.join(EXPORT_DIR, dosya_adi)
        img.save(kayit_yolu)
        return kayit_yolu

    def hafta_degisti(self, secim):
        hafta_no = secim.split(".")[0].strip()
        mac = self.maclar.get(hafta_no, {})
        
        t1 = mac.get("takim1", [])
        t2 = mac.get("takim2", [])
        
        self.tarih_ent.delete(0, "end")
        self.tarih_ent.insert(0, mac.get("tarih", datetime.now().strftime("%d.%m.%Y")))
        
        self.lokasyon_ent.delete(0, "end")
        self.lokasyon_ent.insert(0, mac.get("lokasyon", "") or DEFAULT_LOKASYON)
        
        self.gun_ent.delete(0, "end")
        self.gun_ent.insert(0, mac.get("gun", "") or DEFAULT_GUN)
        
        self.saat_ent.delete(0, "end")
        self.saat_ent.insert(0, mac.get("saat", "") or DEFAULT_SAAT)

        if t1 and t2:
            self.takim1 = []
            self.takim2 = []
            
            for k in t1:
                p_bulunur = next((p for p in self.oyuncular if p["isim"] == k["isim"]), None)
                if p_bulunur:
                    self.takim1.append(p_bulunur)
                else:
                    self.takim1.append({"isim": k["isim"], "mevki": k["mevki"], "ana_puan": 6.0, "ek_puan": 0.0, "telefon": ""})

            for k in t2:
                p_bulunur = next((p for p in self.oyuncular if p["isim"] == k["isim"]), None)
                if p_bulunur:
                    self.takim2.append(p_bulunur)
                else:
                    self.takim2.append({"isim": k["isim"], "mevki": k["mevki"], "ana_puan": 6.0, "ek_puan": 0.0, "telefon": ""})

            fark = abs(sum(self.net_puan(p) for p in self.takim1) - sum(self.net_puan(p) for p in self.takim2))
            self.kadro_tablosu_ciz(1, 1, fark)
            self.kadro_kaydet_btn.configure(state="normal")
            self.mac_kaydet_btn.configure(state="normal")
            self.wp_metin_btn.configure(state="normal")
            self.wp_paylas_btn.configure(state="normal")
            
            if mac.get("skor_girildi", False):
                self.t1_skor_ent.delete(0, "end")
                self.t1_skor_ent.insert(0, str(mac.get("skor1", "")))
                self.t2_skor_ent.delete(0, "end")
                self.t2_skor_ent.insert(0, str(mac.get("skor2", "")))
        else:
            for w in self.sonuc_frame.winfo_children():
                w.destroy()
            self.takim1 = []
            self.takim2 = []
            self.kadro_kaydet_btn.configure(state="disabled")
            self.mac_kaydet_btn.configure(state="disabled")
            self.wp_metin_btn.configure(state="disabled")
            self.wp_paylas_btn.configure(state="disabled")

    def oyuncu_listesini_ciz(self):
        for w in self.liste_frame.winfo_children():
            w.destroy()
        self.row_widgets = []
        for idx, p in enumerate(self.oyuncular):
            row = ctk.CTkFrame(self.liste_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)

            cb_var = ctk.BooleanVar(value=p.get("secili", False))
            cb = ctk.CTkCheckBox(row, text="", variable=cb_var, width=35, command=lambda i=idx, v=cb_var: self.tik_degisti(i, v))
            cb.pack(side="left", padx=1)

            isim_entry = ctk.CTkEntry(row, width=120, font=(FONT_FAMILY, 11))
            isim_entry.insert(0, p.get("isim", ""))
            isim_entry.pack(side="left", padx=1)
            isim_entry.bind("<FocusOut>", lambda e, i=idx, ent=isim_entry: self.isim_degisti(i, ent))

            mevki_opt = ctk.CTkOptionMenu(row, values=["Kale", "Defans", "Ortasaha", "Forvet"], width=95, font=(FONT_FAMILY, 11), command=lambda val, i=idx: self.mevki_degisti(i, val))
            mevki_opt.set(p.get("mevki", "Ortasaha"))
            mevki_opt.pack(side="left", padx=1)

            ana_puan_entry = ctk.CTkEntry(row, width=50, font=(FONT_FAMILY, 11))
            ana_puan_entry.insert(0, str(p.get("ana_puan", 6.0)))
            ana_puan_entry.pack(side="left", padx=1)
            ana_puan_entry.bind("<FocusOut>", lambda e, i=idx, ent=ana_puan_entry: self.ana_puan_degisti(i, ent))

            ek_puan_val = p.get("ek_puan", 0.0)
            ek_puan_text = f"+{ek_puan_val:.1f}" if ek_puan_val > 0 else f"{ek_puan_val:.1f}"
            lbl_ek_puan = ctk.CTkLabel(row, text=ek_puan_text, width=45, font=(FONT_FAMILY, 11, "bold"), text_color="#2ecc71" if ek_puan_val > 0 else ("#e74c3c" if ek_puan_val < 0 else "#bdc3c7"))
            lbl_ek_puan.pack(side="left", padx=1)

            lbl_toplam = ctk.CTkLabel(row, text=f"{self.net_puan(p):.1f}", width=55, font=(FONT_FAMILY, 12, "bold"), text_color="#f1c40f")
            lbl_toplam.pack(side="left", padx=1)

            tel_entry = ctk.CTkEntry(row, width=125, placeholder_text="Tel / No", font=(FONT_FAMILY, 11))
            tel_entry.insert(0, p.get("telefon", ""))
            tel_entry.pack(side="left", padx=1)
            tel_entry.bind("<FocusOut>", lambda e, i=idx, ent=tel_entry: self.telefon_degisti(i, ent))

            del_btn = ctk.CTkButton(row, text="X", width=25, fg_color="#c0392b", hover_color="#962d22", font=(FONT_FAMILY, 10, "bold"), command=lambda i=idx, isim=p["isim"]: self.onayli_oyuncu_sil(i, isim))
            del_btn.pack(side="left", padx=1)

            self.row_widgets.append({"cb_var": cb_var, "isim_ent": isim_entry, "ana_puan_ent": ana_puan_entry, "tel_ent": tel_entry})
        self.secili_sayisi_guncelle()

    def tik_degisti(self, idx, var):
        self.oyuncular[idx]["secili"] = var.get()
        self.verileri_kaydet()
        self.secili_sayisi_guncelle()

    def isim_degisti(self, idx, entry):
        yeni_ad = entry.get().strip()
        if yeni_ad and yeni_ad != self.oyuncular[idx]["isim"]:
            self.oyuncular[idx]["isim"] = yeni_ad
            self.oyunculari_sirala()
            self.verileri_kaydet()
            self.oyuncu_listesini_ciz()
            self.istatistik_tablosunu_ciz()
            self.kimya_oyuncu_listesini_guncelle()

    def mevki_degisti(self, idx, yeni_mevki):
        self.oyuncular[idx]["mevki"] = yeni_mevki
        self.verileri_kaydet()
        self.istatistik_tablosunu_ciz()

    def ana_puan_degisti(self, idx, entry):
        try:
            val = float(entry.get().replace(",", "."))
            self.oyuncular[idx]["ana_puan"] = round(val, 2)
            self.verileri_kaydet()
            self.oyuncu_listesini_ciz()
            self.istatistik_tablosunu_ciz()
        except ValueError:
            entry.delete(0, "end")
            entry.insert(0, str(self.oyuncular[idx]["ana_puan"]))

    def telefon_degisti(self, idx, entry):
        tel_val = entry.get().strip()
        self.oyuncular[idx]["telefon"] = tel_val
        self.verileri_kaydet()

    def yeni_oyuncu_ekle(self):
        ad = self.yeni_isim_ent.get().strip()
        mevki = self.yeni_mevki_opt.get()
        puan_str = self.yeni_puan_ent.get().replace(",", ".").strip()
        tel = self.yeni_tel_ent.get().strip()
        if not ad: return
        try: puan = float(puan_str) if puan_str else 6.0
        except ValueError: puan = 6.0
        self.oyuncular.append({"isim": ad, "mevki": mevki, "ana_puan": puan, "ek_puan": 0.0, "telefon": tel, "mac": 0, "galibiyet": 0, "beraberlik": 0, "maglubiyet": 0, "gelmedigi_hafta": 0, "secili": False})
        self.oyunculari_sirala()
        self.verileri_kaydet()
        self.oyuncu_listesini_ciz()
        self.istatistik_tablosunu_ciz()
        self.kimya_oyuncu_listesini_guncelle()
        self.yeni_isim_ent.delete(0, "end")
        self.yeni_puan_ent.delete(0, "end")
        self.yeni_tel_ent.delete(0, "end")

    def onayli_oyuncu_sil(self, idx, isim):
        cevap = messagebox.askyesno("Oyuncu Silme Onayi", f"'{isim}' isimli oyuncu havuzdan kalici olarak silinecek. Emin misiniz?")
        if cevap:
            self.oyuncu_sil(idx)

    def oyuncu_sil(self, idx):
        self.oyuncular.pop(idx)
        self.verileri_kaydet()
        self.oyuncu_listesini_ciz()
        self.istatistik_tablosunu_ciz()
        self.kimya_oyuncu_listesini_guncelle()

    def secili_sayisi_guncelle(self):
        secili_sayisi = sum(1 for p in self.oyuncular if p.get("secili", False))
        if hasattr(self, "secili_sayisi_label"):
            self.secili_sayisi_label.configure(text=f"Secili Oyuncu: {secili_sayisi} / 14", text_color="#3498db" if secili_sayisi == 14 else "#f39c12")

    def onayli_ek_puan_sifirla(self):
        cevap = messagebox.askyesno("Onay", "Tum oyuncularin ek puanlari (0.0) olarak sifirlanacak. Emin misiniz?")
        if cevap:
            self.ek_puanlari_sifirla()

    def ek_puanlari_sifirla(self):
        for p in self.oyuncular:
            p["ek_puan"] = 0.0
        self.verileri_kaydet()
        self.oyuncu_listesini_ciz()
        self.istatistik_tablosunu_ciz()
        self.secili_sayisi_label.configure(text="Tum oyuncularin ek puanlari 0.0 yapildi!", text_color="#f1c40f")

    def onayli_istatistik_sifirla(self):
        cevap = messagebox.askyesno("Kritik Uyari", "Tum oyuncu mac, galibiyet ve istatistik verileri kalici olarak sifirlanacak! Emin misiniz?")
        if cevap:
            self.istatistikleri_sifirla()

    def istatistikleri_sifirla(self):
        for p in self.oyuncular:
            p["mac"] = 0
            p["galibiyet"] = 0
            p["beraberlik"] = 0
            p["maglubiyet"] = 0
            p["gelmedigi_hafta"] = 0
        self.verileri_kaydet()
        self.istatistik_tablosunu_ciz()
        self.kimya_tablosunu_ciz()
        self.secili_sayisi_label.configure(text="Tum oyuncu istatistikleri sifirlandi!", text_color="#e74c3c")

    def sadece_kadro_kaydet(self):
        if len(self.takim1) != 7 or len(self.takim2) != 7:
            self.secili_sayisi_label.configure(text="HATA: Once 7 vs 7 kadro olusturun!", text_color="#e74c3c")
            return

        secilen_hafta_str = self.hafta_secim_opt.get()
        hafta_no = secilen_hafta_str.split(".")[0].strip()
        tarih_str = self.tarih_ent.get().strip()
        if not tarih_str:
            tarih_str = datetime.now().strftime("%d.%m.%Y")

        lokasyon_str = self.lokasyon_ent.get().strip() or DEFAULT_LOKASYON
        gun_str = self.gun_ent.get().strip() or DEFAULT_GUN
        saat_str = self.saat_ent.get().strip() or DEFAULT_SAAT

        mevcut = self.maclar.get(hafta_no, {})
        self.maclar[hafta_no] = {
            "oynandi": mevcut.get("oynandi", False),
            "skor_girildi": mevcut.get("skor_girildi", False),
            "tarih": tarih_str,
            "lokasyon": lokasyon_str,
            "gun": gun_str,
            "saat": saat_str,
            "skor1": mevcut.get("skor1", ""),
            "skor2": mevcut.get("skor2", ""),
            "takim1": [{"isim": p["isim"], "mevki": p["mevki"]} for p in self.takim1],
            "takim2": [{"isim": p["isim"], "mevki": p["mevki"]} for p in self.takim2]
        }
        self.maclari_kaydet()
        self.sezon_kartlarini_ciz()
        
        fark = abs(sum(self.net_puan(p) for p in self.takim1) - sum(self.net_puan(p) for p in self.takim2))
        self.kadro_tablosu_ciz(getattr(self, 'son_varyasyon_no', 1), getattr(self, 'toplam_varyasyon_sayisi', 1), fark)
        
        self.secili_sayisi_label.configure(text=f"{hafta_no}. Hafta kadrosu ve detaylari fiksture kaydedildi.", text_color="#3498db")

    def mac_ve_skor_kaydet(self):
        if len(self.takim1) != 7 or len(self.takim2) != 7:
            self.secili_sayisi_label.configure(text="HATA: Once 7 vs 7 kadro olusturun!", text_color="#e74c3c")
            return

        try:
            skor1 = int(self.t1_skor_ent.get().strip())
            skor2 = int(self.t2_skor_ent.get().strip())
        except ValueError:
            self.secili_sayisi_label.configure(text="HATA: Lutfen gecerli bir skor girin (orn. 7 ve 5)", text_color="#e74c3c")
            return

        secilen_hafta_str = self.hafta_secim_opt.get()
        hafta_no = secilen_hafta_str.split(".")[0].strip()
        tarih_str = self.tarih_ent.get().strip()
        if not tarih_str:
            tarih_str = datetime.now().strftime("%d.%m.%Y")

        lokasyon_str = self.lokasyon_ent.get().strip() or DEFAULT_LOKASYON
        gun_str = self.gun_ent.get().strip() or DEFAULT_GUN
        saat_str = self.saat_ent.get().strip() or DEFAULT_SAAT

        self.maclar[hafta_no] = {
            "oynandi": True,
            "skor_girildi": True,
            "tarih": tarih_str,
            "lokasyon": lokasyon_str,
            "gun": gun_str,
            "saat": saat_str,
            "skor1": skor1,
            "skor2": skor2,
            "takim1": [{"isim": p["isim"], "mevki": p["mevki"]} for p in self.takim1],
            "takim2": [{"isim": p["isim"], "mevki": p["mevki"]} for p in self.takim2]
        }
        self.maclari_kaydet()

        for p in self.oyuncular:
            t1_de = any(k["isim"] == p["isim"] for k in self.takim1)
            t2_de = any(k["isim"] == p["isim"] for k in self.takim2)
            
            if t1_de or t2_de:
                p["gelmedigi_hafta"] = 0
                p["mac"] = p.get("mac", 0) + 1
                
                if skor1 > skor2:
                    if t1_de:
                        p["ek_puan"] = round(p.get("ek_puan", 0.0) + 0.2, 2)
                        p["galibiyet"] = p.get("galibiyet", 0) + 1
                    else:
                        p["ek_puan"] = round(p.get("ek_puan", 0.0) - 0.2, 2)
                        p["maglubiyet"] = p.get("maglubiyet", 0) + 1
                elif skor2 > skor1:
                    if t2_de:
                        p["ek_puan"] = round(p.get("ek_puan", 0.0) + 0.2, 2)
                        p["galibiyet"] = p.get("galibiyet", 0) + 1
                    else:
                        p["ek_puan"] = round(p.get("ek_puan", 0.0) - 0.2, 2)
                        p["maglubiyet"] = p.get("maglubiyet", 0) + 1
                else:
                    p["beraberlik"] = p.get("beraberlik", 0) + 1
            else:
                p["gelmedigi_hafta"] = p.get("gelmedigi_hafta", 0) + 1

        self.verileri_kaydet()
        self.oyuncu_listesini_ciz()
        self.istatistik_tablosunu_ciz()
        self.kimya_tablosunu_ciz()
        self.sezon_kartlarini_ciz()
        
        sonraki_hafta = int(hafta_no) + 1
        if sonraki_hafta <= 52:
            self.hafta_secim_opt.set(f"{sonraki_hafta}. Hafta")
        
        self.t1_skor_ent.delete(0, "end")
        self.t2_skor_ent.delete(0, "end")
        self.kadro_kaydet_btn.configure(state="disabled")
        self.mac_kaydet_btn.configure(state="disabled")
        
        fark = abs(sum(self.net_puan(p) for p in self.takim1) - sum(self.net_puan(p) for p in self.takim2))
        self.kadro_tablosu_ciz(getattr(self, 'son_varyasyon_no', 1), getattr(self, 'toplam_varyasyon_sayisi', 1), fark)
        
        self.secili_sayisi_label.configure(text=f"{hafta_no}. Hafta maci ve istatistikler basariyla islendi!", text_color="#2ecc71")

    def hafta_sifirla(self, hafta_str):
        cevap = messagebox.askyesno("Onay", f"{hafta_str}. haftanin kadro ve mac kayitlari sifirlanacak. Emin misiniz?")
        if cevap:
            if hafta_str in self.maclar:
                self.maclar[hafta_str] = {
                    "oynandi": False,
                    "skor_girildi": False,
                    "tarih": "",
                    "lokasyon": "",
                    "gun": "",
                    "saat": "",
                    "skor1": "",
                    "skor2": "",
                    "takim1": [],
                    "takim2": []
                }
                self.maclari_kaydet()
                self.sezon_kartlarini_ciz()
                secilen_aktif = self.hafta_secim_opt.get().split(".")[0].strip()
                if secilen_aktif == hafta_str:
                    self.hafta_degisti(f"{hafta_str}. Hafta")

    def istatistik_sekmesi_olustur(self):
        for w in self.tab_istatistik.winfo_children():
            w.destroy()

        ust_bilgi = ctk.CTkFrame(self.tab_istatistik, fg_color="transparent")
        ust_bilgi.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(ust_bilgi, text="OYUNCU PERFORMANS & DEVAMLILIK ISTATISTIKLERI (Basliklara tiklayarak siralayabilirsiniz)", font=(FONT_FAMILY, 14, "bold"), text_color="#3498db").pack(side="left")
        
        btn_ust_sifirla = ctk.CTkButton(ust_bilgi, text="Tum Istatistikleri Sifirla", command=self.onayli_istatistik_sifirla, fg_color="#c0392b", hover_color="#962d22", font=(FONT_FAMILY, 11, "bold"), height=28)
        btn_ust_sifirla.pack(side="right", padx=10)

        ctk.CTkLabel(ust_bilgi, text=f"Kayitli Oyuncu: {len(self.oyuncular)}", font=(FONT_FAMILY, 12)).pack(side="right", padx=10)

        self.baslik_kutusu = ctk.CTkFrame(self.tab_istatistik, fg_color="#2c3e50")
        self.baslik_kutusu.pack(fill="x", padx=10, pady=5)

        self.baslik_butonlarini_olustur()

        self.istatistik_scroll = ctk.CTkScrollableFrame(self.tab_istatistik)
        self.istatistik_scroll.pack(fill="both", expand=True, padx=10, pady=5)

        self.istatistik_tablosunu_ciz()

    def baslik_butonlarini_olustur(self):
        for w in self.baslik_kutusu.winfo_children():
            w.destroy()

        kolonlar = [
            ("sira", "Sira", 40, "#bdc3c7"),
            ("isim", "Oyuncu Ismi", 160, "#ecf0f1"),
            ("mevki", "Mevki", 95, "#ecf0f1"),
            ("toplam_puan", "Toplam Puan", 95, "#f1c40f"),
            ("mac", "Mac (M)", 75, "#3498db"),
            ("galibiyet", "Galibiyet (G)", 95, "#2ecc71"),
            ("beraberlik", "Beraberlik (B)", 95, "#f1c40f"),
            ("maglubiyet", "Maglubiyet (Mg)", 105, "#e74c3c"),
            ("yuzde", "Kazanma (%)", 95, "#ecf0f1"),
            ("gelmedigi_hafta", "Ust Uste Gelmedigi", 130, "#e67e22"),
            ("form", "Form (Son 10)", 260, "#1abc9c")
        ]

        for col_id, col_name, col_width, col_text_color in kolonlar:
            ok = ""
            if self.sort_column == col_id:
                ok = " ▲" if not self.sort_reverse else " ▼"

            btn_text = f"{col_name}{ok}"
            btn = ctk.CTkButton(
                self.baslik_kutusu,
                text=btn_text,
                width=col_width,
                font=(FONT_FAMILY, 11, "bold"),
                text_color=col_text_color,
                fg_color="#34495e" if self.sort_column == col_id else "transparent",
                hover_color="#1abc9c",
                command=lambda cid=col_id: self.istatistik_sirala(cid)
            )
            btn.pack(side="left", padx=2, pady=3)

    def istatistik_sirala(self, column_id):
        if self.sort_column == column_id:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column_id
            if column_id in ["isim", "mevki", "sira"]:
                self.sort_reverse = False
            else:
                self.sort_reverse = True

        self.baslik_butonlarini_olustur()
        self.istatistik_tablosunu_ciz()

    def istatistik_tablosunu_ciz(self):
        for w in self.istatistik_scroll.winfo_children():
            w.destroy()

        if self.sort_column == "sira":
            key_func = lambda x: self.net_puan(x)
        elif self.sort_column == "isim":
            key_func = lambda x: tr_sort_key(x.get("isim", ""))
        elif self.sort_column == "mevki":
            mevki_sira = {"Kale": 1, "Defans": 2, "Ortasaha": 3, "Forvet": 4}
            key_func = lambda x: mevki_sira.get(x.get("mevki", ""), 5)
        elif self.sort_column == "toplam_puan":
            key_func = lambda x: self.net_puan(x)
        elif self.sort_column == "mac":
            key_func = lambda x: x.get("mac", 0)
        elif self.sort_column == "galibiyet":
            key_func = lambda x: x.get("galibiyet", 0)
        elif self.sort_column == "beraberlik":
            key_func = lambda x: x.get("beraberlik", 0)
        elif self.sort_column == "maglubiyet":
            key_func = lambda x: x.get("maglubiyet", 0)
        elif self.sort_column == "yuzde":
            key_func = lambda x: self.galibiyet_orani(x)
        elif self.sort_column == "gelmedigi_hafta":
            key_func = lambda x: x.get("gelmedigi_hafta", 0)
        elif self.sort_column == "form":
            key_func = lambda x: self.form_skoru_hesapla(x.get("isim", ""))
        else:
            key_func = lambda x: self.net_puan(x)

        sirali_oyuncular = sorted(self.oyuncular, key=key_func, reverse=self.sort_reverse)

        for idx, p in enumerate(sirali_oyuncular, 1):
            row = ctk.CTkFrame(self.istatistik_scroll, fg_color="#1e272e" if idx % 2 == 0 else "#242d38")
            row.pack(fill="x", pady=2)

            m = p.get("mac", 0)
            g = p.get("galibiyet", 0)
            b = p.get("beraberlik", 0)
            mg = p.get("maglubiyet", 0)
            yuzde = self.galibiyet_orani(p)
            gelmedigi = p.get("gelmedigi_hafta", 0)

            ctk.CTkLabel(row, text=str(idx), width=40, font=(FONT_FAMILY, 11, "bold")).pack(side="left", padx=2, pady=3)
            ctk.CTkLabel(row, text=p["isim"], width=160, anchor="w", font=(FONT_FAMILY, 11, "bold")).pack(side="left", padx=2)
            ctk.CTkLabel(row, text=p["mevki"], width=95, font=(FONT_FAMILY, 11)).pack(side="left", padx=2)
            ctk.CTkLabel(row, text=f"{self.net_puan(p):.1f}", width=95, font=(FONT_FAMILY, 11, "bold"), text_color="#f1c40f").pack(side="left", padx=2)
            ctk.CTkLabel(row, text=str(m), width=75, font=(FONT_FAMILY, 11, "bold"), text_color="#3498db").pack(side="left", padx=2)
            ctk.CTkLabel(row, text=str(g), width=95, font=(FONT_FAMILY, 11), text_color="#2ecc71").pack(side="left", padx=2)
            ctk.CTkLabel(row, text=str(b), width=95, font=(FONT_FAMILY, 11), text_color="#f1c40f").pack(side="left", padx=2)
            ctk.CTkLabel(row, text=str(mg), width=105, font=(FONT_FAMILY, 11), text_color="#e74c3c").pack(side="left", padx=2)
            ctk.CTkLabel(row, text=f"%{yuzde}", width=95, font=(FONT_FAMILY, 11, "bold")).pack(side="left", padx=2)
            
            gelmedi_renk = "#e74c3c" if gelmedigi >= 3 else ("#e67e22" if gelmedigi > 0 else "#2ecc71")
            gelmedi_txt = f"{gelmedigi} Hafta" if gelmedigi > 0 else "Aktif (Geldi)"
            ctk.CTkLabel(row, text=gelmedi_txt, width=130, font=(FONT_FAMILY, 11, "bold"), text_color=gelmedi_renk).pack(side="left", padx=2)

            form_frame = ctk.CTkFrame(row, fg_color="transparent", width=260)
            form_frame.pack(side="left", padx=2)
            
            son_10 = self.form_durumu_al(p["isim"])
            if not son_10:
                ctk.CTkLabel(form_frame, text="Henüz maç verisi yok", font=(FONT_FAMILY, 10), text_color="#7f8c8d").pack(padx=20)
            else:
                for res in son_10:
                    if res == "G":
                        bg_c = "#27ae60"
                    elif res == "B":
                        bg_c = "#f39c12"
                    else:
                        bg_c = "#e74c3c"
                    
                    b_box = ctk.CTkFrame(form_frame, fg_color=bg_c, corner_radius=3, width=20, height=20)
                    b_box.pack(side="left", padx=1.5)
                    b_box.pack_propagate(False)
                    ctk.CTkLabel(b_box, text=res, font=(FONT_FAMILY, 9, "bold"), text_color="white").pack(expand=True)

    def kimya_sekmesi_olustur(self):
        for w in self.tab_kimya.winfo_children():
            w.destroy()

        ust_bilgi = ctk.CTkFrame(self.tab_kimya, fg_color="transparent")
        ust_bilgi.pack(fill="x", padx=10, pady=6)

        ctk.CTkLabel(ust_bilgi, text="OYUNCU KİMYA & BİRLİKTE KAZANMA ANALİZİ", font=(FONT_FAMILY, 15, "bold"), text_color="#e67e22").pack(side="left")

        secim_frame = ctk.CTkFrame(ust_bilgi, fg_color="transparent")
        secim_frame.pack(side="right")
        
        ctk.CTkLabel(secim_frame, text="Oyuncu Seç:", font=(FONT_FAMILY, 11, "bold")).pack(side="left", padx=4)
        
        oyuncu_isimleri = ["--- Tüm Ligin En İyileri ---"] + [p["isim"] for p in sorted(self.oyuncular, key=lambda x: tr_sort_key(x["isim"]))]
        self.kimya_oyuncu_opt = ctk.CTkOptionMenu(secim_frame, values=oyuncu_isimleri, width=210, font=(FONT_FAMILY, 11), command=lambda _: self.kimya_tablosunu_ciz())
        self.kimya_oyuncu_opt.set("--- Tüm Ligin En İyileri ---")
        self.kimya_oyuncu_opt.pack(side="left", padx=4)

        # Tablo Başlıkları
        self.kimya_baslik = ctk.CTkFrame(self.tab_kimya, fg_color="#2c3e50")
        self.kimya_baslik.pack(fill="x", padx=10, pady=(6, 2))

        ctk.CTkLabel(self.kimya_baslik, text="Sıra", width=45, font=(FONT_FAMILY, 11, "bold"), text_color="#bdc3c7").pack(side="left", padx=4)
        ctk.CTkLabel(self.kimya_baslik, text="İkili / Ortaklık", width=300, anchor="w", font=(FONT_FAMILY, 11, "bold"), text_color="#ecf0f1").pack(side="left", padx=6)
        ctk.CTkLabel(self.kimya_baslik, text="Birlikte Maç", width=120, font=(FONT_FAMILY, 11, "bold"), text_color="#3498db").pack(side="left", padx=4)
        ctk.CTkLabel(self.kimya_baslik, text="Galibiyet (G)", width=120, font=(FONT_FAMILY, 11, "bold"), text_color="#2ecc71").pack(side="left", padx=4)
        ctk.CTkLabel(self.kimya_baslik, text="Beraberlik (B)", width=120, font=(FONT_FAMILY, 11, "bold"), text_color="#f1c40f").pack(side="left", padx=4)
        ctk.CTkLabel(self.kimya_baslik, text="Mağlubiyet (M)", width=120, font=(FONT_FAMILY, 11, "bold"), text_color="#e74c3c").pack(side="left", padx=4)
        ctk.CTkLabel(self.kimya_baslik, text="Kazanma / Kimya (%)", width=160, font=(FONT_FAMILY, 11, "bold"), text_color="#1abc9c").pack(side="left", padx=4)
        ctk.CTkLabel(self.kimya_baslik, text="Sinerji Durumu", width=180, font=(FONT_FAMILY, 11, "bold"), text_color="#e67e22").pack(side="left", padx=4)

        self.kimya_scroll = ctk.CTkScrollableFrame(self.tab_kimya)
        self.kimya_scroll.pack(fill="both", expand=True, padx=10, pady=5)

        self.kimya_tablosunu_ciz()

    def kimya_oyuncu_listesini_guncelle(self):
        if hasattr(self, "kimya_oyuncu_opt"):
            oyuncu_isimleri = ["--- Tüm Ligin En İyileri ---"] + [p["isim"] for p in sorted(self.oyuncular, key=lambda x: tr_sort_key(x["isim"]))]
            self.kimya_oyuncu_opt.configure(values=oyuncu_isimleri)

    def kimya_tablosunu_ciz(self):
        for w in self.kimya_scroll.winfo_children():
            w.destroy()

        secilen_oyuncu = self.kimya_oyuncu_opt.get() if hasattr(self, "kimya_oyuncu_opt") else "--- Tüm Ligin En İyileri ---"
        tum_ciftler = self.kimya_istatistiklerini_hesapla()

        if not tum_ciftler:
            ctk.CTkLabel(self.kimya_scroll, text="Henüz tamamlanmış maç kaydı bulunmuyor. Maç sonuçları girildikçe kimya analizleri burada listelenecektir.", font=(FONT_FAMILY, 13), text_color="#bdc3c7").pack(pady=40)
            return

        satirlar = []
        for (p1, p2), veri in tum_ciftler.items():
            if secilen_oyuncu != "--- Tüm Ligin En İyileri ---" and secilen_oyuncu not in (p1, p2):
                continue
            
            m = veri["mac"]
            g = veri["galibiyet"]
            b = veri["beraberlik"]
            mg = veri["maglubiyet"]
            
            if m > 0:
                yuzde = int(((g + (b * 0.5)) / m) * 100)
            else:
                yuzde = 0
            
            satirlar.append({
                "p1": p1, "p2": p2,
                "mac": m, "g": g, "b": b, "mg": mg,
                "yuzde": yuzde
            })

        # Çok oynayan ve yüksek kazananları öne alacak şekilde sırala
        satirlar.sort(key=lambda x: (x["yuzde"], x["mac"], x["g"]), reverse=True)

        if not satirlar:
            ctk.CTkLabel(self.kimya_scroll, text=f"'{secilen_oyuncu}' için henüz birlikte oynanmış maç kaydı bulunamadı.", font=(FONT_FAMILY, 13), text_color="#bdc3c7").pack(pady=40)
            return

        for idx, row_data in enumerate(satirlar, 1):
            row = ctk.CTkFrame(self.kimya_scroll, fg_color="#1e272e" if idx % 2 == 0 else "#242d38")
            row.pack(fill="x", pady=2)

            if secilen_oyuncu != "--- Tüm Ligin En İyileri ---":
                partner = row_data["p2"] if row_data["p1"] == secilen_oyuncu else row_data["p1"]
                isim_str = f"{secilen_oyuncu}  +  {partner}"
            else:
                isim_str = f"{row_data['p1']}  +  {row_data['p2']}"

            yuzde = row_data["yuzde"]
            if yuzde >= 70 and row_data["mac"] >= 2:
                sinerji_txt = "🔥 Mükemmel Uyum"
                sinerji_color = "#2ecc71"
            elif yuzde >= 50:
                sinerji_txt = "⚡ İyi Denge"
                sinerji_color = "#f1c40f"
            else:
                sinerji_txt = "❄️ Uyumsuz İkili"
                sinerji_color = "#e74c3c"

            ctk.CTkLabel(row, text=str(idx), width=45, font=(FONT_FAMILY, 11, "bold")).pack(side="left", padx=4, pady=3)
            ctk.CTkLabel(row, text=isim_str, width=300, anchor="w", font=(FONT_FAMILY, 11, "bold")).pack(side="left", padx=6)
            ctk.CTkLabel(row, text=str(row_data["mac"]), width=120, font=(FONT_FAMILY, 11, "bold"), text_color="#3498db").pack(side="left", padx=4)
            ctk.CTkLabel(row, text=str(row_data["g"]), width=120, font=(FONT_FAMILY, 11), text_color="#2ecc71").pack(side="left", padx=4)
            ctk.CTkLabel(row, text=str(row_data["b"]), width=120, font=(FONT_FAMILY, 11), text_color="#f1c40f").pack(side="left", padx=4)
            ctk.CTkLabel(row, text=str(row_data["mg"]), width=120, font=(FONT_FAMILY, 11), text_color="#e74c3c").pack(side="left", padx=4)
            ctk.CTkLabel(row, text=f"%{yuzde}", width=160, font=(FONT_FAMILY, 11, "bold"), text_color="#1abc9c").pack(side="left", padx=4)
            ctk.CTkLabel(row, text=sinerji_txt, width=180, font=(FONT_FAMILY, 11, "bold"), text_color=sinerji_color).pack(side="left", padx=4)

    def sezon_sekmesi_olustur(self):
        for w in self.tab_sezon.winfo_children():
            w.destroy()

        ust_bilgi = ctk.CTkFrame(self.tab_sezon, fg_color="transparent")
        ust_bilgi.pack(fill="x", padx=10, pady=5)
        
        oynanan_sayisi = sum(1 for m in self.maclar.values() if m.get("oynandi", False) and m.get("skor_girildi", False))
        ctk.CTkLabel(ust_bilgi, text="SEZON FIKSTURU VE HAFTALIK MAC SONUCLARI (52 HAFTA)", font=(FONT_FAMILY, 15, "bold"), text_color="#f39c12").pack(side="left")
        ctk.CTkLabel(ust_bilgi, text=f"Tamamlanan Mac: {oynanan_sayisi} / 52", font=(FONT_FAMILY, 12)).pack(side="right")

        self.sezon_scroll = ctk.CTkScrollableFrame(self.tab_sezon)
        self.sezon_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        self.sezon_kartlarini_ciz()

    def sezon_kartlarini_ciz(self):
        for w in self.sezon_scroll.winfo_children():
            w.destroy()

        for i in range(1, 53):
            hafta_str = str(i)
            mac = self.maclar[hafta_str]
            idx = i - 1
            col = idx % 3
            row = idx // 3

            skor_girildi = mac.get("skor_girildi", False)
            kadro_var = len(mac.get("takim1", [])) > 0

            border_renk = "#2ecc71" if skor_girildi else ("#3498db" if kadro_var else "#4b6584")

            kart = ctk.CTkFrame(self.sezon_scroll, fg_color="#222f3e", border_width=1, border_color=border_renk, width=440)
            kart.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")

            baslik_renk = "#27ae60" if skor_girildi else ("#2980b9" if kadro_var else "#4b6584")
            baslik_bar = ctk.CTkFrame(kart, fg_color=baslik_renk, corner_radius=0)
            baslik_bar.pack(fill="x")
            
            durum_txt = " (Oynandi)" if skor_girildi else (" (Kadro Belirlendi)" if kadro_var else " (Bekliyor)")
            ctk.CTkLabel(baslik_bar, text=f"{i}. HAFTA{durum_txt}", font=(FONT_FAMILY, 14, "bold"), text_color="white").pack(side="left", padx=10, pady=4)

            ctk.CTkButton(baslik_bar, text="Sifirla", width=55, height=22, fg_color="#c0392b", hover_color="#962d22", font=(FONT_FAMILY, 10, "bold"),
                          command=lambda h=hafta_str: self.hafta_sifirla(h)).pack(side="right", padx=6, pady=2)

            tarih_str = mac.get("tarih", "")
            lokasyon_str = mac.get("lokasyon", "") or DEFAULT_LOKASYON
            gun_str = mac.get("gun", "") or DEFAULT_GUN
            saat_str = mac.get("saat", "") or DEFAULT_SAAT
            
            detay_parcalar = []
            if tarih_str: detay_parcalar.append(tarih_str)
            if gun_str: detay_parcalar.append(gun_str)
            if saat_str: detay_parcalar.append(saat_str)
            if lokasyon_str: detay_parcalar.append(f"({lokasyon_str})")
            
            bilgi_metni = "  •  ".join(detay_parcalar) if detay_parcalar else "- - . - - . - - - -"
            ctk.CTkLabel(kart, text=bilgi_metni, font=(FONT_FAMILY, 11), text_color="#bdc3c7").pack(pady=2)

            skor_bar = ctk.CTkFrame(kart, fg_color="#17202a", corner_radius=6)
            skor_bar.pack(fill="x", padx=6, pady=4)

            if skor_girildi:
                s1, s2 = int(mac["skor1"]), int(mac["skor2"])
                t1_renk = "#2ecc71" if s1 > s2 else ("#e74c3c" if s1 < s2 else "#f1c40f")
                t2_renk = "#2ecc71" if s2 > s1 else ("#e74c3c" if s2 < s1 else "#f1c40f")
                
                ctk.CTkLabel(skor_bar, text="TURUNCU", width=125, font=(FONT_FAMILY, 12, "bold"), text_color=t1_renk).pack(side="left", padx=4)
                
                skor_kutusu = ctk.CTkFrame(skor_bar, fg_color="#2c3e50", corner_radius=4)
                skor_kutusu.pack(side="left", expand=True, padx=4, pady=3)
                ctk.CTkLabel(skor_kutusu, text=f"SKOR:  {s1} - {s2}", font=(FONT_FAMILY, 13, "bold"), text_color="#f1c40f").pack(padx=10, pady=2)
                
                ctk.CTkLabel(skor_bar, text="SIYAH", width=125, font=(FONT_FAMILY, 12, "bold"), text_color=t2_renk).pack(side="right", padx=4)
            else:
                ctk.CTkLabel(skor_bar, text="TURUNCU", width=125, font=(FONT_FAMILY, 12, "bold"), text_color="#7f8c8d").pack(side="left", padx=4)
                
                skor_kutusu = ctk.CTkFrame(skor_bar, fg_color="#2c3e50", corner_radius=4)
                skor_kutusu.pack(side="left", expand=True, padx=4, pady=3)
                ctk.CTkLabel(skor_kutusu, text="SKOR:  — - —", font=(FONT_FAMILY, 12, "bold"), text_color="#7f8c8d").pack(padx=8, pady=2)
                
                ctk.CTkLabel(skor_bar, text="SIYAH", width=125, font=(FONT_FAMILY, 12, "bold"), text_color="#7f8c8d").pack(side="right", padx=4)

            liste_kutusu = ctk.CTkFrame(kart, fg_color="#1e272e")
            liste_kutusu.pack(fill="both", expand=True, padx=6, pady=5)

            t1_kolon = ctk.CTkFrame(liste_kutusu, fg_color="transparent")
            t1_kolon.pack(side="left", fill="both", expand=True, padx=4, pady=3)

            t2_kolon = ctk.CTkFrame(liste_kutusu, fg_color="transparent")
            t2_kolon.pack(side="right", fill="both", expand=True, padx=4, pady=3)

            if kadro_var:
                for p in mac.get("takim1", []):
                    ctk.CTkLabel(t1_kolon, text=f"{p['isim']} ({p['mevki']})", font=(FONT_FAMILY, 12, "bold"), anchor="w").pack(fill="x", padx=4, pady=2)
                for p in mac.get("takim2", []):
                    ctk.CTkLabel(t2_kolon, text=f"{p['isim']} ({p['mevki']})", font=(FONT_FAMILY, 12, "bold"), anchor="w").pack(fill="x", padx=4, pady=2)
            else:
                for _ in range(7):
                    ctk.CTkLabel(t1_kolon, text="—", font=(FONT_FAMILY, 12), text_color="#576574").pack(pady=2)
                    ctk.CTkLabel(t2_kolon, text="—", font=(FONT_FAMILY, 12), text_color="#576574").pack(pady=2)

    def takim_degistir(self, kimden_takim, kime_takim, secilen_isim):
        if not secilen_isim or secilen_isim == "Oyuncu Sec":
            return
        bulunan = None
        for p in kimden_takim:
            if p.get("isim") == secilen_isim:
                bulunan = p
                break
        if bulunan:
            kimden_takim.remove(bulunan)
            kime_takim.append(bulunan)
            self.kadro_tablosu_ciz(getattr(self, 'son_varyasyon_no', 1), getattr(self, 'toplam_varyasyon_sayisi', 1), getattr(self, 'son_fark', 0.0))

    def kadro_tablosu_ciz(self, varyasyon_no=1, toplam=1, fark=0.0):
        self.son_varyasyon_no = varyasyon_no
        self.toplam_varyasyon_sayisi = toplam
        self.son_fark = fark

        for widget in self.sonuc_frame.winfo_children():
            widget.destroy()

        secilen_hafta = tr_temizle(self.hafta_secim_opt.get())
        lok_val = tr_temizle(self.lokasyon_ent.get().strip() or DEFAULT_LOKASYON)
        gun_val = tr_temizle(self.gun_ent.get().strip() or DEFAULT_GUN)
        saat_val = self.saat_ent.get().strip() or DEFAULT_SAAT
        
        detay_str = f"{secilen_hafta}  |  {gun_val}  |  Saat: {saat_val}  |  Saha: {lok_val}"

        bilgi_bar = ctk.CTkFrame(self.sonuc_frame, fg_color="#17202a", corner_radius=8)
        bilgi_bar.pack(fill="x", padx=6, pady=(4, 6))
        
        sol_bilgi_frame = ctk.CTkFrame(bilgi_bar, fg_color="transparent")
        sol_bilgi_frame.pack(side="left", padx=12, pady=6)

        ctk.CTkLabel(sol_bilgi_frame, text=f"Varyasyon: {varyasyon_no} / {toplam}", font=(FONT_FAMILY, 13, "bold"), text_color="#3498db").pack(side="left", padx=(0, 15))
        ctk.CTkLabel(sol_bilgi_frame, text=detay_str, font=(FONT_FAMILY, 14, "bold"), text_color="#e67e22").pack(side="left", padx=5)
        
        fark_badge = ctk.CTkFrame(bilgi_bar, fg_color="#27ae60" if fark < 0.5 else "#e67e22", corner_radius=6)
        fark_badge.pack(side="right", padx=12, pady=6)
        ctk.CTkLabel(fark_badge, text=f"Puan Farki: {fark:.2f}", font=(FONT_FAMILY, 13, "bold"), text_color="white").pack(padx=10, pady=3)

        govde = ctk.CTkFrame(self.sonuc_frame, fg_color="transparent")
        govde.pack(fill="both", expand=True)

        t1_puan = sum(self.net_puan(p) for p in self.takim1)
        t2_puan = sum(self.net_puan(p) for p in self.takim2)

        mevki_renkleri = {
            "Kale": "#e74c3c",
            "Defans": "#3498db",
            "Ortasaha": "#2ecc71",
            "Forvet": "#f39c12"
        }
        sira = {"Kale": 1, "Defans": 2, "Ortasaha": 3, "Forvet": 4}

        # 1. TAKIM (TURUNCU TAKIM KARTI)
        t1_kart = ctk.CTkFrame(govde, fg_color="#1c2833", border_width=2, border_color="#e67e22", corner_radius=10)
        t1_kart.pack(side="left", fill="both", expand=True, padx=4, pady=2)

        t1_hdr = ctk.CTkFrame(t1_kart, fg_color="#e67e22", corner_radius=8)
        t1_hdr.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(t1_hdr, text="TURUNCU TAKIM", font=(FONT_FAMILY, 13, "bold"), text_color="white").pack(side="left", padx=8, pady=5)
        
        t1_puan_box = ctk.CTkFrame(t1_hdr, fg_color="#1c2833", corner_radius=6)
        t1_puan_box.pack(side="right", padx=8, pady=3)
        ctk.CTkLabel(t1_puan_box, text=f"{t1_puan:.1f} P", font=(FONT_FAMILY, 12, "bold"), text_color="#f1c40f").pack(padx=8, pady=2)

        t1_transfer_bar = ctk.CTkFrame(t1_kart, fg_color="#273746", corner_radius=6)
        t1_transfer_bar.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(t1_transfer_bar, text="Transfer Et:", font=(FONT_FAMILY, 10, "bold"), text_color="#f1c40f").pack(side="left", padx=5)
        
        t1_isimler = [p.get("isim") for p in self.takim1]
        t1_secim_var = ctk.StringVar(value=t1_isimler[0] if t1_isimler else "Oyuncu Sec")
        t1_opt = ctk.CTkOptionMenu(t1_transfer_bar, values=t1_isimler if t1_isimler else ["Oyuncu Sec"], variable=t1_secim_var, width=130, height=24, font=(FONT_FAMILY, 10))
        t1_opt.pack(side="left", padx=3)
        
        ctk.CTkButton(t1_transfer_bar, text="Siyah'a Gonder ➔", width=110, height=24, fg_color="#c0392b", hover_color="#962d22", font=(FONT_FAMILY, 10, "bold"),
                      command=lambda: self.takim_degistir(self.takim1, self.takim2, t1_secim_var.get())).pack(side="left", padx=3)

        t1_liste = ctk.CTkFrame(t1_kart, fg_color="transparent")
        t1_liste.pack(fill="x", padx=5, pady=2)

        for p in sorted(self.takim1, key=lambda x: sira.get(x["mevki"], 5)):
            p_row = ctk.CTkFrame(t1_liste, fg_color="#273746", corner_radius=6)
            p_row.pack(fill="x", pady=1, padx=1)

            m_badge = ctk.CTkFrame(p_row, fg_color=mevki_renkleri.get(p["mevki"], "#7f8c8d"), corner_radius=4, width=50)
            m_badge.pack(side="left", padx=4, pady=3)
            ctk.CTkLabel(m_badge, text=tr_temizle(p["mevki"][:3].upper()), font=(FONT_FAMILY, 10, "bold"), text_color="white").pack(padx=3, pady=1)

            ctk.CTkLabel(p_row, text=p["isim"], font=(FONT_FAMILY, 11, "bold"), anchor="w").pack(side="left", padx=6, expand=True, fill="x")
            ctk.CTkLabel(p_row, text=f"{self.net_puan(p):.1f} P", font=(FONT_FAMILY, 11, "bold"), text_color="#f1c40f").pack(side="right", padx=8)

        saha1_frame = ctk.CTkFrame(t1_kart, fg_color="transparent")
        saha1_frame.pack(fill="both", expand=True, padx=4, pady=4)
        self.ciz_3d_saha(saha1_frame, self.takim1, forma_rengi="#e67e22")

        # 2. TAKIM (SİYAH TAKIM KARTI)
        t2_kart = ctk.CTkFrame(govde, fg_color="#1c2833", border_width=2, border_color="#5d6d7e", corner_radius=10)
        t2_kart.pack(side="right", fill="both", expand=True, padx=4, pady=2)

        t2_hdr = ctk.CTkFrame(t2_kart, fg_color="#34495e", corner_radius=8)
        t2_hdr.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(t2_hdr, text="SIYAH TAKIM", font=(FONT_FAMILY, 13, "bold"), text_color="white").pack(side="left", padx=8, pady=5)
        
        t2_puan_box = ctk.CTkFrame(t2_hdr, fg_color="#1c2833", corner_radius=6)
        t2_puan_box.pack(side="right", padx=8, pady=3)
        ctk.CTkLabel(t2_puan_box, text=f"{t2_puan:.1f} P", font=(FONT_FAMILY, 12, "bold"), text_color="#ecf0f1").pack(padx=8, pady=2)

        t2_transfer_bar = ctk.CTkFrame(t2_kart, fg_color="#273746", corner_radius=6)
        t2_transfer_bar.pack(fill="x", padx=5, pady=3)
        ctk.CTkButton(t2_transfer_bar, text="⬅ Turuncu'ya Gonder", width=125, height=24, fg_color="#2980b9", hover_color="#1f618d", font=(FONT_FAMILY, 10, "bold"),
                      command=lambda: self.takim_degistir(self.takim2, self.takim1, t2_secim_var.get())).pack(side="left", padx=3)
        
        t2_isimler = [p.get("isim") for p in self.takim2]
        t2_secim_var = ctk.StringVar(value=t2_isimler[0] if t2_isimler else "Oyuncu Sec")
        t2_opt = ctk.CTkOptionMenu(t2_transfer_bar, values=t2_isimler if t2_isimler else ["Oyuncu Sec"], variable=t2_secim_var, width=130, height=24, font=(FONT_FAMILY, 10))
        t2_opt.pack(side="left", padx=3)
        ctk.CTkLabel(t2_transfer_bar, text=":Transfer Et", font=(FONT_FAMILY, 10, "bold"), text_color="#ecf0f1").pack(side="left", padx=5)

        t2_liste = ctk.CTkFrame(t2_kart, fg_color="transparent")
        t2_liste.pack(fill="x", padx=5, pady=2)

        for p in sorted(self.takim2, key=lambda x: sira.get(x["mevki"], 5)):
            p_row = ctk.CTkFrame(t2_liste, fg_color="#273746", corner_radius=6)
            p_row.pack(fill="x", pady=1, padx=1)

            m_badge = ctk.CTkFrame(p_row, fg_color=mevki_renkleri.get(p["mevki"], "#7f8c8d"), corner_radius=4, width=50)
            m_badge.pack(side="left", padx=4, pady=3)
            ctk.CTkLabel(m_badge, text=tr_temizle(p["mevki"][:3].upper()), font=(FONT_FAMILY, 10, "bold"), text_color="white").pack(padx=3, pady=1)

            ctk.CTkLabel(p_row, text=p["isim"], font=(FONT_FAMILY, 11, "bold"), anchor="w").pack(side="left", padx=6, expand=True, fill="x")
            ctk.CTkLabel(p_row, text=f"{self.net_puan(p):.1f} P", font=(FONT_FAMILY, 11, "bold"), text_color="#ecf0f1").pack(side="right", padx=8)

        saha2_frame = ctk.CTkFrame(t2_kart, fg_color="transparent")
        saha2_frame.pack(fill="both", expand=True, padx=4, pady=4)
        self.ciz_3d_saha(saha2_frame, self.takim2, forma_rengi="#2c3e50")

    def ciz_3d_saha(self, parent, takim_oyunculari, forma_rengi):
        canvas = tk.Canvas(parent, bg="#1c2833", highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        def cizim_islem(event=None):
            canvas.delete("all")
            total_w = canvas.winfo_width()
            total_h = canvas.winfo_height()
            
            if total_w <= 30 or total_h <= 30:
                total_w, total_h = 330, 230

            target_aspect = 1.45
            avail_w = total_w - 12
            avail_h = total_h - 10

            if avail_w / avail_h > target_aspect:
                pitch_h = avail_h
                pitch_w = pitch_h * target_aspect
            else:
                pitch_w = avail_w
                pitch_h = pitch_w / target_aspect

            offset_x = (total_w - pitch_w) / 2
            offset_y = (total_h - pitch_h) / 2

            side_inset = pitch_w * 0.08
            top_y = offset_y + pitch_h * 0.06
            bot_y = offset_y + pitch_h * 0.88
            depth_3d = pitch_h * 0.05

            p_top_left = (offset_x + side_inset, top_y)
            p_top_right = (offset_x + pitch_w - side_inset, top_y)
            p_bot_right = (offset_x + pitch_w - side_inset, bot_y)
            p_bot_left = (offset_x + side_inset, bot_y)

            canvas.create_polygon(
                p_bot_left[0], p_bot_left[1],
                p_bot_right[0], p_bot_right[1],
                p_bot_right[0], p_bot_right[1] + depth_3d,
                p_bot_left[0], p_bot_left[1] + depth_3d,
                fill="#0a3818", outline="#072811"
            )
            canvas.create_polygon(
                p_top_right[0], p_top_right[1],
                p_bot_right[0], p_bot_right[1],
                p_bot_right[0], p_bot_right[1] + depth_3d,
                p_top_right[0], p_top_right[1] + depth_3d,
                fill="#0d421d", outline="#072811"
            )
            canvas.create_polygon(
                p_top_left[0], p_top_left[1],
                p_top_right[0], p_top_right[1],
                p_bot_right[0], p_bot_right[1],
                p_bot_left[0], p_bot_left[1],
                fill="#157335", outline="#7bed9f", width=2
            )

            dilim_sayisi = 5
            for i in range(dilim_sayisi):
                if i % 2 == 1:
                    t_ratio1 = i / dilim_sayisi
                    t_ratio2 = (i + 1) / dilim_sayisi
                    y1 = top_y + (bot_y - top_y) * t_ratio1
                    y2 = top_y + (bot_y - top_y) * t_ratio2
                    canvas.create_polygon(offset_x + side_inset, y1, offset_x + pitch_w - side_inset, y1, offset_x + pitch_w - side_inset, y2, offset_x + side_inset, y2, fill="#19873e", outline="")

            def saha_xy(u, v):
                cur_y = top_y + (bot_y - top_y) * v
                cur_x_left = offset_x + side_inset
                cur_x_right = offset_x + pitch_w - side_inset
                cur_x = cur_x_left + (cur_x_right - cur_x_left) * u
                return cur_x, cur_y

            c_tl = saha_xy(0.03, 0.03)
            c_tr = saha_xy(0.97, 0.03)
            c_br = saha_xy(0.97, 0.97)
            c_bl = saha_xy(0.03, 0.97)
            canvas.create_polygon(c_tl[0], c_tl[1], c_tr[0], c_tr[1], c_br[0], c_br[1], c_bl[0], c_bl[1], fill="", outline="#ffffff", width=2)

            m_l = saha_xy(0.03, 0.52)
            m_r = saha_xy(0.97, 0.52)
            canvas.create_line(m_l[0], m_l[1], m_r[0], m_r[1], fill="#ffffff", width=2)

            cx, cy = saha_xy(0.5, 0.52)
            canvas.create_oval(cx - pitch_w*0.13, cy - pitch_h*0.05, cx + pitch_w*0.13, cy + pitch_h*0.05, outline="#ffffff", width=2)

            k1 = saha_xy(0.28, 0.03)
            k2 = saha_xy(0.72, 0.03)
            k3 = saha_xy(0.72, 0.20)
            k4 = saha_xy(0.28, 0.20)
            canvas.create_polygon(k1[0], k1[1], k2[0], k2[1], k3[0], k3[1], k4[0], k4[1], fill="", outline="#ffffff", width=2)

            a1 = saha_xy(0.28, 0.97)
            a2 = saha_xy(0.72, 0.97)
            a3 = saha_xy(0.72, 0.80)
            a4 = saha_xy(0.28, 0.80)
            canvas.create_polygon(a1[0], a1[1], a2[0], a2[1], a3[0], a3[1], a4[0], a4[1], fill="", outline="#ffffff", width=2)

            scale = max(1.0, pitch_w / 320)
            fw = 15 * scale
            fh = 15 * scale

            def ciz_forma(cx, cy, isim, numara, f_renk, kollar_beyaz=True):
                if kollar_beyaz:
                    canvas.create_polygon(cx - fw*0.6, cy - fh*0.4, cx - fw*1.0, cy - fh*0.05, cx - fw*0.7, cy + fh*0.35, cx - fw*0.4, cy + fh*0.05, fill="#ffffff", outline="#222222")
                    canvas.create_polygon(cx + fw*0.6, cy - fh*0.4, cx + fw*1.0, cy - fh*0.05, cx + fw*0.7, cy + fh*0.35, cx + fw*0.4, cy + fh*0.05, fill="#ffffff", outline="#222222")

                canvas.create_polygon(
                    cx - fw*0.6, cy - fh*0.4,
                    cx + fw*0.6, cy - fh*0.4,
                    cx + fw*0.5, cy + fh*0.5,
                    cx - fw*0.5, cy + fh*0.5,
                    fill=f_renk, outline="#111111"
                )
                canvas.create_polygon(cx - fw*0.25, cy - fh*0.4, cx + fw*0.25, cy - fh*0.4, cx, cy - fh*0.15, fill="#ffffff", outline="")
                canvas.create_text(cx, cy + 2, text=str(numara), fill="#ffffff", font=(FONT_FAMILY, int(9*scale), "bold"))

                isim_kisa = tr_temizle(isim.split()[0][:8])
                box_w = max(34 * scale, len(isim_kisa) * (5.5 * scale) + 10)
                box_h = 12 * scale
                bx1 = cx - box_w / 2
                by1 = cy + fh*0.5 + 2
                bx2 = cx + box_w / 2
                by2 = by1 + box_h

                canvas.create_rectangle(bx1, by1, bx2, by2, fill="#ffffff", outline="#000000")
                canvas.create_text(cx, (by1 + by2) / 2, text=isim_kisa, fill="#000000", font=(FONT_FAMILY, int(8*scale), "bold"))

            mevkiler = {"Kale": [], "Defans": [], "Ortasaha": [], "Forvet": []}
            for p in takim_oyunculari:
                mevkiler.setdefault(p.get("mevki", "Ortasaha"), []).append(p)

            hat_v_oranlari = {"Kale": 0.06, "Defans": 0.28, "Ortasaha": 0.54, "Forvet": 0.80}
            forma_no = 1

            for p in mevkiler.get("Kale", []):
                px, py = saha_xy(0.5, hat_v_oranlari["Kale"])
                ciz_forma(px, py, p["isim"], forma_no, f_renk="#2ecc71", kollar_beyaz=False)
                forma_no += 1

            def_list = mevkiler.get("Defans", [])
            for i, p in enumerate(def_list):
                u_pos = (i + 1) / (len(def_list) + 1)
                px, py = saha_xy(u_pos, hat_v_oranlari["Defans"])
                ciz_forma(px, py, p["isim"], forma_no, f_renk=forma_rengi, kollar_beyaz=True)
                forma_no += 1

            ort_list = mevkiler.get("Ortasaha", [])
            for i, p in enumerate(ort_list):
                u_pos = (i + 1) / (len(ort_list) + 1)
                px, py = saha_xy(u_pos, hat_v_oranlari["Ortasaha"])
                ciz_forma(px, py, p["isim"], forma_no, f_renk=forma_rengi, kollar_beyaz=True)
                forma_no += 1

            forv_list = mevkiler.get("Forvet", [])
            for i, p in enumerate(forv_list):
                u_pos = (i + 1) / (len(forv_list) + 1)
                px, py = saha_xy(u_pos, hat_v_oranlari["Forvet"])
                ciz_forma(px, py, p["isim"], forma_no, f_renk=forma_rengi, kollar_beyaz=True)
                forma_no += 1

        canvas.bind("<Configure>", cizim_islem)

if __name__ == "__main__":
    app = HaliSahaApp()
    app.mainloop()