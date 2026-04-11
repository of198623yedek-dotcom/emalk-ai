import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import re

# --- CONFIGURATION ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
        st.error("❌ GEMINI_API_KEY geçerli değil!")
        st.stop()
    genai.configure(api_key=api_key)
except KeyError:
    st.error("❌ GEMINI_API_KEY bulunamadı!")
    st.info("Streamlit Cloud Settings → Secrets → ekleyin:\nGEMINI_API_KEY=your-key-here")
    st.stop()

# --- VERİ KAYNAGI (CSV) ---
@st.cache_data
def load_ilanlar():
    try:
        df = pd.read_csv("ilanlar.csv")
        return df
    except FileNotFoundError:
        st.error("❌ ilanlar.csv dosyası bulunamadı!")
        st.stop()

df_ilanlar = load_ilanlar()

# --- AŞAMA 1: NLU (Intent Recognition) ---
def extract_intent(user_query: str) -> dict:
    """
    Kullanıcı sorgusundan amacını (intent) ve parametreleri çıkart
    Gemini API'sini kullanarak NLU yap
    """
    prompt = f"""
Sen bir emlak asistanı. Kullanıcının yazısını analiz et ve JSON formatında çıkart.

Kullanıcı Sorgusu: "{user_query}"

Çıkartacak bilgiler:
- intent: "greeting" (selamlaşma), "farewell" (vedalaşma), "search" (ilan arama), "thanks" (teşekkür), "other" (diğer)
- city: Şehir adı (varsa, yoksa null)
- room_type: Oda sayısı (varsa, yoksa null)
- price_max: Maksimum fiyat TL (varsa, yoksa null)
- query_type: "budget" (uygun), "luxury" (lüks), "general" (genel)

Sadece JSON döndür, başka bir şey yazma!

Örnek:
{{"intent": "search", "city": "Kadıköy", "room_type": "2+1", "price_max": null, "query_type": "general"}}
"""
    
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    
    try:
        # JSON çıkartmayı dene
        json_str = response.text.strip()
        # Eğer ```json``` bloğu varsa temizle
        json_str = re.sub(r'```json\n?|\n?```', '', json_str)
        result = json.loads(json_str)
        return result
    except json.JSONDecodeError:
        return {"intent": "other", "city": None, "room_type": None, "price_max": None, "query_type": "general"}

# --- AŞAMA 3: ROUTER LOGIC (CSV Filtreleme) ---
def search_ilanlar(intent_data: dict) -> list:
    """
    Intent'ten gelen verilere göre CSV'de arama yap
    """
    results = df_ilanlar.copy()
    
    # Şehir filtrelemesi
    if intent_data.get("city"):
        results = results[results["sehir"].str.contains(intent_data["city"], case=False, na=False)]
    
    # Oda sayısı filtrelemesi
    if intent_data.get("room_type"):
        results = results[results["oda_sayisi"].str.contains(intent_data["room_type"], case=False, na=False)]
    
    # Fiyat filtrelemesi (maksimum)
    if intent_data.get("price_max"):
        try:
            max_price = int(intent_data["price_max"])
            results = results[results["fiyat_tl"] <= max_price]
        except:
            pass
    
    # Bütçe sorgusu (uygun fiyat)
    if intent_data.get("query_type") == "budget":
        results = results[results["fiyat_tl"] < 10000000]
    
    # Lüks sorgusu
    elif intent_data.get("query_type") == "luxury":
        results = results[results["fiyat_tl"] > 35000000]
    
    return results.to_dict("records")

# --- AŞAMA 2: RESPONSE GENERATION ---
def generate_response(intent: dict, search_results: list) -> str:
    """
    Intent ve arama sonuçlarına göre cevap oluştur
    """
    intent_type = intent.get("intent")
    
    # Selamlaşma
    if intent_type == "greeting":
        return "🏠 Merhaba! Ben emlak asistanınız. Size bir ev bulmakta yardımcı olabilirim. Ne arıyorsunuz?"
    
    # Vedalaşma
    elif intent_type == "farewell":
        return "👋 Görüşmek üzere! İyi günler dilerim."
    
    # Teşekkür
    elif intent_type == "thanks":
        return "😊 Rica ederim! Başka bir şey sorabilirsiniz."
    
    # Ilan Arama
    elif intent_type == "search":
        if not search_results:
            return "😔 Maalesef sizin kriterlere uygun bir ilan bulamadım. Başka bir arama yapmak ister misiniz?"
        
        response = f"✅ **{len(search_results)} ilan buldum:**\n\n"
        for ilan in search_results[:5]:  # Max 5 sonuç
            response += f"""
🏠 **{ilan['baslik']}**
📍 Şehir: {ilan['sehir']}
🚪 Oda Sayısı: {ilan['oda_sayisi']}
💰 Fiyat: ₺{ilan['fiyat_tl']:,.0f}
✨ Özellikler: {ilan['ozellik']}
---
"""
        return response
    
    # Diğer
    else:
        return "🤔 Anlayamadım. Bir emlak ilanı arıyor musunuz? Örneğin: 'Kadıköy'de uygun daire bulabilir misin?'"

# --- STREAMLIT UI ---
st.set_page_config(page_title="🏠 Akıllı Emlak Asistanı", page_icon="🏠", layout="centered")
st.title("🏠 Akıllı Emlak Asistanı (AI Powered)")
st.markdown("**🤖 Gemini AI tarafından desteklenen akıllı arama sistemi**")

st.info("✨ Bu sistem yapay zekayı kullanarak sorularınızı anlıyor ve en uygun ilanları buluyor!")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesaj geçmişi
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcı girişi
if prompt := st.chat_input("Bir soru yazın... (Örn: Kadıköy'de 2+1 uygun daire var mı?)"):
    # Kullanıcı mesajı
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Bot yanıtı (Gemini AI tarafından)
    with st.chat_message("assistant"):
        with st.spinner("🤔 Analiz ediliyor..."):
            # 1. Intent Recognition (NLU)
            intent = extract_intent(prompt)
            
            # 2. Search (CSV Filtreleme)
            if intent.get("intent") == "search":
                results = search_ilanlar(intent)
            else:
                results = []
            
            # 3. Response Generation
            response = generate_response(intent, results)
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})

# Alt bilgiler
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.caption("💡 **Örnek Sorular:**")
    st.caption("• Merhaba\n• Kadıköy'de 2+1\n• Uygun fiyatlı ev\n• Lüks villa\n• Beşiktaş'ta ne var?")
with col2:
    st.caption("📊 **Sistem Hakkında:**")
    st.caption(f"✨ AI: Gemini Pro\n📈 Veri: {len(df_ilanlar)} İlan\n🏙️ Şehirler: {df_ilanlar['sehir'].nunique()}")
