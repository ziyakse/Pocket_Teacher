from flask import Flask
from .models import db, Student, Question

# --- YENİ EKLENEN IMPORTLAR ---
from app.api.auth import auth_bp
from app.api.learning import learning_bp
from app.api.finance import finance_bp
from app.web import web_bp  # <-- İŞTE BU EKSİKTİ!
# ------------------------------

def create_app():
    app = Flask(__name__)
    
    # SQLite veritabanı ayarı
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pocket_teacher.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    # Blueprintleri sisteme kaydet
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(learning_bp, url_prefix='/api')
    app.register_blueprint(finance_bp, url_prefix='/api')
    
    # Web Dashboard (Admin Paneli)
    app.register_blueprint(web_bp) 
    
    with app.app_context():
        # Veritabanı tablolarını otomatik oluşturur
        db.create_all()
    
    # TEST ROTASI
    @app.route('/test-data')
    def test_data():
        student = Student.query.first()
        questions = Question.query.all()
        if not student:
            return "Veritabanı boş! Önce 'python seed.py' çalıştır."

        output = {
            "Student": f"{student.name} {student.last_name} ({student.account_type})",
            "Location": student.city.city_name,
            "Questions": [q.question_text for q in questions]
        }
        return output
        
    return app