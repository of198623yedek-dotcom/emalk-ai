import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import re
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# --- 1. API CONFIGURATION ---
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
    st.info("Streamlit Cloud: Settings → Secrets → GEMINI_API_KEY ekleyin")
    st.stop()

try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro')
except Exception as e:
    st.error(f"❌ API Error: {str(e)}")
    st.stop()

# --- 2. CSV DATA ---
def load_ilanlar():
    try:
        df = pd.read_csv("ilanlar.csv")
        return df
    except:
        st.error("❌ ilanlar.csv bulunamadı!")
        st.stop()

df_ilanlar = load_ilanlar()

# --- 3. INTENT EXTRACTION (Gemini AI) ---
def extract_search_intent(user_input):
    """
    Kullanıcının cümlesinden şehir, oda sayısı ve bütçe bilgilerini ayıklar.
    """
    prompt = f"""
    Sen bir emlak asistanı veri ayıklama botusun. 
    Kullanıcının yazdığı cümleden şu bilgileri çıkar:
    1. city (şehir veya ilçe)
    2. room_type (oda sayısı, örn: '2+1', '3+1' veya 'daire')
    3. max_budget (maksimum bütçe, sadece sayı olarak, bulamazsan null)

    Kullanıcı cümlesi: "{user_input}"

    Yanıtını SADECE aşağıdaki JSON formatında ver, başka hiçbir açıklama yapma:
    {{
        "city": "string veya null",
        "room_type": "string veya null",
        "max_budget": number veya null
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        json_str = re.sub(r'```json\n?|\n?```', '', response.text.strip())
        return json.loads(json_str)
    except Exception as e:
        st.warning(f"⚠️ Analiz hatası: {str(e)}")
        return {"city": None, "room_type": None, "max_budget": None}

# --- 4. SEARCH IN DATABASE ---
def search_ilanlar(intent_data):
    """CSV'de arama yap"""
    results = df_ilanlar.copy()
    
    # City filter
    if intent_data.get("city"):
        city = intent_data["city"].lower()
        results = results[results["sehir"].str.lower().str.contains(city, na=False)]
    
    # Room type filter
    if intent_data.get("room_type"):
        room = intent_data["room_type"]
        results = results[results["oda_sayisi"].str.contains(room, na=False)]
    
    # Budget filter
    if intent_data.get("max_budget"):
        try:
            max_budget = int(intent_data["max_budget"])
            results = results[results["fiyat_tl"] <= max_budget]
        except:
            pass
    
    return results.to_dict("records")

# --- 5. UI ---
st.set_page_config(page_title="🏠 Akıllı Emlak Asistanı", page_icon="🏠", layout="centered")
st.title("🏠 Akıllı Emlak Asistanı")
st.markdown("**🤖 Gemini AI + Smart Search**")
st.write("Aradığınız evi doğal dille söyleyin, ben bulayım!")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_query = st.chat_input("Örn: Beşiktaş'ta 3+1, 5 milyon TL altı bir ev arıyorum.")

if user_query:
    # User message
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)
    
    # Bot response
    with st.chat_message("assistant"):
        with st.spinner("🔍 İstek analiz ediliyor..."):
            try:
                # 1. Intent extraction
                extracted_data = extract_search_intent(user_query)
                
                # 2. Database search
                search_results = search_ilanlar(extracted_data)
                
                # 3. Build response
                response = f"""
✅ **Analiz Sonucu:**
- 🏙️ Şehir: {extracted_data.get("city") or "Belirtilmedi"}
- 🚪 Oda Sayısı: {extracted_data.get("room_type") or "Belirtilmedi"}
- 💰 Max Bütçe: {f"₺{extracted_data.get('max_budget'):,.0f}" if extracted_data.get("max_budget") else "Belirtilmedi"}

"""
                
                if search_results:
                    response += f"🎯 **{len(search_results)} ilan bulundu:**\n\n"
                    for ilan in search_results[:5]:
                        response += f"""
🏠 **{ilan['baslik']}**
📍 {ilan['sehir']} - {ilan['oda_sayisi']}
💰 ₺{ilan['fiyat_tl']:,.0f}
✨ {ilan['ozellik']}
---
"""
                else:
                    response += "😔 Maalesef kriterlerinize uygun ilan bulamadım. Başka bir arama yapmak ister misiniz?"
                
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_msg = f"❌ Hata: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

st.divider()
st.caption(f"📊 {len(df_ilanlar)} İlan | 🏙️ {df_ilanlar['sehir'].nunique()} Şehir")
