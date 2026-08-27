import streamlit as st
import itertools
import json
import os
import io
import base64
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Sayfa Yapılandırması ve Masaüstü Koyu Tema CSS Enjeksiyonu
st.set_page_config(page_title="Halı Saha Yönetim Sistemi", page_icon="⚽", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    /* Ana Koyu Tema */
    .stApp {
        background-color: #0f172a !important;
        color: #f8fafc;
    }
    
    /* Sekme Başlıkları */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1e293b;
        padding: 6px;
        border-radius: 8px;
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8;
        font-weight: 600;
        border-radius: 6px;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0284c7 !important;
        color: white !important;
    }

    /* Kart Yapıları */
    .team-card-t1 {
        background-color: #1c2833;
        border: 2px solid #e67e22;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
    }
    .team-card-t2 {
        background-color: #1c2833;
        border: 2px solid #5d6d7e;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
    }
    
    .team-header-t1 {
        background-color: #e67e22;
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-weight: bold;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 15px;
    }
    .team-header-t2 {
        background-color: #34495e;
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-weight: bold;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 15px;
    }

    .player-row {
        background-color: #273746;
        border-radius: 5px;
        padding: 4px 8px;
        margin: 3px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 13px;
        font-weight: bold;
    }

    .badge-kal { background-color: #e74c3c; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; margin-right: 6px; }
    .badge-def { background-color: #3498db; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; margin-right: 6px; }
    .badge-ort { background-color: #2ecc71; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; margin-right: 6px; }
    .badge-for { background-color: #f39c12; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; margin-right: 6px; }

    .score-badge { color: #f1c40f; font-weight: bold; }
    
    .match-info-bar {
        background-color: #17202a;
        border-radius: 8px;
        padding: 8px 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

DATA_FILE = "oyuncular.json"
MACLAR_FILE = "maclar.json"

DEFAULT_LOKASYON = "ATAPARK HALISAHA"
DEFAULT_GUN = "Çarşamba"
DEFAULT_SAAT = "21:00 / 22:00"

def tr_temizle(metin):
    if not metin: return ""
    donusum = {'İ': 'I', 'ı': 'i', 'Ş': 'S', 'ş': 's', 'Ğ': 'G', 'ğ': 'g', 'Ü': 'U', 'ü': 'u', 'Ö': 'O', 'ö': 'o', 'Ç': 'C', 'ç': 'c'}
    sonuc = str(metin)
    for k, v in donusum.items(): sonuc = sonuc.replace(k, v)
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

def verileri_yukle():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception: pass
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
                    for k, v in kayitli.items(): sezon_52[str(k)] = v
        except Exception: pass
    return sezon_52

def maclari_kaydet(maclar):
    with open(MACLAR_FILE, "w", encoding="utf-8") as f:
        json.dump(maclar, f, ensure_ascii=False, indent=2)

if "oyuncular" not in st.session_state: st.session_state.oyuncular = verileri_yukle()
if "maclar" not in st.session_state: st.session_state.maclar = maclari_yukle()
if "varyasyon_no" not in st.session_state: st.session_state.varyasyon_no = 0
if "olasi_kadrolar" not in st.session_state: st.session_state.olasi_kadrolar = []

def net_puan(p): return round(p.get("ana_puan", 6.0) + p.get("ek_puan", 0.0), 2)
def galibiyet_orani(p):
    m, g = p.get("mac", 0), p.get("galibiyet", 0)
    return int((g / m) * 100) if m > 0 else 0

# 3D Saha Çizim Motoru (Pillow)
def saha_gorseli_olustur(takim_oyunculari, forma_renk):
    img_w, img_h = 560, 360
    img = Image.new("RGB", (img_w, img_h), color="#1c2833")
    draw = ImageDraw.Draw(img)

    side_inset = img_w * 0.08
    top_y = img_h * 0.08
    bot_y = img_h * 0.86
    depth_3d = img_h * 0.05

    draw.polygon([
        (side_inset, bot_y), (img_w - side_inset, bot_y),
        (img_w - side_inset, bot_y + depth_3d), (side_inset, bot_y + depth_3d)
    ], fill="#0a3818")

    draw.polygon([
        (img_w - side_inset, top_y), (img_w - side_inset, bot_y),
        (img_w - side_inset, bot_y + depth_3d), (img_w - side_inset, top_y + depth_3d)
    ], fill="#0d421d")

    draw.polygon([
        (side_inset, top_y), (img_w - side_inset, top_y),
        (img_w - side_inset, bot_y), (side_inset, bot_y)
    ], fill="#157335", outline="#7bed9f", width=2)

    def s_xy(u, v):
        cur_y = top_y + (bot_y - top_y) * v
        cur_x = (side_inset) + (img_w - 2 * side_inset) * u
        return cur_x, cur_y

    tl, tr, br, bl = s_xy(0.03, 0.03), s_xy(0.97, 0.03), s_xy(0.97, 0.97), s_xy(0.03, 0.97)
    draw.polygon([tl, tr, br, bl], fill=None, outline="#ffffff", width=2)

    ml, mr = s_xy(0.03, 0.52), s_xy(0.97, 0.52)
    draw.line([ml, mr], fill="#ffffff", width=2)

    cx, cy = s_xy(0.5, 0.52)
    draw.ellipse([cx - img_w*0.13, cy - img_h*0.06, cx + img_w*0.13, cy + img_h*0.06], outline="#ffffff", width=2)

    k1, k2, k3, k4 = s_xy(0.28, 0.03), s_xy(0.72, 0.03), s_xy(0.72, 0.22), s_xy(0.28, 0.22)
    draw.polygon([k1, k2, k3, k4], fill=None, outline="#ffffff", width=2)

    a1, a2, a3, a4 = s_xy(0.28, 0.97), s_xy(0.72, 0.97), s_xy(0.72, 0.78), s_xy(0.28, 0.78)
    draw.polygon([a1, a2, a3, a4], fill=None, outline="#ffffff", width=2)

    fw, fh = 16, 16
    def ciz_forma_img(px, py, isim, no, f_col, kollar_beyaz=True):
        if kollar_beyaz:
            draw.polygon([(px - fw*0.6, py - fh*0.4), (px - fw*1.0, py - fh*0.05), (px - fw*0.7, py + fh*0.35), (px - fw*0.4, py + fh*0.05)], fill="#ffffff", outline="#222222")
            draw.polygon([(px + fw*0.6, py - fh*0.4), (px + fw*1.0, py - fh*0.05), (px + fw*0.7, py + fh*0.35), (px + fw*0.4, py + fh*0.05)], fill="#ffffff", outline="#222222")
        draw.polygon([(px - fw*0.6, py - fh*0.4), (px + fw*0.6, py - fh*0.4), (px + fw*0.5, py + fh*0.5), (px - fw*0.5, py + fh*0.5)], fill=f_col, outline="#111111")
        draw.text((px, py + 1), str(no), fill="#ffffff", anchor="mm", font_size=10)

        isim_k = tr_temizle(isim.split()[0][:8])
        bw = max(40, len(isim_k) * 7 + 10)
        draw.rectangle([px - bw/2, py + fh*0.5 + 2, px + bw/2, py + fh*0.5 + 16], fill="#ffffff", outline="#000000")
        draw.text((px, py + fh*0.5 + 9), isim_k, fill="#000000", anchor="mm", font_size=10)

    mevkiler = {"Kale": [], "Defans": [], "Ortasaha": [], "Forvet": []}
    for p in takim_oyunculari: mevkiler.setdefault(p.get("mevki", "Ortasaha"), []).append(p)

    f_no = 1
    for p in mevkiler.get("Kale", []):
        px, py = s_xy(0.5, 0.08)
        ciz_forma_img(px, py, p["isim"], f_no, "#2ecc71", kollar_beyaz=False)
        f_no += 1

    for mvk_adi, v_oran in [("Defans", 0.30), ("Ortasaha", 0.54), ("Forvet", 0.78)]:
        m_list = mevkiler.get(mvk_adi, [])
        for i, p in enumerate(m_list):
            u_pos = (i + 1) / (len(m_list) + 1)
            px, py = s_xy(u_pos, v_oran)
            ciz_forma_img(px, py, p["isim"], f_no, forma_renk, kollar_beyaz=True)
            f_no += 1

    return img

# --- ARAYÜZ BAŞLANGICI ---
st.title("⚽ Halı Saha Kadro & 52 Haftalık Sezon Yönetim Sistemi")

sekmeler = st.tabs(["Kadro Kurucu & Dengeleme", "Oyuncu İstatistikleri", "Kimya & Sinerji Analizi", "Sezon Fikstürü (52 Hafta)"])

# 1. SEKME: KADRO KURUCU
with sekmeler[0]:
    col_havuz, col_saha = st.columns([0.38, 0.62])

    with col_havuz:
        st.markdown("<h4 style='text-align:center;'>Oyuncu Havuzu</h4>", unsafe_allow_html=True)
        
        secili_sayisi = sum(1 for p in st.session_state.oyuncular if p.get("secili", False))
        st.markdown(f"<div style='text-align:center; font-weight:bold; color:{'#2ecc71' if secili_sayisi==14 else '#f39c12'}; margin-bottom:10px;'>Seçili Oyuncu: {secili_sayisi} / 14</div>", unsafe_allow_html=True)

        # Tablo Başlıkları
        h1, h2, h3, h4, h5, h6 = st.columns([0.8, 2.5, 1.8, 1.2, 1.2, 0.8])
        h1.caption("Tik")
        h2.caption("İsim")
        h3.caption("Mevki")
        h4.caption("Sabit")
        h5.caption("Toplam")
        h6.caption("Sil")

        # Oyuncu Listesi
        for idx, p in enumerate(st.session_state.oyuncular):
            r1, r2, r3, r4, r5, r6 = st.columns([0.8, 2.5, 1.8, 1.2, 1.2, 0.8])
            with r1:
                chk = st.checkbox("", value=p.get("secili", False), key=f"p_chk_{idx}", label_visibility="collapsed")
                if chk != p.get("secili", False):
                    st.session_state.oyuncular[idx]["secili"] = chk
                    verileri_kaydet(st.session_state.oyuncular)
                    st.rerun()
            with r2:
                st.markdown(f"<span style='font-size:13px; font-weight:bold;'>{p['isim']}</span>", unsafe_allow_html=True)
            with r3:
                badge_class = f"badge-{p['mevki'][:3].lower()}"
                st.markdown(f"<span class='{badge_class}'>{p['mevki'][:3].upper()}</span>", unsafe_allow_html=True)
            with r4:
                st.markdown(f"<span style='font-size:12px;'>{p.get('ana_puan',6.0):.1f}</span>", unsafe_allow_html=True)
            with r5:
                st.markdown(f"<span class='score-badge'>{net_puan(p):.1f}</span>", unsafe_allow_html=True)
            with r6:
                if st.button("X", key=f"p_del_{idx}"):
                    st.session_state.oyuncular.pop(idx)
                    verileri_kaydet(st.session_state.oyuncular)
                    st.rerun()

        # Yeni Oyuncu Ekleme
        with st.expander("+ Yeni Oyuncu Ekle"):
            y_isim = st.text_input("Oyuncu İsmi", key="y_isim_inp")
            y_mevki = st.selectbox("Mevki", ["Kale", "Defans", "Ortasaha", "Forvet"], key="y_mevki_inp")
            y_puan = st.number_input("Sabit Puan", value=6.0, step=0.1, key="y_puan_inp")
            if st.button("Listeye Ekle", use_container_width=True):
                if y_isim:
                    st.session_state.oyuncular.append({
                        "isim": y_isim, "mevki": y_mevki, "ana_puan": y_puan, 
                        "ek_puan": 0.0, "telefon": "", "mac": 0, "galibiyet": 0, 
                        "beraberlik": 0, "maglubiyet": 0, "gelmedigi_hafta": 0, "secili": False
                    })
                    verileri_kaydet(st.session_state.oyuncular)
                    st.rerun()

        if st.button("KADRO KUR (7 vs 7)", type="primary", use_container_width=True):
            gelenler = [p for p in st.session_state.oyuncular if p.get("secili", False)]
            if len(gelenler) != 14:
                st.error("Kadro kurmak için tam 14 oyuncu seçmelisiniz!")
            else:
                mevkiler = {}
                for p in gelenler: mevkiler.setdefault(p["mevki"], []).append(p)
                olasi = []
                for t1_cand in itertools.combinations(gelenler, 7):
                    t2_cand = [p for p in gelenler if p not in t1_cand]
                    uygun = True
                    for mvk, liste in mevkiler.items():
                        t1_s = sum(1 for p in t1_cand if p["mevki"] == mvk)
                        hedef = len(liste) // 2
                        if abs(t1_s - hedef) > (1 if len(liste) % 2 != 0 else 0):
                            uygun = False; break
                    if uygun:
                        fark = abs(sum(net_puan(p) for p in t1_cand) - sum(net_puan(p) for p in t2_cand))
                        olasi.append((fark, list(t1_cand), t2_cand))
                olasi.sort(key=lambda x: x[0])
                st.session_state.olasi_kadrolar = olasi[:20]
                st.session_state.varyasyon_no = 0
                st.rerun()

    with col_saha:
        gelenler = [p for p in st.session_state.oyuncular if p.get("secili", False)]
        
        # Üst Bilgi Barı
        if st.session_state.olasi_kadrolar:
            secili_varyasyon = st.session_state.olasi_kadrolar[st.session_state.varyasyon_no % len(st.session_state.olasi_kadrolar)]
            fark, t1_aktif, t2_aktif = secili_varyasyon
        else:
            t1_aktif, t2_aktif, fark = [], [], 0.0

        h_sec = st.selectbox("Hafta Seçimi", [f"{i}. Hafta" for i in range(1, 53)], index=2)
        h_no = h_sec.split(".")[0].strip()

        st.markdown(f"""
        <div class="match-info-bar">
            <div>
                <span style="color:#3498db; font-weight:bold;">Varyasyon: {st.session_state.varyasyon_no+1 if st.session_state.olasi_kadrolar else 1} / {len(st.session_state.olasi_kadrolar) if st.session_state.olasi_kadrolar else 1}</span>
                <span style="color:#e67e22; font-weight:bold; margin-left:15px;">{h_sec} | {DEFAULT_GUN} | Saat: {DEFAULT_SAAT} | Saha: {DEFAULT_LOKASYON}</span>
            </div>
            <div style="background-color:{'#27ae60' if fark < 0.5 else '#e67e22'}; padding:4px 10px; border-radius:6px; color:white; font-weight:bold;">
                Puan Farkı: {fark:.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # İki Takım Yan Yana (Masaüstü Gibi)
        t1_col, t2_col = st.columns(2)

        sira = {"Kale": 1, "Defans": 2, "Ortasaha": 3, "Forvet": 4}

        with t1_col:
            t1_puan = sum(net_puan(p) for p in t1_aktif)
            st.markdown(f"""
            <div class="team-header-t1">
                <span>🟠 TURUNCU TAKIM</span>
                <span style="background-color:#1c2833; padding:2px 8px; border-radius:4px; color:#f1c40f;">{t1_puan:.1f} P</span>
            </div>
            """, unsafe_allow_html=True)

            for p in sorted(t1_aktif, key=lambda x: sira.get(x["mevki"], 5)):
                badge = f"<span class='badge-{p['mevki'][:3].lower()}'>{p['mevki'][:3].upper()}</span>"
                st.markdown(f"""
                <div class="player-row">
                    <div>{badge} {p['isim']}</div>
                    <div class="score-badge">{net_puan(p):.1f} P</div>
                </div>
                """, unsafe_allow_html=True)

            if t1_aktif:
                img1 = saha_gorseli_olustur(t1_aktif, "#e67e22")
                st.image(img1, use_container_width=True)

        with t2_col:
            t2_puan = sum(net_puan(p) for p in t2_aktif)
            st.markdown(f"""
            <div class="team-header-t2">
                <span>⚫ SİYAH TAKIM</span>
                <span style="background-color:#1c2833; padding:2px 8px; border-radius:4px; color:#ecf0f1;">{t2_puan:.1f} P</span>
            </div>
            """, unsafe_allow_html=True)

            for p in sorted(t2_aktif, key=lambda x: sira.get(x["mevki"], 5)):
                badge = f"<span class='badge-{p['mevki'][:3].lower()}'>{p['mevki'][:3].upper()}</span>"
                st.markdown(f"""
                <div class="player-row">
                    <div>{badge} {p['isim']}</div>
                    <div style="color:#ecf0f1; font-weight:bold;">{net_puan(p):.1f} P</div>
                </div>
                """, unsafe_allow_html=True)

            if t2_aktif:
                img2 = saha_gorseli_olustur(t2_aktif, "#2c3e50")
                st.image(img2, use_container_width=True)

        # Alt Kontrol Barı (Kadro & Skor İşleme)
        st.markdown("---")
        b1, b2 = st.columns(2)
        with b1:
            if st.button("🔄 Sonraki Varyasyonu Göster", use_container_width=True):
                if st.session_state.olasi_kadrolar:
                    st.session_state.varyasyon_no += 1
                    st.rerun()
        with b2:
            if st.button("💾 KADROYU FİKSTÜRE KAYDET", type="primary", use_container_width=True):
                if t1_aktif and t2_aktif:
                    st.session_state.maclar[h_no] = {
                        "oynandi": False, "skor_girildi": False,
                        "tarih": datetime.now().strftime("%d.%m.%Y"), "lokasyon": DEFAULT_LOKASYON, 
                        "gun": DEFAULT_GUN, "saat": DEFAULT_SAAT, "skor1": "", "skor2": "",
                        "takim1": [{"isim": p["isim"], "mevki": p["mevki"]} for p in t1_aktif],
                        "takim2": [{"isim": p["isim"], "mevki": p["mevki"]} for p in t2_aktif]
                    }
                    maclari_kaydet(st.session_state.maclar)
                    st.success(f"{h_sec} kadrosu başarıyla fikstüre kaydedildi!")

# 2. SEKME: OYUNCU İSTATİSTİKLERİ
with sekmeler[1]:
    st.markdown("### OYUNCU PERFORMANS & DEVAMLILIK İSTATİSTİKLERİ")
    sirali = sorted(st.session_state.oyuncular, key=lambda x: net_puan(x), reverse=True)
    
    col_baslik = st.columns([0.6, 2.5, 1.5, 1.2, 1, 1, 1, 1, 1.2, 1.8])
    col_baslik[0].caption("Sıra")
    col_baslik[1].caption("İsim")
    col_baslik[2].caption("Mevki")
    col_baslik[3].caption("Toplam P")
    col_baslik[4].caption("M")
    col_baslik[5].caption("G")
    col_baslik[6].caption("B")
    col_baslik[7].caption("Mğ")
    col_baslik[8].caption("Kazanma %")
    col_baslik[9].caption("Devamlılık")

    for idx, p in enumerate(sirali, 1):
        cols = st.columns([0.6, 2.5, 1.5, 1.2, 1, 1, 1, 1, 1.2, 1.8])
        cols[0].write(f"#{idx}")
        cols[1].write(f"**{p['isim']}**")
        cols[2].write(p["mevki"])
        cols[3].markdown(f"<span class='score-badge'>{net_puan(p):.1f}</span>", unsafe_allow_html=True)
        cols[4].write(str(p.get("mac", 0)))
        cols[5].write(str(p.get("galibiyet", 0)))
        cols[6].write(str(p.get("beraberlik", 0)))
        cols[7].write(str(p.get("maglubiyet", 0)))
        cols[8].write(f"%{galibiyet_orani(p)}")
        gelmedi = p.get("gelmedigi_hafta", 0)
        cols[9].markdown(f"<span style='color:{'#e74c3c' if gelmedi>=3 else ('#e67e22' if gelmedi>0 else '#2ecc71')}; font-weight:bold;'>{'Aktif' if gelmedi==0 else f'{gelmedi} Hafta Yok'}</span>", unsafe_allow_html=True)

# 3. SEKME: KİMYA & SİNERJİ
with sekmeler[2]:
    st.markdown("### OYUNCU KİMYA & BİRLİKTE KAZANMA ANALİZİ")
    st.info("Tamamlanan maç sonuçları girildikçe ikili kimya ve sinerji oranları burada listelenir.")

# 4. SEKME: 52 HAFTALIK FİKSTÜR
with sekmeler[3]:
    st.markdown("### 52 HAFTALIK SEZON FİKSTÜRÜ")
    for i in range(1, 53):
        mac = st.session_state.maclar.get(str(i), {})
        with st.expander(f"{i}. Hafta - {'Oynandı ✅' if mac.get('skor_girildi') else ('Kadro Hazır 📋' if mac.get('takim1') else 'Bekliyor ⏳')}"):
            if mac.get("takim1"):
                st.write(f"📍 Saha: {mac.get('lokasyon')} | 🗓 Tarih: {mac.get('tarih')} ({mac.get('gun')})")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Turuncu Takım:**")
                    for p in mac.get("takim1", []): st.write(f"• {p['isim']} ({p['mevki']})")
                with c2:
                    st.markdown("**Siyah Takım:**")
                    for p in mac.get("takim2", []): st.write(f"• {p['isim']} ({p['mevki']})")
