from flask import Blueprint, request, jsonify
from app.models import db, Student, FinancialTransaction, City
from datetime import datetime

finance_bp = Blueprint('finance', __name__)

@finance_bp.route('/purchase', methods=['POST'])
def purchase_subscription():
    data = request.get_json()
    purchaser_id = data.get('student_id')
    amount = data.get('amount') # Örn: 100.0 TL

    # 1. Satın alan öğrenciyi bul
    purchaser = Student.query.get_or_404(purchaser_id)

    # 2. Sosyal Etki Mantığı (H-2): İhtiyaç sahibi öğrenci bul
    # Dezavantajlı şehirde yaşayan (is_disadvantaged=True) ve hesabı 'Free' olan birini bul
    supported_student = Student.query.join(City).filter(
        City.is_disadvantaged == True,
        Student.account_type == 'Free'
    ).first()

    supported_student_id = None
    
    # Eğer böyle bir öğrenci varsa, onu da Premium yap (Supported)
    if supported_student:
        supported_student.account_type = 'Supported' # Artık o da ücretsiz premium!
        supported_student_id = supported_student.student_id
        print(f"--- SOSYAL ETKİ: {supported_student.name} isimli öğrenciye destek sağlandı! ---")

    # 3. Satın alanı güncelle
    purchaser.account_type = 'Premium'

    # 4. İşlemi Kaydet (FinancialTransactions Tablosu)
    transaction = FinancialTransaction(
        purchaser_id=purchaser_id,
        supported_user_id=supported_student_id, # Desteklenen öğrenciyi buraya bağladık
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