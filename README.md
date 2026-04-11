# 🏠 AI Emlak Satış Asistanı

Streamlit ve OpenAI API kullanarak yazılmış yapay zeka destekli emlak danışman chatbotu.

## 📋 Özellikleri

- 🤖 **AI Powered**: GPT-4o modeli ile akıllı cevaplar
- 🔍 **Vektör Arama**: FAISS ile semantik arama (anlamsal olarak benzer ilanları bulur)
- 💬 **Chat Interface**: Streamlit ile modern chat arayüzü
- 🏘️ **İlan Verisi**: 10 adet örnek İstanbul emlak ilanı
- ⚡ **Hızlı Cevaplar**: LangChain RAG (Retrieval-Augmented Generation) zincirleme

## 🚀 Kurulum

### 1. Gerekli Yazılımlar

- Python 3.8+ ([indirin](https://www.python.org/downloads/))
- OpenAI API Key ([buradan alın](https://platform.openai.com/api-keys))

### 2. Projeyi Klonlayın/Açın

```bash
cd emlak
```

### 3. Virtual Environment Oluşturun (Opsiyonel ama Önerilir)

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:
```bash
python -m venv venv
source venv/bin/activate
```

### 4. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### 5. .env Dosyasını Oluşturun

`.env.example` dosyasını kopyalayarak `.env` adında yeni bir dosya oluşturun:

```bash
copy .env.example .env
```

Ardından `.env` dosyasını açıp `OPENAI_API_KEY` kısmını kendi API anahtarınızla değiştirin:

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
```

## 🎯 Kullanım

### Lokal Çalıştırma

```bash
streamlit run app.py
```

Tarayıcınız otomatik olarak `http://localhost:8501` adresinde açılacak.

### Örnek Sorular

Chatbota şunlar gibi sorular sorun:

- "Boğaz manzarası olan bir evi var mı?"
- "5 milyon TL'nin altında deniz manzaralı daire?"
- "En pahalı villa hangisi?"
- "Üsküdar'da evler var mı?"
- "Öğrenciye uygun ucuz bir daire bul"
- "Havuzlu ev istiyorum"

## 🌐 Streamlit Cloud'da Deploy Etme

### 1. GitHub'a Yükleyin

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/emlak-ai.git
git push -u origin main
```

### 2. Streamlit Cloud'a Bağlanın

1. [Streamlit Cloud](https://share.streamlit.io/)'a gidin
2. GitHub hesabınızla oturum açın
3. "New app" butonuna tıklayın
4. Repository, branch ve main file path'i seçin (`app.py`)
5. "Deploy" butonuna tıklayın

### 3. Secrets Ekleyin

1. Deploy edildikten sonra ⚙️ Settings butonuna tıklayın
2. "Secrets" sekmesine gidin
3. Şu formatı kullanarak OpenAI API key'i ekleyin:

```
OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxx"
```

## 📁 Dosya Yapısı

```
emlak/
├── app.py                  # Ana Streamlit uygulaması
├── requirements.txt        # Python bağımlılıkları
├── .env.example           # API key şablonu
├── .env                    # API key'i buraya yazın (gitignore'da)
├── .gitignore             # .env dosyasını push'tan koru
└── README.md              # Bu dosya
```

## ⚙️ Teknik Detaylar

### Teknoloji Stack'i

- **Streamlit**: Web arayüzü
- **LangChain**: LLM orchestration
- **OpenAI**: GPT-4o model
- **FAISS**: Vektör arama/similarity search
- **python-dotenv**: Environment variables yönetimi

### Sistem Akışı

```
Kullanıcı Sorusu
       ↓
   FAISS Vektör Arama (Benzer ilanları bul)
       ↓
   Prompt Template (Danışman kişiliği ile hazırla)
       ↓
   OpenAI GPT-4o (Cevap oluştur)
       ↓
   Chat UI'da Göster
```

### Prompt Engineering

Chatbot, profesyonel bir emlak danışmanı gibi davranacak şekilde yazılmıştır. Sistem prompt'u:

> "Sen profesyonel, nazik ve ikna edici bir gayrimenkul satış danışmanısın. Görevin, kullanıcının sorularına elindeki ilanları kullanarak cevap vermek. Eğer cevap verecek uygun bir ilan yoksa, nazikçe başka bir bölge sor veya iletişim bilgilerini bırakmalarını iste. Asla uydurma bilgi verme, sadece verilen ilanlara sadık kal."

## 🐛 Sorun Giderme

### "OPENAI_API_KEY not found"
- `.env` dosyasının proje kökünde olduğunu kontrol edin
- API key'i doğru formatta yazıp yazmadığınızı kontrol edin

### Yavaş Cevaplar
- OpenAI API'nin yüklü olduğu kontrol edin
- İnternet bağlantınızı kontrol edin

### FAISS Hatası
- CPU sürümü kullanıyorsunuz: `faiss-cpu==1.7.4`
- GPU sürümü istersek: `pip install faiss-gpu` (CUDA gerekli)

## 📊 İlan Verisi Nasıl Değiştirilir

`app.py` dosyasında `ilan_verileri` listesini düzenleyerek yeni ilanlar ekleyebilirsiniz:

```python
ilan_verileri = [
    "Başlık: ... Fiyat: ... Özellik: ...",
    "Başlık: ... Fiyat: ... Özellik: ...",
    # Daha fazla ilana ekle
]
```

## 💰 Maliyet Tahmini

OpenAI API kullanım ücretleri:
- **Embedding**: ~$0.02 per 1M tokens
- **GPT-4o**: ~$0.03 per 1K input tokens, ~$0.06 per 1K output tokens

Aylık 100 sorgu için tahmini maliyet: ~$1-2

## 📞 İletişim & Destek

Herhangi bir sorunuz varsa, bu dosyayı güncelleyebilirsiniz.

## 📄 Lisans

MIT License

---

**Hazırlayan**: AI Emlak Danışmanı  
**Güncelleme Tarihi**: 2024
