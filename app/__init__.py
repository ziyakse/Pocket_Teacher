import os
from flask import Flask
from flask_mail import Mail
from app.models import db 

mail = Mail()

def create_app():
    app = Flask(__name__)
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'pocket_teacher.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = "cok_gizli_bir_anahtar_buraya_yaz"

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    
    db.init_app(app)
    mail.init_app(app)

    from app.student import student_bp
    from app.api.learning import learning_bp
    from app.api.auth import auth_bp
    from app.api.finance import finance_bp
    from app.web import web_bp

    app.register_blueprint(student_bp)
    app.register_blueprint(learning_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(finance_bp, url_prefix='/api')
    app.register_blueprint(web_bp)

    with app.app_context():
        db.create_all()

    return app