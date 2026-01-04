import json
import random
from flask_mail import Message
from app import mail # __init__.py'den mail objesini çağırıyoruz
from itsdangerous import URLSafeTimedSerializer
from flask import current_app # Config'e erişmek için lazım
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import db, Student, Course, Module, Section, Question, LearningEventFact, AdaptiveState
from datetime import datetime
from app.ai_manager import generate_question_from_ai

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
        password = request.form.get('password')
        
        # 1. Kullanıcıyı bul
        user = Student.query.filter_by(email=email).first()
        
        # 2. Kullanıcı var mı VE şifresi doğru mu?
        if user and user.check_password(password):
            session['user_id'] = user.student_id
            session['user_name'] = user.name
            flash('Başarıyla giriş yapıldı! 🎉', 'success')
            return redirect(url_for('student.home'))
        else:
            flash('Hatalı e-posta veya şifre! ❌', 'danger')
            
    return render_template('login.html')

# --- KAYIT OL (REGISTER) ---
# app/routes/student.py içindeki register ve home fonksiyonlarını güncelle

@student_bp.route('/register', methods=['GET', 'POST'])
def register():
    from app.models import City 
    cities = City.query.all()

    if request.method == 'POST':
        name = request.form.get('name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        city_id = request.form.get('city_id')
        grade = request.form.get('grade') # <--- YENİ: Formdan sınıfı alıyoruz
        
        existing_user = Student.query.filter_by(email=email).first()
        if existing_user:
            flash('Bu e-posta adresi zaten kayıtlı.', 'warning')
            return redirect(url_for('student.register'))
        
        new_student = Student(
            name=name,
            last_name=last_name,
            email=email,
            city_id=city_id,
            grade=int(grade), # <--- YENİ: Seçilen sınıfı kaydediyoruz (String gelir, int yaparız)
            account_type='Free'
        )
        new_student.set_password(password)
        
        db.session.add(new_student)
        db.session.commit()
        
        flash('Kayıt başarılı! Şimdi giriş yapabilirsin. 🚀', 'success')
        return redirect(url_for('student.login'))

    return render_template('register.html', cities=cities)

@student_bp.route('/home')
def home():
    if 'user_id' not in session: return redirect(url_for('student.login'))
    
    # Giriş yapan öğrencinin bilgilerini çekiyoruz
    user = Student.query.get(session['user_id'])
    user_name = user.name
    
    # --- KRİTİK DEĞİŞİKLİK: FİLTRELEME ---
    # Sadece öğrencinin sınıfına (user.grade) ait dersleri getir!
    all_courses = Course.query.filter_by(grade_level=user.grade).all()
    
    courses_data = []
    for c in all_courses:
        progress = calculate_progress(session['user_id'], course_id=c.course_id)
        courses_data.append({
            "course_id": c.course_id,
            "course_name": c.course_name,
            "grade_level": c.grade_level,
            "progress": progress
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
    if 'user_id' not in session: return redirect(url_for('student.login')) # Güvenlik önlemi
    student_id = session['user_id']
    
    # 1. BU ÜNİTEYE AİT BÖLÜMÜ BUL
    section = Section.query.filter_by(module_id=module_id).first()
    if not section:
        flash('Ünite bulunamadı.', 'danger')
        return redirect(url_for('student.course_detail', course_id=1))

    # --- ADIM 1: GEÇMİŞİ TEMİZLE (PUANLARI SİL) ---
    # Bu ünitedeki sorulara verdiğin cevapları siliyoruz
    questions = Question.query.filter_by(section_id=section.section_id).all()
    question_ids = [q.question_id for q in questions]
    
    if question_ids:
        LearningEventFact.query.filter(
            LearningEventFact.question_id.in_(question_ids),
            LearningEventFact.student_id == student_id
        ).delete(synchronize_session=False)

    # --- ADIM 2: ZOR SORULARI SİL (HAVUZU BOŞALT) ---
    # Mevcut soruların hepsi siliniyor (Level 3, 4, 5 hepsi gider)
    Question.query.filter_by(section_id=section.section_id).delete()
    
    # --- ADIM 3: TAZE BAŞLANGIÇ (SEVİYE 1 SORULARI GETİR) ---
    module = Module.query.get(module_id)
    topic = module.module_name
    
    # AI'dan 10 tane Seviye 1 soru istiyoruz
    try:
        # Seviye 1, 10 adet soru
        ai_questions = generate_question_from_ai(topic, difficulty_level=1, count=10)
        
        if ai_questions:
            for q_data in ai_questions:
                all_options = [
                    q_data['question_answer'],
                    q_data.get('wrong_answer_1', 'Yanlış 1'),
                    q_data.get('wrong_answer_2', 'Yanlış 2')
                ]
                random.shuffle(all_options)
                
                new_q = Question(
                    section_id=section.section_id,
                    question_text=q_data['question_text'],
                    question_answer=q_data['question_answer'],
                    difficulty_score=1,  # İşte burası! Kesinlikle 1. Seviye
                    topic=topic,
                    options=json.dumps(all_options)
                )
                db.session.add(new_q)
            
            success_msg = "Ünite sıfırlandı! Seviye 1 sorular hazırlandı."
        else:
            success_msg = "Ünite sıfırlandı ancak yeni soru üretilirken sorun oluştu."
            
    except Exception as e:
        print(f"Reset sırasında hata: {e}")
        success_msg = "Sıfırlama yapıldı (AI Hatası)."

    db.session.commit()
    
    flash(success_msg, 'success')
    # Doğru derse yönlendir (course_id'yi module üzerinden buluyoruz)
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

def send_reset_email(user_email):
    # 1. Güvenli Token Oluştur (15 dk geçerli olur)
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = s.dumps(user_email, salt='password-reset-salt')
    
    # 2. Link Hazırla
    link = url_for('student.reset_password', token=token, _external=True)
    
    # 3. Maili Gönder
    msg = Message('Pocket Teacher - Şifre Sıfırlama', 
                  sender=current_app.config['MAIL_USERNAME'], 
                  recipients=[user_email])
    
    msg.body = f"""Merhaba,
    
Şifreni sıfırlamak için aşağıdaki linke tıkla:
{link}

Bu link 15 dakika boyunca geçerlidir.
Eğer bu isteği sen yapmadıysan, bu maili görmezden gel.
    """
    mail.send(msg)

@student_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = Student.query.filter_by(email=email).first()
        
        if user:
            # Kullanıcı varsa mail at, yoksa da güvenlik gereği "attık" de (Hacker bulamasın)
            try:
                send_reset_email(email)
                flash('Sıfırlama linki e-posta adresine gönderildi! 📩', 'info')
            except Exception as e:
                print(e)
                flash('Mail gönderilirken bir hata oluştu. Ayarlarını kontrol et.', 'danger')
        else:
            flash('Sıfırlama linki e-posta adresine gönderildi! 📩', 'info')
            
        return redirect(url_for('student.login'))
        
    return render_template('forgot_password.html')

@student_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    
    try:
        # Token süresi dolmuş mu kontrol et (900 sn = 15 dk)
        email = s.loads(token, salt='password-reset-salt', max_age=900)
    except:
        flash('Sıfırlama linki geçersiz veya süresi dolmuş.', 'danger')
        return redirect(url_for('student.login'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        
        user = Student.query.filter_by(email=email).first()
        if user:
            user.set_password(password)
            db.session.commit()
            flash('Şifren başarıyla güncellendi! Giriş yapabilirsin. 🔑', 'success')
            return redirect(url_for('student.login'))
            
    return render_template('reset_password.html')