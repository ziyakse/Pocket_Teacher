import google.generativeai as genai
import os

API_KEY = "AIzaSyANN9KUf-NBkj6QLw_1ytZZV5jyut_KAKo"

genai.configure(api_key=API_KEY)

print("--- Mevcut Modeller Listeleniyor ---")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Hata: {e}")