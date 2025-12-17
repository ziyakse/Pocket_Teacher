from flask import Blueprint, jsonify, request  # <-- request BURADA olmalı
from app.models import db, Course, Module, Section, Question, LearningEventFact, AdaptiveState
from datetime import datetime

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