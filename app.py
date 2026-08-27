import streamlit as st
import itertools
import json
import os
from datetime import datetime

# Sayfa Yapılandırması ve Özel CSS (Masaüstü Temasına Benzetme)
st.set_page_config(page_title="Halı Saha Yönetim Sistemi", page_icon="⚽", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #121212; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1f2937;
        border-radius: 6px;
        color: white;
        font-weight: bold;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important;
    }
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "oyuncular.json"
MACLAR_FILE = "maclar.json"
TAHMINLER_FILE = "tahminler.json"

DEFAULT_LOKASYON = "ATAPARK HALISAHA"
DEFAULT_GUN = "Çarşamba"
DEFAULT_SAAT = "21:00 / 22:00"

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

def verileri_yukle():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return VARSAYILAN_OYUNCULAR

def verileri_kaydet(veriler):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(veriler, f, ensure_ascii=False, indent=2)

def maclari_yukle():
    sezon_52 = {str(i): {"oynandi": False, "skor_girildi": False, "tarih": "", "lokasyon": DEFAULT_LOKASYON, "gun": DEFAULT_GUN, "saat": DEFAULT_SAAT, "skor1": "", "skor2": "", "takim1": [], "takim2": []} for i in range(1, 53)}
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

def maclari_kaydet(maclar):
    with open(MACLAR_FILE, "w", encoding="utf-8") as f:
        json.dump(maclar, f, ensure_ascii=False, indent=2)

def tahminleri_yukle():
    if os.path.exists(TAHMINLER_FILE):
        try:
            with open(TAHMINLER_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def tahminleri_kaydet(tahminler):
    with open(TAHMINLER_FILE, "w", encoding="utf-8") as f:
        json.dump(tahminler, f, ensure_ascii=False, indent=2)

if "oyuncular" not in st.session_state:
    st.session_state.oyuncular = verileri_yukle()
if "maclar" not in st.session_state:
    st.session_state.maclar = maclari_yukle()
if "tahminler" not in st.session_state:
    st.session_state.tahminler = tahminleri_yukle()

def net_puan(p):
    return round(p.get("ana_puan", 6.0) + p.get("ek_puan", 0.0), 2)

def galibiyet_orani(p):
    m = p.get("mac", 0)
    g = p.get("galibiyet", 0)
    return int((g / m) * 100) if m > 0 else 0

st.title("⚽ Halı Saha Kadro & Sezon Yönetim Sistemi")

sekmeler = st.tabs(["Kadro Kurucu & Dengeleme", "Oyuncu İstatistikleri", "Maç Tahmin Oyunu", "Sezon Fikstürü (52 Hafta)"])

# 1. SEKME: KADRO KURUCU
with sekmeler[0]:
    st.markdown("### Oyuncu Havuzu & Adil 7v7 Kadro Dağılımı")
    
    col_sol, col_sag = st.columns([1, 1])
    
    with col_sol:
        st.markdown("#### Oyuncu Havuzu (14 Seçim)")
        secili_sayisi = sum(1 for p in st.session_state.oyuncular if p.get("secili", False))
        
        if secili_sayisi == 14:
            st.success(f"Seçili Oyuncu: {secili_sayisi} / 14 (Hazır)")
        else:
            st.warning(f"Seçili Oyuncu: {secili_sayisi} / 14 (Tam 14 olmalı)")
        
        for idx, p in enumerate(st.session_state.oyuncular):
            c1, c2, c3, c4 = st.columns([1, 3, 2, 2])
            with c1:
                yeni_secim = st.checkbox("", value=p.get("secili", False), key=f"chk_{idx}")
                if yeni_secim != p.get("secili", False):
                    st.session_state.oyuncular[idx]["secili"] = yeni_secim
                    verileri_kaydet(st.session_state.oyuncular)
                    st.rerun()
            with c2:
                mevki_renk = {"Kale": "🔴", "Defans": "🔵", "Ortasaha": "🟢", "Forvet": "🟠"}.get(p['mevki'], "⚪")
                st.markdown(f"{mevki_renk} **{p['isim']}** <span style='color:gray; font-size:12px;'>({p['mevki']})</span>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"<span style='color:#f1c40f; font-weight:bold;'>{net_puan(p)} P</span>", unsafe_allow_html=True)
            with c4:
                if st.button("Sil", key=f"del_{idx}"):
                    st.session_state.oyuncular.pop(idx)
                    verileri_kaydet(st.session_state.oyuncular)
                    st.rerun()

        with st.form("yeni_oyuncu_form"):
            st.markdown("##### Yeni Oyuncu Ekle")
            y_isim = st.text_input("İsim")
            y_mevki = st.selectbox("Mevki", ["Kale", "Defans", "Ortasaha", "Forvet"])
            y_puan = st.number_input("Sabit Puan", value=6.0, step=0.1)
            if st.form_submit_button("Oyuncuyu Ekle"):
                if y_isim:
                    st.session_state.oyuncular.append({
                        "isim": y_isim, "mevki": y_mevki, "ana_puan": y_puan, 
                        "ek_puan": 0.0, "telefon": "", "mac": 0, "galibiyet": 0, 
                        "beraberlik": 0, "maglubiyet": 0, "gelmedigi_hafta": 0, "secili": False
                    })
                    verileri_kaydet(st.session_state.oyuncular)
                    st.success(f"{y_isim} eklendi!")
                    st.rerun()

    with col_sag:
        st.markdown("#### Maç ve Kadro Paneli")
        gelenler = [p for p in st.session_state.oyuncular if p.get("secili", False)]
        
        hafta_sec = st.selectbox("Hafta Seçimi", [f"{i}. Hafta" for i in range(1, 53)])
        h_no = hafta_sec.split(".")[0].strip()
        
        c_tarih, c_gun = st.columns(2)
        with c_tarih:
            tarih_val = st.text_input("Tarih", value=datetime.now().strftime("%d.%m.%Y"))
        with c_gun:
            gun_val = st.text_input("Gün", value=DEFAULT_GUN)
            
        c_saat, c_lok = st.columns(2)
        with c_saat:
            saat_val = st.text_input("Saat", value=DEFAULT_SAAT)
        with c_lok:
            lok_val = st.text_input("Lokasyon", value=DEFAULT_LOKASYON)

        if st.button("🚀 7 vs 7 ADİL KADRO OLUŞTUR", type="primary", use_container_width=True):
            if len(gelenler) != 14:
                st.error("Kadro kurmak için tam 14 oyuncu seçmelisiniz!")
            else:
                sirali_gelenler = sorted(gelenler, key=lambda x: net_puan(x), reverse=True)
                t1, t2 = [], []
                for p in sirali_gelenler:
                    if len(t1) < 7 and (len(t2) == 7 or sum(net_puan(x) for x in t1) <= sum(net_puan(x) for x in t2)):
                        t1.append(p)
                    else:
                        t2.append(p)
                st.session_state.aktif_t1 = t1
                st.session_state.aktif_t2 = t2
                st.success("Adil kadrolar başarıyla oluşturuldu!")

        if "aktif_t1" in st.session_state and "aktif_t2" in st.session_state:
            t1 = st.session_state.aktif_t1
            t2 = st.session_state.aktif_t2
            p1 = sum(net_puan(x) for x in t1)
            p2 = sum(net_puan(x) for x in t2)
            fark = abs(p1 - p2)
            
            st.markdown(f"<div style='text-align:center; background-color:#1e293b; padding:8px; border-radius:6px; margin:10px 0;'>Puan Farkı: <span style='color:{'#22c55e' if fark < 0.5 else '#f59e0b'}; font-weight:bold;'>{fark:.2f}</span></div>", unsafe_allow_html=True)

            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.markdown(f"<div style='background-color:#c2410c; padding:10px; border-radius:8px; color:white; font-weight:bold; text-align:center;'>🟠 TURUNCU TAKIM<br>({p1:.1f} P)</div>", unsafe_allow_html=True)
                for p in t1:
                    st.markdown(f"• {p['isim']} <span style='color:#facc15;'>({net_puan(p)}p)</span>", unsafe_allow_html=True)
            with col_t2:
                st.markdown(f"<div style='background-color:#1e293b; padding:10px; border-radius:8px; color:white; font-weight:bold; text-align:center; border: 1px solid #475569;'>⚫ SİYAH TAKIM<br>({p2:.1f} P)</div>", unsafe_allow_html=True)
                for p in t2:
                    st.markdown(f"• {p['isim']} <span style='color:#facc15;'>({net_puan(p)}p)</span>", unsafe_allow_html=True)

            if st.button("💾 Kadroyu Fikstüre Kaydet", use_container_width=True):
                st.session_state.maclar[h_no] = {
                    "oynandi": False, "skor_girildi": False,
                    "tarih": tarih_val, "lokasyon": lok_val, "gun": gun_val, "saat": saat_val,
                    "skor1": "", "skor2": "",
                    "takim1": [{"isim": p["isim"], "mevki": p["mevki"]} for p in t1],
                    "takim2": [{"isim": p["isim"], "mevki": p["mevki"]} for p in t2]
                }
                maclari_kaydet(st.session_state.maclar)
                st.success(f"{hafta_sec} kadrosu başarıyla kaydedildi!")

# 2. SEKME: OYUNCU İSTATİSTİKLERİ
with sekmeler[1]:
    st.subheader("📊 Oyuncu Performans & İstatistik Masası")
    for idx, p in enumerate(sorted(st.session_state.oyuncular, key=lambda x: net_puan(x), reverse=True), 1):
        c1, c2, c3, c4, c5 = st.columns([1, 3, 2, 2, 2])
        c1.write(f"#{idx}")
        c2.markdown(f"**{p['isim']}** ({p['mevki']})")
        c3.markdown(f"<span style='color:#f1c40f;'>{net_puan(p)} P</span>", unsafe_allow_html=True)
        c4.write(f"Maç: {p.get('mac',0)} | G: {p.get('galibiyet',0)}")
        c5.markdown(f"Kazanma: **%{galibiyet_orani(p)}**")

# 3. SEKME: MAÇ TAHMİN OYUNU
with sekmeler[2]:
    st.subheader("🎯 Maç Tahmin ve Skor Bahisleri")
    tahmin_hafta = st.selectbox("Tahmin Yapılacak Hafta", [f"{i}. Hafta" for i in range(1, 53)], key="tahmin_hafta_sec")
    h_key = tahmin_hafta.split(".")[0].strip()
    
    mac_bilgi = st.session_state.maclar.get(h_key, {})
    if not mac_bilgi.get("takim1"):
        st.warning("Bu haftanın kadrosu henüz belirlenmemiş!")
    else:
        st.info(f"Tarih: {mac_bilgi.get('tarih')} | Saha: {mac_bilgi.get('lokasyon')}")
        
        with st.form("tahmin_form"):
            t_isim = st.selectbox("Adınız", [p["isim"] for p in st.session_state.oyuncular])
            ts1 = st.number_input("Turuncu Takım Skor Tahmini", min_value=0, max_value=20, value=5)
            ts2 = st.number_input("Siyah Takım Skor Tahmini", min_value=0, max_value=20, value=5)
            
            if st.form_submit_button("Tahmini Kaydet"):
                if h_key not in st.session_state.tahminler:
                    st.session_state.tahminler[h_key] = {}
                st.session_state.tahminler[h_key][t_isim] = {"turuncu": ts1, "siyah": ts2}
                tahminleri_kaydet(st.session_state.tahminler)
                st.success(f"{t_isim}, tahminin kaydedildi!")

        st.markdown("#### Bu Hafta Yapılan Tahminler")
        hafta_tahminleri = st.session_state.tahminler.get(h_key, {})
        if hafta_tahminleri:
            for kisi, tahmin in hafta_tahminleri.items():
                st.markdown(f"👤 **{kisi}**: Turuncu {tahmin['turuncu']} - {tahmin['siyah']} Siyah")
        else:
            st.text("Henüz tahmin giren kimse yok.")

# 4. SEKME: SEZON FİKSTÜRÜ
with sekmeler[3]:
    st.subheader("🗓️ 52 Haftalık Sezon Fikstürü ve Skor Girişi")
    for i in range(1, 53):
        mac = st.session_state.maclar.get(str(i), {})
        with st.expander(f"{i}. Hafta - {'Oynandı ✅' : mac.get('skor_girildi') else 'Bekliyor ⏳'}"):
            if mac.get("takim1"):
                st.text(f"Tarih: {mac.get('tarih')} | Saha: {mac.get('lokasyon')} | Gün: {mac.get('gun')} - {mac.get('saat')}")
                
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    st.markdown("**Turuncu Takım**")
                    for p in mac.get("takim1", []):
                        st.text(f"• {p['isim']} ({p['mevki']})")
                with col_t2:
                    st.markdown("**Siyah Takım**")
                    for p in mac.get("takim2", []):
                        st.text(f"• {p['isim']} ({p['mevki']})")

                if mac.get("skor_girildi"):
                    st.markdown(f"### 🏆 Skor: Turuncu {mac.get('skor1')} - {mac.get('skor2')} Siyah")
                
                with st.form(f"skor_form_{i}"):
                    s1 = st.number_input("Turuncu Skor", 0, 20, 0, key=f"s1_{i}")
                    s2 = st.number_input("Siyah Skor", 0, 20, 0, key=f"s2_{i}")
                    if st.form_submit_button("Skoru ve İstatistikleri İşle"):
                        st.session_state.maclar[str(i)]["skor_girildi"] = True
                        st.session_state.maclar[str(i)]["skor1"] = s1
                        st.session_state.maclar[str(i)]["skor2"] = s2
                        maclari_kaydet(st.session_state.maclar)
                        st.success("Skor işlendi ve istatistikler güncellendi!")
                        st.rerun()
            else:
                st.text("Bu hafta için henüz kadro kurulmadı.")
