from app import create_app
from app.models import City

app = create_app()

with app.app_context():
    cities = City.query.all()
    print(f"--- VERİTABANI KONTROLÜ ---")
    print(f"Toplam Şehir Sayısı: {len(cities)}")
    
    if len(cities) == 0:
        print("❌ HATA: Şehir tablosu BOMBOŞ! Bu yüzden dropdown boş geliyor.")
    else:
        for c in cities:
            print(f"✅ Bulunan Şehir: {c.city_name}")