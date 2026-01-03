from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Veritabanı objesini burada oluşturuyoruz
db = SQLAlchemy()

# --- OPERASYONEL KATMAN (Boyut Tabloları) ---

class City(db.Model):
    __tablename__ = 'cities'
    city_id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(100), nullable=False)
    country_name = db.Column(db.String(100), nullable=False)
    is_disadvantaged = db.Column(db.Boolean, default=False) 
    
    students = db.relationship('Student', backref='city', lazy=True)

class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.city_id'), nullable=False)
    birth_date = db.Column(db.Date)
    grade = db.Column(db.Integer)
    account_type = db.Column(db.String(50), default='Free') 
    
    # İlişkiler
    adaptive_state = db.relationship('AdaptiveState', backref='student', uselist=False)

class Course(db.Model):
    __tablename__ = 'courses'
    course_id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    grade_level = db.Column(db.Integer)
    source_link = db.Column(db.Text) 

    modules = db.relationship('Module', backref='course', lazy=True)

class Module(db.Model):
    __tablename__ = 'modules'
    module_id = db.Column(db.Integer, primary_key=True)
    module_name = db.Column(db.String(100), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'), nullable=False)
    content_type = db.Column(db.String(30))

    sections = db.relationship('Section', backref='module', lazy=True)

class Section(db.Model):
    __tablename__ = 'sections'
    section_id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.module_id'), nullable=False)
    section_name = db.Column(db.String(100))
    section_content = db.Column(db.Text)

    questions = db.relationship('Question', backref='section', lazy=True)

class Question(db.Model):
    __tablename__ = 'questions'
    question_id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.section_id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_answer = db.Column(db.String(100))
    difficulty_score = db.Column(db.Integer) 
    topic = db.Column(db.String(50))

    # --- YENİ EKLENEN SÜTUN ---
    # Şıkların hepsini (A, B, C) metin olarak burada tutacağız
    options = db.Column(db.Text, nullable=True) 
    # --------------------------

# --- ANALİTİK VE İŞ MANTIĞI KATMANI ---

class LearningEventFact(db.Model):
    __tablename__ = 'learning_event_fact'
    event_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id'), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    student_rel = db.relationship('Student', backref='events')
    question_rel = db.relationship('Question', backref='events')

class AdaptiveState(db.Model):
    __tablename__ = 'adaptive_state'
    state_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), unique=True, nullable=False)
    current_module_id = db.Column(db.Integer, db.ForeignKey('modules.module_id'))
    next_recommended_module_id = db.Column(db.Integer, db.ForeignKey('modules.module_id'))

class FinancialTransaction(db.Model):
    __tablename__ = 'financial_transactions'
    transaction_id = db.Column(db.Integer, primary_key=True)
    purchaser_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    supported_user_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=True)
    transaction_type = db.Column(db.String(50)) 
    purchase_amount = db.Column(db.Float)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)