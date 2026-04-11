import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import re
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# --- CONFIGURATION ---
def get_api_key():
    # Streamlit Cloud Secrets'tan
    if "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    # .env dosyasından
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return api_key
    return None

api_key = get_api_key()

if not api_key:
    st.error("❌ GEMINI_API_KEY bulunamadı!")
    st.info("""
    Streamlit Cloud'da ayarlamak için:
    1. App Settings → Secrets
    2. Ekle: GEMINI_API_KEY=your-key
    """)
    st.stop()

try:
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"❌ API Key Error: {str(e)}")
    st.stop()

# --- VERİ KAYNAGI ---
@st.cache_data
def load_ilanlar():
    try:
        df = pd.read_csv("ilanlar.csv")
        return df
    except:
        st.error("❌ ilanlar.csv bulunamadı!")
        st.stop()

df_ilanlar = load_ilanlar()

# --- NLU: INTENT RECOGNITION ---
def extract_intent(user_query: str) -> dict:
    """Gemini ile user intent'ini anla"""
    prompt = f"""Kullanıcı: "{user_query}"

Bunu analiz et ve JSON döndür (başka bir şey yazma!):
{{"intent": "greeting/farewell/search/thanks/other", 
"city": "şehir adı veya null",
"room_type": "2+1 gibi veya null", 
"price_max": "sayı veya null",
"query_type": "budget/luxury/general"}}"""
    
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt, request_options={"timeout": 10})
        json_str = re.sub(r'```json\n?|\n?```', '', response.text.strip())
        return json.loads(json_str)
    except Exception as e:
        st.warning(f"⚠️ Analiz hatası: {str(e)}")
        return {"intent": "other"}

# --- CSV SEARCH ---
def search_ilanlar(intent_data: dict) -> list:
    results = df_ilanlar.copy()
    
    if intent_data.get("city"):
        results = results[results["sehir"].str.contains(intent_data["city"], case=False, na=False)]
    
    if intent_data.get("room_type"):
        results = results[results["oda_sayisi"].str.contains(intent_data["room_type"], case=False, na=False)]
    
    if intent_data.get("query_type") == "budget":
        results = results[results["fiyat_tl"] < 10000000]
    elif intent_data.get("query_type") == "luxury":
        results = results[results["fiyat_tl"] > 35000000]
    
    return results.to_dict("records")

# --- RESPONSE ---
def generate_response(intent: dict, search_results: list) -> str:
    intent_type = intent.get("intent", "other")
    
    if intent_type == "greeting":
        return "🏠 Merhaba! Size ev bulmakta yardımcı olabilirim. Ne arıyorsunuz?"
    elif intent_type == "farewell":
        return "👋 Görüşmek üzere!"
    elif intent_type == "thanks":
        return "😊 Rica ederim!"
    elif intent_type == "search":
        if not search_results:
            return "😔 Bulunamadı. Başka bir arama yapmak ister misiniz?"
        response = f"✅ **{len(search_results)} ilan buldum:**\n\n"
        for ilan in search_results[:5]:
            response += f"🏠 **{ilan['baslik']}**\n💰 ₺{ilan['fiyat_tl']:,.0f}\n✨ {ilan['ozellik']}\n\n"
        return response
    else:
        return "🤔 Anlayamadım. Bir emlak ilanı arıyor musunuz?"

# --- UI ---
st.set_page_config(page_title="🏠 Akıllı Emlak Asistanı", page_icon="🏠")
st.title("🏠 Akıllı Emlak Asistanı")
st.markdown("**🤖 Gemini AI tarafından destekleniyor**")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Sorununuzu yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("🤔 Analiz ediliyor..."):
            try:
                intent = extract_intent(prompt)
                results = search_ilanlar(intent) if intent.get("intent") == "search" else []
                response = generate_response(intent, results)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"❌ Hata: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

st.divider()
st.caption(f"📊 {len(df_ilanlar)} İlan | 🏙️ {df_ilanlar['sehir'].nunique()} Şehir")
