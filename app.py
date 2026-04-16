import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import random

# Voiceflow web widget (Production). Normal HTML sitelerinde </body> öncesine yapıştırılır;
# Streamlit'te components.html ile yüklenir (balon bazen iframe içinde kalabilir).
VOICEFLOW_WIDGET_SNIPPET = """
<script type="text/javascript">
  (function(d, t) {
      var v = d.createElement(t), s = d.getElementsByTagName(t)[0];
      v.onload = function() {
        window.voiceflow.chat.load({
          verify: { projectID: '69e1057a5ccdc868b3923337' },
          url: 'https://general-runtime.voiceflow.com',
          versionID: 'production',
          voice: {
            url: "https://runtime-api.voiceflow.com"
          }
        });
      }
      v.src = "https://cdn.voiceflow.com/widget-next/bundle.mjs"; v.type = "text/javascript"; s.parentNode.insertBefore(v, s);
  })(document, 'script');
</script>
"""

# --- VERİ YÜKLEME ---
def load_data():
    try:
        df = pd.read_csv("ilanlar.csv")
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

# --- SIMPLE NLU (No API) ---
def extract_intent(user_input):
    """Keyword-based intent extraction"""
    query_lower = user_input.lower()
    
    # Greeting
    if any(word in query_lower for word in ["merhaba", "selam", "naber", "nasılsın"]):
        return {"is_searching": False}
    
    # Search
    cities = df_ilanlar["sehir"].unique().tolist()
    has_city = any(city.lower() in query_lower for city in cities)
    has_search_keyword = any(word in query_lower for word in ["ilan", "ev", "daire", "villa", "ara", "bul"])
    
    if has_city or has_search_keyword:
        filters = {}
        
        # City
        for city in cities:
            if city.lower() in query_lower:
                filters["sehir"] = city
                break
        
        # Budget
        if "ucuz" in query_lower or "uygun" in query_lower:
            filters["budget_type"] = "cheap"
        elif "lüks" in query_lower or "pahalı" in query_lower:
            filters["budget_type"] = "luxury"
        
        # Room type
        if "1+1" in query_lower:
            filters["room_type"] = "1+1"
        elif "2+1" in query_lower:
            filters["room_type"] = "2+1"
        elif "3+1" in query_lower:
            filters["room_type"] = "3+1"
        elif "4+1" in query_lower:
            filters["room_type"] = "4+1"
        
        return {"is_searching": True, "filters": filters}
    
    return {"is_searching": False}

# --- SEARCH ---
def search_listings(df, filters):
    """CSV'de arama yap"""
    if df.empty:
        return df
    
    res = df.copy()
    
    if filters.get("sehir"):
        res = res[res["sehir"].str.lower().str.contains(filters["sehir"].lower(), na=False)]
    
    if filters.get("room_type"):
        res = res[res["oda_sayisi"].astype(str).str.contains(filters["room_type"], na=False)]
    
    if filters.get("budget_type") == "cheap":
        res = res[res["fiyat_tl"] < 5000000]
    elif filters.get("budget_type") == "luxury":
        res = res[res["fiyat_tl"] > 30000000]
    
    return res

# --- UI ---
st.set_page_config(page_title="🏠 Akıllı Emlak Asistanı", page_icon="🏠", layout="centered")
st.title("🏠 Akıllı Emlak Asistanı")
st.markdown("**Demo Modu - No API Required** ✨")
st.write("İstediğiniz evi bana anlatın, ben sizin için bulayım!")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Örn: Beşiktaş'ta 2+1, maksimum 5 milyon TL"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        intent = extract_intent(prompt)
        
        if not intent.get("is_searching", False):
            response = "👋 Merhaba! Size nasıl yardımcı olabilirim? Aradığınız evin özelliklerini söyleyin."
            st.markdown(response)
        else:
            filters = intent.get("filters", {})
            results = search_listings(df_ilanlar, filters)
            
            if results.empty:
                response = "😔 Maalesef kriterlerinize uygun bir ilan bulamadım."
                st.markdown(response)
            else:
                response = f"✅ **{len(results)} ilan buldum:**\n\n"
                st.markdown(response)
                
                for idx, ilan in enumerate(results.head(5).to_dict("records"), 1):
                    st.markdown(f"""
🏠 **{idx}. {ilan.get('baslik', 'N/A')}**
📍 {ilan.get('sehir', 'N/A')} - {ilan.get('oda_sayisi', 'N/A')}
💰 ₺{ilan.get('fiyat_tl', 0):,.0f}
✨ {ilan.get('ozellik', 'N/A')}
---
""")
        
        st.session_state.messages.append({"role": "assistant", "content": response})

st.divider()
st.caption(f"📊 {len(df_ilanlar)} İlan | 🏙️ {df_ilanlar['sehir'].nunique()} Şehir")

with st.sidebar:
    st.caption(
        "Voiceflow danışmanı: sağ altta sohbet balonu görünmüyorsa, "
        "aynı script’i kendi HTML sitenizde `</body>` öncesine ekleyin "
        "(Streamlit sayfası iframe içinde çalıştığı için widget bazen kısıtlı kalabilir)."
    )

components.html(VOICEFLOW_WIDGET_SNIPPET, height=0)
