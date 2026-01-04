import os
from flask import Flask
from flask_mail import Mail
# DB nesnesini models.py'den alıyoruz ki çakışma olmasın
from app.models import db 

# Mail nesnesini burada oluşturuyoruz (student.py buradan çekecek)
mail = Mail()

def create_app():
    app = Flask(__name__)
    
    # --- TEMEL AYARLAR ---
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'pocket_teacher.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = "cok_gizli_bir_anahtar_buraya_yaz"

    # --- MAIL AYARLARI (.env dosyasından okur) ---
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    
    # --- BAŞLATMA ---
    db.init_app(app)   # Veritabanını bağla
    mail.init_app(app) # Mail servisini bağla

    # --- BLUEPRINTLER (En Alta Saklanan Importlar) ---
    # "Circular Import" hatasını çözen sihirli yer burası!
    # Bu satırlar fonksiyonun en sonunda olmazsa hata verir.
    
    from app.student import student_bp
    from app.api.learning import learning_bp
    from app.api.auth import auth_bp
    from app.api.finance import finance_bp
    from app.web import web_bp

    # Hepsini Kaydet
    app.register_blueprint(student_bp)
    app.register_blueprint(learning_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(finance_bp, url_prefix='/api')
    app.register_blueprint(web_bp)

    # Veritabanı tablolarını oluştur (Eğer yoksa)
    with app.app_context():
        db.create_all()

    return app