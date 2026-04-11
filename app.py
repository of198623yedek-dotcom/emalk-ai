import streamlit as st
import pandas as pd
import random
import re

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

# --- SIMPLE NLU (Regex & Keyword Matching) ---
def extract_intent(user_query: str) -> dict:
    """Simple keyword-based intent extraction (NO API)"""
    query_lower = user_query.lower()
    
    # Greeting patterns
    if any(word in query_lower for word in ["merhaba", "selam", "naber", "nasılsın", "hi", "hello"]):
        return {"intent": "greeting"}
    
    # Farewell patterns
    if any(word in query_lower for word in ["baybay", "görüşürüz", "hoşça", "bye"]):
        return {"intent": "farewell"}
    
    # Thanks patterns
    if any(word in query_lower for word in ["teşekkür", "sağol", "thanks"]):
        return {"intent": "thanks"}
    
    # Search patterns
    if any(word in query_lower for word in ["ilan", "ev", "daire", "villa", "bul", "ara", "göster", "var", "kaç"]):
        city = None
        room_type = None
        query_type = "general"
        
        # City detection
        cities = df_ilanlar["sehir"].unique().tolist()
        for city_name in cities:
            if city_name.lower() in query_lower:
                city = city_name
                break
        
        # Room type detection
        if "1+1" in query_lower or "1 1" in query_lower:
            room_type = "1+1"
        elif "2+1" in query_lower or "2 1" in query_lower:
            room_type = "2+1"
        elif "3+1" in query_lower or "3 1" in query_lower:
            room_type = "3+1"
        elif "4+1" in query_lower or "4 1" in query_lower:
            room_type = "4+1"
        elif "5+2" in query_lower or "5 2" in query_lower:
            room_type = "5+2"
        
        # Price query type
        if "ucuz" in query_lower or "uygun" in query_lower:
            query_type = "budget"
        elif "pahalı" in query_lower or "lüks" in query_lower:
            query_type = "luxury"
        
        return {
            "intent": "search",
            "city": city,
            "room_type": room_type,
            "query_type": query_type
        }
    
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

# --- RESPONSE GENERATION ---
def generate_response(intent: dict, search_results: list) -> str:
    intent_type = intent.get("intent", "other")
    
    greetings = [
        "🏠 Merhaba! Size ev bulmakta yardımcı olabilirim. Ne arıyorsunuz?",
        "👋 Hoş geldiniz! Emlak danışmanınız burada. Ne arayabilirim?",
        "🏡 Merhaba! Hayalinizdeki evi bulalım mı?",
    ]
    
    if intent_type == "greeting":
        return random.choice(greetings)
    
    elif intent_type == "farewell":
        return "👋 Görüşmek üzere! İyi günler dilerim."
    
    elif intent_type == "thanks":
        return "😊 Rica ederim! Başka bir şey sorabilirsem..."
    
    elif intent_type == "search":
        if not search_results:
            return "😔 Maalesef bulunamadı. Başka bir arama yapmak ister misiniz?"
        
        response = f"✅ **{len(search_results)} ilan buldum:**\n\n"
        for ilan in search_results[:5]:
            response += f"""🏠 **{ilan['baslik']}**
💰 ₺{ilan['fiyat_tl']:,.0f}
✨ {ilan['ozellik']}
---
"""
        return response
    
    else:
        return "🤔 Anlayamadım. Bir emlak ilanı arıyor musunuz? Örneğin 'Beşiktaş'ta villa' yazabilirsiniz."

# --- STREAMLIT UI ---
st.set_page_config(page_title="🏠 Akıllı Emlak Asistanı", page_icon="🏠")
st.title("🏠 Akıllı Emlak Asistanı")
st.markdown("**Demo Modu - Mock Data (Ücretsiz & Hızlı)**")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Sorununuzu yazın... (Örn: Kadıköy'de 2+1)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("🔍 Aranıyor..."):
            # Intent extraction
            intent = extract_intent(prompt)
            
            # Search
            results = search_ilanlar(intent) if intent.get("intent") == "search" else []
            
            # Response
            response = generate_response(intent, results)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

st.divider()
st.caption(f"📊 {len(df_ilanlar)} İlan | 🏙️ {df_ilanlar['sehir'].nunique()} Şehir")
