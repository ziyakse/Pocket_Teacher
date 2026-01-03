# app/student.py

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import db, Student, Course, Module, Section, Question, LearningEventFact, AdaptiveState
from datetime import datetime

student_bp = Blueprint('student', __name__)

# --- YARDIMCI FONKSİYON: İLERLEME HESAPLA ---
def calculate_progress(student_id, course_id=None, module_id=None):
    """
    Verilen ders veya modül için öğrencinin ilerleme yüzdesini hesaplar.
    Mantık: (Çözülen Benzersiz Doğru Soru Sayısı / Toplam Soru Sayısı) * 100
    """
    # 1. Toplam Soru Sayısını Bul
    query = Question.query.join(Section).join(Module)
    
    if course_id:
        query = query.filter(Module.course_id == course_id)
    if module_id:
        query = query.filter(Module.module_id == module_id)
        
    total_questions = query.count()
    
    if total_questions == 0:
        return 0 # Soru yoksa ilerleme 0'dır
        
    # 2. Öğrencinin Doğru Bildiği (Tekil) Soru Sayısını Bul
    # (Aynı soruyu 5 kere çözse de 1 sayılır)
    solved_query = db.session.query(LearningEventFact.question_id).join(Question).join(Section).join(Module)
    
    solved_query = solved_query.filter(
        LearningEventFact.student_id == student_id,
        LearningEventFact.is_correct == True
    )
    
    if course_id:
        solved_query = solved_query.filter(Module.course_id == course_id)
    if module_id:
        solved_query = solved_query.filter(Module.module_id == module_id)
    
    # distinct() ile aynı soruyu tekrar tekrar saymayı engelliyoruz
    solved_count = solved_query.distinct().count()
    
    # 3. Yüzdeyi Hesapla
    percentage = int((solved_count / total_questions) * 100)
    return percentage

# ----------------------------------------------

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
            flash('Kullanıcı bulunamadı!', 'danger')
    return render_template('login.html')

@student_bp.route('/home')
def home():
    if 'user_id' not in session: return redirect(url_for('student.login'))
    
    user_name = session['user_name']
    all_courses = Course.query.all()
    
    # Her dersin ilerlemesini hesaplayıp listeye ekleyelim
    courses_data = []
    for c in all_courses:
        progress = calculate_progress(session['user_id'], course_id=c.course_id)
        courses_data.append({
            "course_id": c.course_id,
            "course_name": c.course_name,
            "grade_level": c.grade_level,
            "progress": progress # Hesaplanan gerçek yüzde
        })
        
    return render_template('home.html', user_name=user_name, courses=courses_data)

@student_bp.route('/course/<int:course_id>')
def course_detail(course_id):
    if 'user_id' not in session: return redirect(url_for('student.login'))
    
    course = Course.query.get_or_404(course_id)
    all_modules = Module.query.filter_by(course_id=course_id).all()
    
    modules_data = []
    for m in all_modules:
        prog = calculate_progress(session['user_id'], module_id=m.module_id)
        modules_data.append({
            "module_id": m.module_id,
            "module_name": m.module_name,
            "progress": prog # Hesaplanan gerçek yüzde
        })
    
    return render_template('course_detail.html', course=course, modules=modules_data)

@student_bp.route('/module/<int:module_id>', methods=['GET', 'POST'])
def module_content(module_id):
    if 'user_id' not in session: return redirect(url_for('student.login'))
    
    module = Module.query.get_or_404(module_id)
    section = Section.query.filter_by(module_id=module_id).first()
    
    if not section:
        flash("Bu modülde henüz içerik yok.", "warning")
        return redirect(url_for('student.course_detail', course_id=module.course_id))

    questions = Question.query.filter_by(section_id=section.section_id).all()

    if request.method == 'POST':
        correct_count = 0
        for q in questions:
            user_answer = request.form.get(f'question_{q.question_id}')
            is_correct = (user_answer == q.question_answer)
            if is_correct: correct_count += 1
            
            event = LearningEventFact(
                student_id=session['user_id'],
                question_id=q.question_id,
                is_correct=is_correct,
                timestamp=datetime.utcnow()
            )
            db.session.add(event)
            
        if correct_count == len(questions):
            flash("🏆 Mükemmel! Tüm sorular doğru.", "success")
        else:
            flash(f"⚠️ {len(questions)} sorudan {correct_count} tanesini bildin.", "warning")
            
        db.session.commit()
        return redirect(url_for('student.course_detail', course_id=module.course_id))

    return render_template('quiz.html', module=module, questions=questions)

@student_bp.route('/reset_module/<int:module_id>')
def reset_module(module_id):
    if 'user_id' not in session: return redirect(url_for('student.login'))
    
    module = Module.query.get_or_404(module_id)
    
    # 1. Bu modüle ait soruları bul (Section üzerinden)
    # SQL Mantığı: LearningEventFact tablosundan, bu modüldeki sorulara ait kayıtları sil.
    
    # Önce silinecek soruların ID'lerini bulalım
    questions_in_module = db.session.query(Question.question_id)\
        .join(Section).filter(Section.module_id == module_id).all()
    
    question_ids = [q.question_id for q in questions_in_module]
    
    if question_ids:
        # Bu ID'lere sahip cevap geçmişini sil
        LearningEventFact.query.filter(
            LearningEventFact.student_id == session['user_id'],
            LearningEventFact.question_id.in_(question_ids)
        ).delete(synchronize_session=False)
        
        db.session.commit()
        flash(f"'{module.module_name}' ünitesi sıfırlandı. Tekrar çözebilirsin!", "info")
    else:
        flash("Sıfırlanacak bir veri bulunamadı.", "warning")

    return redirect(url_for('student.course_detail', course_id=module.course_id))

@student_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('student.login'))

@student_bp.route('/achievements')
def achievements():
    if 'user_id' not in session: return redirect(url_for('student.login'))
    
    user_name = session['user_name']
    total_correct = LearningEventFact.query.filter_by(
        student_id=session['user_id'], 
        is_correct=True
    ).count()
    
    badges = [
        {"name": "Yeni Başlayan", "desc": "İlk doğru cevabını ver.", "locked": total_correct < 1, "icon": "🌱"},
        {"name": "Hızlı Öğrenci", "desc": "5 doğru cevap ver.", "locked": total_correct < 5, "icon": "🚀"},
        {"name": "Matematik Dehası", "desc": "10 doğru cevap ver.", "locked": total_correct < 10, "icon": "🧠"},
        {"name": "Efsane", "desc": "50 doğru cevap ver.", "locked": total_correct < 50, "icon": "👑"}
    ]
    
    return render_template('achievements.html', user_name=user_name, badges=badges, total_correct=total_correct)