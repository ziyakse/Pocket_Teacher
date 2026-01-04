from app import create_app
from app.models import db, Student

app = create_app()

def list_users():
    with app.app_context():
        # Tüm öğrencileri veritabanından çek
        users = Student.query.all()
        
        print("\n" + "="*50)
        print(f"👥 VERİTABANINDA KAYITLI {len(users)} KULLANICI VAR")
        print("="*50)
        
        for user in users:
            print(f"🆔 ID: {user.student_id}")
            print(f"👤 İsim: {user.name} {user.last_name}")
            print(f"📧 Email: {user.email}")
            print(f"🔑 Şifre (Hash): {user.password_hash[:20]}...") # Şifrenin sadece başını gösteriyoruz
            print(f"🏙️  Şehir ID: {user.city_id}")
            print("-" * 30)

if __name__ == "__main__":
    list_users()