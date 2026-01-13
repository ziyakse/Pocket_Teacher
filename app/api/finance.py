from flask import Blueprint, request, jsonify
from app.models import db, Student, FinancialTransaction, City
from datetime import datetime

finance_bp = Blueprint('finance', __name__)

@finance_bp.route('/purchase', methods=['POST'])
def purchase_subscription():
    data = request.get_json()
    purchaser_id = data.get('student_id')
    amount = data.get('amount')

    purchaser = Student.query.get_or_404(purchaser_id)

    supported_student = Student.query.join(City).filter(
        City.is_disadvantaged == True,
        Student.account_type == 'Free'
    ).first()

    supported_student_id = None
    
    if supported_student:
        supported_student.account_type = 'Supported'
        supported_student_id = supported_student.student_id
        print(f"--- SOSYAL ETKİ: {supported_student.name} isimli öğrenciye destek sağlandı! ---")

    purchaser.account_type = 'Premium'

    transaction = FinancialTransaction(
        purchaser_id=purchaser_id,
        supported_user_id=supported_student_id,
        transaction_type='Purchase',
        purchase_amount=amount,
        transaction_date=datetime.utcnow()
    )

    db.session.add(transaction)
    db.session.commit()

    return jsonify({
        "message": "Satın alma başarılı! Hesabınız Premium'a yükseltildi.",
        "social_impact": f"{supported_student.name} adlı öğrencinin eğitim masrafını karşıladınız." if supported_student else "Havuzda bekleyen ihtiyaç sahibi bulunamadı."
    }), 200