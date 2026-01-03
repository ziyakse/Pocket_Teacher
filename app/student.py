from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import db, Student, Course, Module, Section, Question, LearningEventFact, AdaptiveState
from datetime import datetime

student_bp = Blueprint('student', __name__)

# 1. GİRİŞ SAYFASI (Login)
@student_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        user = Student.query.filter_by(email=email).first()
        
        if user:
            session['user_id'] = user.student_id
            session['user_name'] = user.name
            return redirect(url_for('student.home'))
        else:
            flash('Kullanıcı bulunamadı! (Örn: denis@example.com)', 'danger')
            
    return render_template('login.html')

# 2. ANA SAYFA (Dersler)
@student_bp.route('/home')
def home():
    if 'user_id' not in session: return redirect(url_for('student.login'))
    
    user_name = session['user_name']
    courses = Course.query.all()
    return render_template('home.html', user_name=user_name, courses=courses)

# 3. DERS DETAYI (Modüller) - PDF Sayfa 10
@student_bp.route('/course/<int:course_id>')
def course_detail(course_id):
    if 'user_id' not in session: return redirect(url_for('student.login'))
    
    course = Course.query.get_or_404(course_id)
    modules = Module.query.filter_by(course_id=course_id).all()
    
    return render_template('course_detail.html', course=course, modules=modules)

# 4. QUIZ EKRANI (H-1 ve H-3 Hedefleri) - PDF Sayfa 12
@student_bp.route('/module/<int:module_id>', methods=['GET', 'POST'])
def module_content(module_id):
    if 'user_id' not in session: return redirect(url_for('student.login'))
    
    module = Module.query.get_or_404(module_id)
    # İlk quiz bölümünü buluyoruz
    section = Section.query.filter_by(module_id=module_id).first()
    
    if not section:
        flash("Bu modülde henüz içerik yok.", "warning")
        return redirect(url_for('student.course_detail', course_id=module.course_id))

    questions = Question.query.filter_by(section_id=section.section_id).all()

    # Öğrenci cevapları gönderdiğinde:
    if request.method == 'POST':
        correct_count = 0
        
        for q in questions:
            user_answer = request.form.get(f'question_{q.question_id}')
            is_correct = (user_answer == q.question_answer)
            if is_correct: correct_count += 1
            
            # [H-3] Analitik Verisi Kaydet
            event = LearningEventFact(
                student_id=session['user_id'],
                question_id=q.question_id,
                is_correct=is_correct,
                timestamp=datetime.utcnow()
            )
            db.session.add(event)
            
        # [H-1] AI Geri Bildirimi
        if correct_count == len(questions):
            flash("🏆 Mükemmel! Tüm sorular doğru. Yapay zeka seviyeni yükseltiyor.", "success")
        else:
            flash(f"⚠️ {len(questions)} sorudan {correct_count} tanesini bildin. Biraz daha tekrar yapalım.", "warning")
            
        db.session.commit()
        return redirect(url_for('student.course_detail', course_id=module.course_id))

    return render_template('quiz.html', module=module, questions=questions)

@student_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('student.login'))

# 5. BAŞARILAR SAYFASI (Gamification) - PDF Sayfa 9
@student_bp.route('/achievements')
def achievements():
    if 'user_id' not in session: return redirect(url_for('student.login'))
    
    user_name = session['user_name']
    
    # Basit bir başarı algoritması:
    # Öğrencinin toplam doğru cevap sayısını bulalım
    total_correct = LearningEventFact.query.filter_by(
        student_id=session['user_id'], 
        is_correct=True
    ).count()
    
    # Rozet Durumları (Mock Data)
    # Gerçekte bunlar modül bazlı hesaplanabilir ama şimdilik toplama göre yapalım
    badges = [
        {"name": "Yeni Başlayan", "desc": "İlk doğru cevabını ver.", "locked": total_correct < 1, "icon": "🌱"},
        {"name": "Hızlı Öğrenci", "desc": "5 doğru cevap ver.", "locked": total_correct < 5, "icon": "🚀"},
        {"name": "Matematik Dehası", "desc": "10 doğru cevap ver.", "locked": total_correct < 10, "icon": "🧠"},
        {"name": "Efsane", "desc": "50 doğru cevap ver.", "locked": total_correct < 50, "icon": "👑"}
    ]
    
    return render_template('achievements.html', user_name=user_name, badges=badges, total_correct=total_correct)