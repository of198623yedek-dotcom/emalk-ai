import streamlit as st
import time

# Mock verileri (API key gerekli değil!)
ILANLAR = {
    "Beşiktaş": {
        "title": "Beşiktaş'ta Deniz Manzaralı 3+1",
        "price": "15.000.000 TL",
        "details": "Boğaz manzarası, yeni bina, geniş balkon, asansör, güvenlik sistemi"
    },
    "Kadıköy": {
        "title": "Kadıköy'de Modern Daire",
        "price": "7.500.000 TL",
        "details": "2+1, metroya yakın, deprem yönetmeliğine uygun, bahçeli"
    },
    "Sarıyer": {
        "title": "Sarıyer'de Müstakil Villa",
        "price": "45.000.000 TL",
        "details": "Havuzlu, bahçeli, 5+2, ultra lüks, özel bahçe işçisi"
    },
    "Şişli": {
        "title": "Şişli'de Rezidans Dairesi",
        "price": "12.000.000 TL",
        "details": "1+1, fitness salonu, güvenlikli, merkezi konum, 24 saat bekçi"
    },
    "Üsküdar": {
        "title": "Üsküdar'da Tarihi Ev",
        "price": "8.000.000 TL",
        "details": "3+1, restore edilmiş, yüksek tavanlı, nostaljik, tarihi değer"
    },
    "Beyoğlu": {
        "title": "Beyoğlu'nda Loft Daire",
        "price": "10.000.000 TL",
        "details": "2+1, yüksek tavan, sanat galerisine yakın, modern tasarım"
    },
    "Bakırköy": {
        "title": "Bakırköy'de Deniz Manzaralı 4+1",
        "price": "18.000.000 TL",
        "details": "Geniş aileler için uygun, deniz cepheli, balkonlu"
    },
    "Maltepe": {
        "title": "Maltepe'de Sahil Sıfır Daire",
        "price": "9.000.000 TL",
        "details": "3+1, deniz manzaralı, balkonlu, denize 50m"
    },
    "Zeytinburnu": {
        "title": "Zeytinburnu'da İdeal Daire",
        "price": "6.500.000 TL",
        "details": "1+1, öğrenciye uygun, ulaşım kolay, yakında üniversite"
    },
    "Başakşehir": {
        "title": "Başakşehir'de Bahçeli Ev",
        "price": "11.000.000 TL",
        "details": "4+1, müstakil bahçe, çocuk oyun alanı mevcut, yeşil alan"
    }
}

def find_relevant_listings(query):
    """Sorguya göre ilgili ilanları bul"""
    query_lower = query.lower()
    relevant = []
    
    # Anahtar kelimelere göre eşleştir
    for region, listing in ILANLAR.items():
        combined_text = (listing["title"] + " " + listing["details"]).lower()
        
        # Fiyat sorgusu
        if "ucuz" in query_lower or "uygun" in query_lower:
            if int(listing["price"].split(".")[0]) < 10:
                relevant.append(listing)
        # Pahalı sorgusu
        elif "pahalı" in query_lower or "lüks" in query_lower:
            if int(listing["price"].split(".")[0]) > 35:
                relevant.append(listing)
        # Bölge sorgusu
        elif region.lower() in query_lower:
            relevant.append(listing)
        # Özellik sorgusu
        elif any(keyword in combined_text for keyword in ["deniz", "havuz", "bahçe", "balkon", "metroya"]):
            if any(keyword in query_lower for keyword in ["deniz", "havuz", "bahçe", "balkon", "metroya"]):
                relevant.append(listing)
    
    return relevant if relevant else list(ILANLAR.values())[:3]

def generate_response(query):
    """Sorguya göre cevap oluştur"""
    listings = find_relevant_listings(query)
    
    response = "🏠 **Mevcut İlanlar:**\n\n"
    
    for i, listing in enumerate(listings, 1):
        response += f"**{i}. {listing['title']}**\n"
        response += f"💰 Fiyat: {listing['price']}\n"
        response += f"✨ Özellikler: {listing['details']}\n\n"
    
    response += "---\n"
    response += "📞 Daha fazla bilgi için bizimle iletişime geçebilirsiniz!\n"
    response += "💬 Başka sorularınız varsa devam edebiliriz."
    
    return response

# =================== STREAMLIT UI ===================

st.set_page_config(
    page_title="🏠 AI Emlak Danışmanı", 
    page_icon="🏠",
    layout="centered"
)

st.title("🏠 AI Emlak Satış Asistanı")
st.subheader("Hayalinizdeki evi bulmanıza yardımcı olayım!")

# Info badge
st.info("📌 **Demo Modu** - Ücretsiz test sürümü. Gerçek projede AI güçlendirilecektir!")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Geçmiş mesajları göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcı girişi
if prompt := st.chat_input("Nasıl bir ev bakıyorsunuz?"):
    # Kullanıcı mesajı
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Bot cevabı
    with st.chat_message("assistant"):
        # Spinner efekti
        with st.spinner("🤔 İlanları tarayıyorum..."):
            time.sleep(1)  # İnsan gibi tepki süresi
            response = generate_response(prompt)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# Alt bilgi
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.caption("💡 **Örnek Sorular:**")
    st.caption("• Deniz manzarası var mı?\n• Ucuz daireler?\n• En pahalı villa?\n• Beşiktaş'ta ne var?")
with col2:
    st.caption("📊 **Mevcut İlanlar:**")
    st.caption(f"Toplam {len(ILANLAR)} İlan\n📍 10 Farklı Bölge\n💰 6.5M - 45M TL Arası")
