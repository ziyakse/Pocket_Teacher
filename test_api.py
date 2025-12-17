import requests

BASE_URL = "http://127.0.0.1:5000/api"

def test_login():
    print("--- Login Testi ---")
    payload = {"email": "denis@example.com"}
    response = requests.post(f"{BASE_URL}/login", json=payload)
    
    if response.status_code == 200:
        print("✅ Başarılı:", response.json())
    else:
        print("❌ Hata:", response.text)

def test_courses():
    print("\n--- Dersleri Listeleme Testi ---")
    response = requests.get(f"{BASE_URL}/courses")
    
    if response.status_code == 200:
        print("✅ Başarılı:", response.json())
    else:
        print("❌ Hata:", response.text)

def test_submit_answer():
    print("\n--- Soru Cevaplama Testi (AI Mantığı) ---")
    
    # Denis (id:1), Soru 1'e (Cevap: 18) doğru cevap veriyor mu?
    payload = {
        "student_id": 1,
        "question_id": 1,
        "answer": "18" 
    }
    
    response = requests.post(f"{BASE_URL}/submit_answer", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Cevap Gönderildi: {result['result']}")
        print(f"🤖 AI Mesajı: {result['message']}")
    else:
        print(f"❌ Hata ({response.status_code}):", response.text)

def test_purchase():
    print("\n--- Sosyal Etki (Satın Alma) Testi ---")
    
    # H-2 Senaryosu: Denis (id:1) 100 TL'lik paket alıyor
    # [cite_start]Sistem arkada Ali'yi (Van'daki öğrenciyi) bulup Premium yapmalı [cite: 106]
    payload = {
        "student_id": 1,
        "amount": 100.0
    }
    
    response = requests.post(f"{BASE_URL}/purchase", json=payload)
    
    if response.status_code == 200:
        print("✅", response.json()['message'])
        print("❤️", response.json()['social_impact'])
    else:
        print("❌ Hata:", response.text)

if __name__ == "__main__":
    # Öncekileri şimdilik çalıştırmasın diye önüne # koyduk
    # test_login()
    # test_courses()
    # test_submit_answer()
    
    # Sadece yenisini test edelim
    test_purchase()