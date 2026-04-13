# Basit bir Python hesap makinesi uygulaması

while True:
    try:
        # Kullanıcıdan giriş al
        num1 = float(input("İlk sayıyı girin: "))
        operator = input("İşlemi seçin (+, -, *, /): ")
        num2 = float(input("İkinci sayıyı girin: "))
        
        # İşlem yap
        if operator == '+':
            result = num1 + num2
        elif operator == '-':
            result = num1 - num2
        elif operator == '*':
            result = num1 * num2
        elif operator == '/':
            if num2 == 0:
                print("Hata: Sıfıra bölme işlemi yapılamaz!")
                continue
            result = num1 / num2
        else:
            print("Geçersiz işlem! Lütfen (+, -, *, /) sembollerinden birini seçin.")
            continue
        
        # Sonucu göster
        print(f"Sonuç: {result}")
        
        # Yeni işlem yapmak isteyip istemediğini sor
        again = input("Yeni bir işlem yapmak istiyor musunuz? (e/h): ").lower()
        if again != 'e':
            print("Hesap makinesi kapatılıyor...")
            break
    
    except ValueError:
        print("Hata: Geçerli bir sayı girin!")
    except Exception as e:
        print(f"Bir hata oluştu: {e}")
