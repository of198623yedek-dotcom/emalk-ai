import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import re
import os
from dotenv import load_dotenv

# --- AYARLAR VE CONFIG ---
load_dotenv()

# API Key Kontrolü (Streamlit Cloud + Lokal)
def get_api_key():
    if "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key != "YOUR_GEMINI_API_KEY_HERE":
        return api_key
    return None

GOOGLE_API_KEY = get_api_key()

if not GOOGLE_API_KEY:
    st.error("❌ GEMINI_API_KEY bulunamadı!")
    st.info("Streamlit Cloud: Settings → Secrets → GEMINI_API_KEY ekleyin\nVeya lokal'de .env dosyasına ekleyin")
    st.stop()

try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error(f"❌ API Error: {str(e)}")
    st.stop()

# --- VERİ YÜKLEME ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("ilanlar.csv")
        # Veri temizleme
        if df.empty:
            st.warning("⚠️ CSV dosyası boş!")
            return df
        return df
    except FileNotFoundError:
        st.error("❌ ilanlar.csv bulunamadı!")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Veri yükleme hatası: {e}")
        return pd.DataFrame()

df_ilanlar = load_data()

if df_ilanlar.empty:
    st.stop()

# --- GEMINI INTENT EXTRACTION (Production Ready) ---
def extract_intent_from_gemini(user_query):
    """
    Gemini ile kullanıcı sorgusundan arama parametrelerini ayıklar.
    JSON temizleme ve boş veri kontrolü ile robust.
    """
    prompt = f"""
    Sen bir emlak asistanısın. Kullanıcının isteğini analiz edip JSON formatında çıktı vermelisin.
    
    Kullanıcı Mesajı: "{user_query}"
    
    Çıktı Formatı (SADECE JSON, başka şey yazma):
    {{
      "filters": {{
        "sehir": "string veya null",
        "min_fiyat": number veya null,
        "max_fiyat": number veya null,
        "oda_sayisi": "string veya null"
      }},
      "is_searching": true/false
    }}
    
    Kurallar:
    1. Eğer kullanıcı bir şey aramıyorsa (sadece selam veriyorsa) "is_searching": false yap.
    2. SADECE JSON döndür, açıklama yapma.
    3. Fiyat belirtilmemişse null bırak.
    """

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # --- KRİTİK DOKUNUŞ 1: Robust JSON Temizleme ---
        # 1. Markdown code blocks'u temizle
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # 2. JSON objesini bul
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(0)
            parsed = json.loads(json_str)
            
            # 3. Boş veri kontrolü
            if not parsed:
                return {"is_searching": False, "filters": {}}
            
            return parsed
        else:
            # JSON bulunamazsa safe default dön
            return {"is_searching": False, "filters": {}}
            
    except json.JSONDecodeError as e:
        st.warning(f"⚠️ JSON parse hatası: {str(e)[:50]}")
        return {"is_searching": False, "filters": {}}
    except Exception as e:
        st.warning(f"⚠️ AI Analiz hatası: {str(e)[:50]}")
        return {"is_searching": False, "filters": {}}

# --- FİLTRELEME MOTORU ---
def filter_listings(df, filters):
    """CSV'de arama yap - Boş veri kontrollü"""
    
    # Boş DataFrame kontrolü
    if df.empty:
        return df
    
    res = df.copy()
    
    # Şehir Filtresi
    if filters.get("sehir"):
        try:
            res = res[res['sehir'].str.lower().str.contains(filters['sehir'].lower(), na=False)]
        except:
            pass
    
    # Minimum Fiyat Filtresi
    if filters.get("min_fiyat"):
        try:
            min_price = float(filters['min_fiyat'])
            res = res[res['fiyat_tl'] >= min_price]
        except:
            pass
    
    # Maksimum Fiyat Filtresi
    if filters.get("max_fiyat"):
        try:
            max_price = float(filters['max_fiyat'])
            res = res[res['fiyat_tl'] <= max_price]
        except:
            pass
    
    # Oda Sayısı Filtresi
    if filters.get("oda_sayisi"):
        try:
            res = res[res['oda_sayisi'].astype(str).str.contains(filters['oda_sayisi'], na=False)]
        except:
            pass
    
    return res

# --- STREAMLIT UI ---
st.set_page_config(page_title="🏠 AI Emlak Asistanı", page_icon="🏠", layout="centered")
st.title("🏠 AI Emlak Asistanı")
st.markdown("**🤖 Gemini AI + Production Ready**")
st.write("İstediğiniz evi bana anlatın, ben sizin için bulayım!")

# Chat Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat Geçmişini Göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcı Girişi
if prompt := st.chat_input("Örn: Beşiktaş'ta 2+1, maksimum 5 milyon TL"):
    # 1. Kullanıcı mesajını ekrana bas
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. AI Analizi Yap
    with st.chat_message("assistant"):
        with st.spinner("🔍 İsteğiniz analiz ediliyor..."):
            intent = extract_intent_from_gemini(prompt)
            
            if not intent.get("is_searching", False):
                response_text = "👋 Merhaba! Size nasıl yardımcı olabilirim? Aradığınız evin özelliklerini söylemek yeterli."
                st.markdown(response_text)
            else:
                # 3. Filtrele
                filters = intent.get("filters", {})
                results = filter_listings(df_ilanlar, filters)
                
                if results.empty:
                    response_text = "😔 Maalesef kriterlerinize uygun bir ilan bulamadım. Başka bir arama yapmak ister misiniz?"
                    st.markdown(response_text)
                else:
                    response_text = f"✅ Aradığınız kriterlere uygun **{len(results)}** adet ilan buldum:\n\n"
                    st.markdown(response_text)
                    
                    # Sonuçları ekrana bas (Max 5)
                    for idx, ilan in enumerate(results.head(5).to_dict("records"), 1):
                        st.markdown(f"""
🏠 **{idx}. {ilan.get('baslik', 'N/A')}**
📍 {ilan.get('sehir', 'N/A')} - {ilan.get('oda_sayisi', 'N/A')}
💰 ₺{ilan.get('fiyat_tl', 0):,.0f}
✨ {ilan.get('ozellik', 'N/A')}
---
""")
            
            st.session_state.messages.append({"role": "assistant", "content": response_text})

st.divider()
st.caption(f"📊 Toplam: {len(df_ilanlar)} İlan | 🏙️ {df_ilanlar['sehir'].nunique()} Şehir")
