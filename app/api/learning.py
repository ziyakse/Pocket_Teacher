import json
import random
from flask import Blueprint, jsonify, request
from app.models import db, Course, Module, Section, Question, LearningEventFact, AdaptiveState
from datetime import datetime
from app.ai_manager import generate_question_from_ai
from sqlalchemy.sql.expression import func # Rastgele seçim için gerekli

learning_bp = Blueprint('learning', __name__)

# --- MEVCUT KODLAR (GET işlemleri) ---
@learning_bp.route('/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    output = [{"course_id": c.course_id, "title": c.course_name, "grade_level": c.grade_level, "progress": "15%"} for c in courses]
    return jsonify(output), 200

@learning_bp.route('/courses/<int:course_id>/modules', methods=['GET'])
def get_modules(course_id):
    course = Course.query.get_or_404(course_id)
    modules = Module.query.filter_by(course_id=course_id).all()
    output = [{"module_id": m.module_id, "title": m.module_name, "content_type": m.content_type} for m in modules]
    return jsonify({"course": course.course_name, "modules": output}), 200

# --- SORU CEVAPLAMA VE AI KISMI ---
@learning_bp.route('/submit_answer', methods=['POST'])
def submit_answer():
    # 1. Mobil uygulamadan gelen veriyi al
    data = request.get_json()
    student_id = data.get('student_id')
    question_id = data.get('question_id')
    given_answer = data.get('answer') 

    # 2. Soruyu ve Doğru Cevabı Bul
    question = Question.query.get_or_404(question_id)
    is_correct = (given_answer == question.question_answer)

    # 3. [H-3] ANALİTİK KAYDI (LearningEventFact)
    event = LearningEventFact(
        student_id=student_id,
        question_id=question_id,
        is_correct=is_correct,
        timestamp=datetime.utcnow()
    )
    db.session.add(event)
    
    # 4. [H-1] AI ADAPTİF MANTIK
    adaptive_state = AdaptiveState.query.filter_by(student_id=student_id).first()
    
    message = "Cevap alındı."
    if adaptive_state:
        if is_correct:
            message = "Harika! Doğru cevap. Yapay zeka seni sonraki seviyeye hazırlıyor."
        else:
            message = "Yanlış cevap. Bu konuyu tekrar etmen öneriliyor."
            
    db.session.commit()

    return jsonify({
        "result": "Correct" if is_correct else "Incorrect",
        "message": message,
        "correct_answer": question.question_answer
    }), 200


# --- ESKİ TEKLİ AI ROTASI (İstersen durabilir, zararı yok) ---
@learning_bp.route('/generate_ai_quiz/<int:module_id>', methods=['POST'])
def generate_ai_quiz(module_id):
    student_id = 1 
    module = Module.query.get_or_404(module_id)
    section = Section.query.filter_by(module_id=module_id).first()
    
    if not section:
        return jsonify({"error": "Bölüm bulunamadı."}), 400

    last_event = LearningEventFact.query.filter_by(student_id=student_id).order_by(LearningEventFact.timestamp.desc()).first()
    difficulty = 2 
    
    if last_event:
        last_question = Question.query.get(last_event.question_id)
        if last_question:
            current_level = last_question.difficulty_score or 2
            if last_event.is_correct:
                difficulty = min(current_level + 1, 5)
            else:
                difficulty = max(current_level - 1, 1)
    
    topic = module.module_name
    ai_data = generate_question_from_ai(topic, difficulty)
    
    if ai_data:
        all_options = [
            ai_data['question_answer'],
            ai_data.get('wrong_answer_1', 'Yanlış 1'),
            ai_data.get('wrong_answer_2', 'Yanlış 2')
        ]
        options_json = json.dumps(all_options)

        new_q = Question(
            section_id=section.section_id,
            question_text=ai_data['question_text'],
            question_answer=ai_data['question_answer'],
            difficulty_score=difficulty,
            topic=topic,
            options=options_json
        )
        db.session.add(new_q)
        db.session.commit()
        
        return jsonify({
            "message": f"Yapay Zeka senin için Seviye {difficulty} bir soru hazırladı!",
            "question": ai_data
        }), 200
    else:
        return jsonify({"message": "AI servisine ulaşılamadı."}), 500


# --- YENİ EKLENEN TOPLU SEVİYE ATLAMA ROTASI ---
@learning_bp.route('/upgrade_level/<int:module_id>', methods=['POST'])
def upgrade_level(module_id):
    student_id = 1 
    
    # --- 1. BAŞARI KONTROLÜ ---
    total_q = Question.query.join(Section).filter(Section.module_id == module_id).count()
    correct_q = LearningEventFact.query.join(Question).join(Section).filter(
        Section.module_id == module_id,
        LearningEventFact.student_id == student_id,
        LearningEventFact.is_correct == True
    ).distinct().count()
    
    success_rate = (correct_q / total_q * 100) if total_q > 0 else 0
    
    if success_rate < 70:
        return jsonify({
            "status": "fail",
            "message": f"Başarı oranın %{int(success_rate)}. Seviye atlamak için %70 yapmalısın!"
        }), 200

    # --- 2. HEDEF BELİRLEME (TURBO MOD 🔥) ---
    section = Section.query.filter_by(module_id=module_id).first()
    BATCH_SIZE = 5
    
    # Silinecekler: Hala EN KOLAY olanlar (Temizlik yapıyoruz)
    easy_questions = Question.query.filter_by(section_id=section.section_id)\
        .order_by(Question.difficulty_score.asc(), func.random())\
        .limit(BATCH_SIZE).all()
        
    if not easy_questions:
         return jsonify({"status": "error", "message": "Soru havuzu boş."}), 400
    
    # --- KRİTİK DEĞİŞİKLİK BURADA ---
    # Hedef Seviye: En düşüğe +1 eklemek yerine, MEVCUT EN YÜKSEĞE +1 ekliyoruz.
    # Böylece havuzda L1 varken bile L3 gelebilir!
    
    max_q = Question.query.filter_by(section_id=section.section_id)\
        .order_by(Question.difficulty_score.desc()).first()
        
    current_max_level = max_q.difficulty_score if max_q else 1
    target_level = min(current_max_level + 1, 5) # Asla 5'i geçme
    
    topic = Module.query.get(module_id).module_name

    # --- 3. AI'DAN YENİ SORU İSTE ---
    ai_questions_list = generate_question_from_ai(topic, target_level, count=BATCH_SIZE)
    
    if not ai_questions_list:
        return jsonify({
            "status": "error", 
            "message": "AI servisine bağlanılamadı. Soruların silinmedi."
        }), 500

    # --- 4. GÜVENLİ TAKAS ---
    received_count = len(ai_questions_list)
    questions_to_delete = easy_questions[:received_count]
    
    # Eskileri Sil
    for q in questions_to_delete:
        LearningEventFact.query.filter_by(question_id=q.question_id).delete()
        db.session.delete(q)
    
    # Yenileri Ekle
    for ai_data in ai_questions_list:
        all_options = [
            ai_data['question_answer'],
            ai_data.get('wrong_answer_1', 'Y1'),
            ai_data.get('wrong_answer_2', 'Y2')
        ]
        random.shuffle(all_options)
        
        new_q = Question(
            section_id=section.section_id,
            question_text=ai_data['question_text'],
            question_answer=ai_data['question_answer'],
            difficulty_score=target_level,
            topic=topic,
            options=json.dumps(all_options)
        )
        db.session.add(new_q)
            
    db.session.commit()
    
    return jsonify({
        "status": "success",
        "message": f"TURBO MOD: {received_count} kolay soru silindi, yerine Seviye {target_level} eklendi! 🚀"
    }), 200