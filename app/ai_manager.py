import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# --- SENİN HESABINDA VAR OLAN MODELLER ---
# test_ai.py çıktısına göre güncellendi.
CANDIDATE_MODELS = [
    "gemini-flash-latest",       # Senin listende bu vardı (En yüksek ihtimal)
    "gemini-pro-latest",         # Bu da vardı
    "gemini-2.0-flash-exp",      # Bu vardı (Kota sorunu olabilir ama denemeye değer)
    "gemini-2.0-flash-lite-preview-02-05",
    "gemini-1.5-flash"           # Standart (Yedek)
]

def generate_question_from_ai(topic, difficulty_level, student_age=10, count=1):
    prompt_text = f"""
    Sen {student_age} yaşındaki bir öğrenci için eğlenceli bir öğretmensin.
    
    Lütfen aşağıdaki kriterlere göre TAM OLARAK {count} ADET çoktan seçmeli soru hazırla:
    - Konu: {topic}
    - Zorluk Seviyesi (1-5 arası): {difficulty_level}
    
    ÖNEMLİ: Cevabı sadece ve sadece geçerli bir JSON DİZİSİ (Array) formatında ver. 
    Başka hiçbir metin, açıklama veya markdown (```json) kullanma.
    
    İstenen JSON Formatı:
    [
        {{
            "question_text": "Soru metni...",
            "question_answer": "Doğru",
            "wrong_answer_1": "Yanlış 1",
            "wrong_answer_2": "Yanlış 2"
        }}
    ]
    Soruları Türkçe hazırla.
    """

    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {"temperature": 0.7, "response_mime_type": "application/json"}
    }
    
    if not api_key:
        print("❌ HATA: API Key bulunamadı!")
        return None

    # --- GÜVENLİ URL YAPISI ---
    part1 = "https://"
    part2 = "generativelanguage.googleapis.com"
    part3 = "/v1beta/models/"
    
    for model_name in CANDIDATE_MODELS:
        # URL Birleştirme
        final_url = f"{part1}{part2}{part3}{model_name}:generateContent"
        params = {'key': api_key}
        
        try:
            # print(f"Deneniyor: {model_name}...") 
            response = requests.post(final_url, params=params, headers={"Content-Type": "application/json"}, json=payload)
            
            if response.status_code != 200:
                print(f"⚠️ {model_name} başarısız (Kod: {response.status_code})...")
                continue 
            
            # --- BAŞARILI ---
            print(f"✅ BAŞARILI MODEL: {model_name}")
            
            result_json = response.json()
            
            if 'candidates' not in result_json: continue

            raw_text = result_json['candidates'][0]['content']['parts'][0]['text']
            clean_text = raw_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_text)
            
            if isinstance(data, dict):
                return [data]
            return data
            
        except Exception as e:
            print(f"Hata ({model_name}): {e}")
            continue

    print("❌ TÜM MODELLER BAŞARISIZ OLDU.")
    return None