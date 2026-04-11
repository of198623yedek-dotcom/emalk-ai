import streamlit as st
import random

# --- 1. VERİ SETİ (Gerçek bir veritabanı gibi düşün) ---
ilanlar = [
    {"id": 1, "baslik": "Beşiktaş'ta Deniz Manzaralı 3+1", "fiyat": "15.000.000 TL", "ozellik": "Boğaz manzarası, yeni bina, geniş balkon"},
    {"id": 2, "baslik": "Kadıköy'de Modern Daire", "fiyat": "7.500.000 TL", "ozellik": "2+1, metroya yakın, deprem yönetmeliğine uygun"},
    {"id": 3, "baslik": "Sarıyer'de Müstakil Villa", "fiyat": "45.000.000 TL", "ozellik": "Havuzlu, bahçeli, 5+2, ultra lüks"},
    {"id": 4, "baslik": "Şişli'de Rezidans Dairesi", "fiyat": "12.000.000 TL", "ozellik": "1+1, fitness salonu, güvenlikli, merkezi konum"},
    {"id": 5, "baslik": "Üsküdar'da Tarihi Ev", "fiyat": "8.000.000 TL", "ozellik": "3+1, restore edilmiş, yüksek tavanlı, nostaljik"},
    {"id": 6, "baslik": "Beyoğlu'nda Loft Daire", "fiyat": "10.000.000 TL", "ozellik": "2+1, yüksek tavan, sanat galerisine yakın, modern"},
    {"id": 7, "baslik": "Bakırköy'de Deniz Manzaralı 4+1", "fiyat": "18.000.000 TL", "ozellik": "Geniş aileler için uygun, deniz cepheli"},
    {"id": 8, "baslik": "Maltepe'de Sahil Sıfır Daire", "fiyat": "9.000.000 TL", "ozellik": "3+1, deniz manzaralı, balkonlu"},
    {"id": 9, "baslik": "Zeytinburnu'da İdeal Daire", "fiyat": "6.500.000 TL", "ozellik": "1+1, öğrenciye uygun, ulaşım kolay"},
    {"id": 10, "baslik": "Başakşehir'de Bahçeli Ev", "fiyat": "11.000.000 TL", "ozellik": "4+1, müstakil bahçe, çocuk oyun alanı mevcut"},
]

# --- 2. CHATBOT MANTIĞI (Zeka Katmanı) ---
def chatbot_cevap_ver(user_input):
    user_input = user_input.lower().strip()
    
    # Senaryo A: Selamlaşma veya Genel Sorular
    selamlasma_kelimeleri = ["merhaba", "selam", "naber", "nasılsın", "kimsin", "adın ne", "kim", "hi", "hello"]
    if any(kelime in user_input for kelime in selamlasma_kelimeleri):
        cevaplar = [
            "🏠 Merhaba! Ben emlak asistanınız. Size nasıl yardımcı olabilirim?",
            "👋 Selam! Ben harika hissediyorum, size en uygun ilanları bulmak için hazırım. Siz nasılsınız?",
            "🏡 Merhaba, ben emlak botu. İlanlar hakkında bilgi almak ister misiniz?",
            "💬 Merhaba! Hoş geldiniz. Emlak konusunda her türlü sorunuza yanıt verebilirim.",
        ]
        return random.choice(cevaplar)

    # Senaryo B: Vedalaşma
    vedalaşma_kelimeleri = ["baybay", "görüşürüz", "hoşça kal", "bye", "goodbye", "tekrar görüşmek üzere"]
    if any(kelime in user_input for kelime in vedalaşma_kelimeleri):
        return "👋 Görüşmek üzere! İyi günler dilerim. Başka bir zaman tekrar yazabilirsiniz!"

    # Senaryo C: Teşekkür
    tesekküre_kelimeleri = ["teşekkür", "sağol", "sağolun", "thanks", "thank you", "çok sağol"]
    if any(kelime in user_input for kelime in tesekküre_kelimeleri):
        return "😊 Rica ederim! Size yardımcı olabilmekten mutluyum. Başka bir şey sorabilirsiniz!"

    # Senaryo D: İlan Sorgulama (Anahtar Kelime Kontrolü)
    ilan_anahtar_kelimeler = ["ilan", "ev", "daire", "satılık", "fiyat", "villa", "bak", "göster", "var", "kaç", "bulabilir", "ara"]
    
    if any(kelime in user_input for kelime in ilan_anahtar_kelimeler):
        # Fiyat aralığı sorgulama
        if "ucuz" in user_input or "uygun" in user_input:
            ucuz_ilanlar = [i for i in ilanlar if int(i["fiyat"].split(".")[0]) < 10]
            if ucuz_ilanlar:
                liste_metni = ""
                for ilan in ucuz_ilanlar:
                    liste_metni += f"🏠 **{ilan['baslik']}**\n💰 Fiyat: {ilan['fiyat']}\n✨ Özellik: {ilan['ozellik']}\n\n"
                return f"💡 Uygun fiyatlı ilanlarımız:\n\n{liste_metni}"
        
        # Pahalı/Lüks sorgulama
        if "pahalı" in user_input or "lüks" in user_input or "harika" in user_input:
            pahalı_ilanlar = [i for i in ilanlar if int(i["fiyat"].split(".")[0]) > 35]
            if pahalı_ilanlar:
                liste_metni = ""
                for ilan in pahalı_ilanlar:
                    liste_metni += f"🏠 **{ilan['baslik']}**\n💰 Fiyat: {ilan['fiyat']}\n✨ Özellik: {ilan['ozellik']}\n\n"
                return f"👑 Lüks ilanlarımız:\n\n{liste_metni}"
        
        # Bölge sorgulaması
        bolge_ilanlari = []
        for ilan in ilanlar:
            if any(bolge in ilan["baslik"].lower() for bolge in ["beşiktaş", "kadıköy", "üsküdar", "sarıyer", "şişli", "beyoğlu", "bakırköy", "maltepe", "zeytinburnu", "başakşehir"]):
                for bolge_kelime in user_input.split():
                    if bolge_kelime in ilan["baslik"].lower():
                        bolge_ilanlari.append(ilan)
                        break
        
        if bolge_ilanlari:
            liste_metni = ""
            for ilan in bolge_ilanlari:
                liste_metni += f"🏠 **{ilan['baslik']}**\n💰 Fiyat: {ilan['fiyat']}\n✨ Özellik: {ilan['ozellik']}\n\n"
            return f"📍 Bulduğum ilanlar:\n\n{liste_metni}"
        
        # Varsayılan: Tüm ilanları göster
        liste_metni = ""
        for ilan in ilanlar:
            liste_metni += f"🏠 **{ilan['baslik']}**\n💰 Fiyat: {ilan['fiyat']}\n✨ Özellik: {ilan['ozellik']}\n\n"
        return f"📋 Tüm güncel ilanlarımız:\n\n{liste_metni}"

    # Senaryo E: Hiçbir Şey Anlamazsa (Varsayılan Cevap)
    yanıtlar = [
        "🤔 Anlayamadım. Ama isterseniz size emlak ilanlarımızı gösterebilirim. 'İlanları göster' yazabilirsiniz.",
        "💭 Pardon, daha net bir soru sorabilir misiniz? Örneğin 'ucuz daireler' veya 'Beşiktaş'ta ne var?'",
        "❓ Anlamadım, ama ev arama konusunda yardımcı olabilirim! Sorularınızı yazabilirsiniz.",
        "🏠 İlanlar hakkında soru sormak isterseniz yardımcı olabilirim!",
    ]
    return random.choice(yanıtlar)

# --- 3. STREAMLIT ARAYÜZÜ ---
st.set_page_config(page_title="🏠 Akıllı Emlak Asistanı", page_icon="🏠", layout="centered")
st.title("🏠 Akıllı Emlak Asistanı")
st.markdown("**Merhaba! Size en uygun evi bulmak için buradayım.** 😊")

# Info badge
st.info("📌 **Demo Modu** - Gerçek proje OpenAI API entegrasyonu ile geliştirilecektir!")

# Sohbet geçmişini başlat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Eski mesajları ekrana bas
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcıdan mesaj al
if prompt := st.chat_input("Bir şeyler yazın... (Örn: Merhaba, Ucuz daireler, Beşiktaş'ta ne var?)"):
    # Kullanıcı mesajını ekrana ekle
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Botun cevabını hesapla
    response = chatbot_cevap_ver(prompt)

    # Bot mesajını ekrana ekle
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Alt bilgi
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.caption("💡 **Örnek Sorular:**")
    st.caption("• Merhaba\n• Ucuz daireler\n• Beşiktaş'ta ne var?\n• Lüks villalar\n• İlanları göster")
with col2:
    st.caption("📊 **Hakkında:**")
    st.caption(f"Toplam {len(ilanlar)} İlan\n📍 10 Farklı Bölge\n💰 6.5M - 45M TL")
