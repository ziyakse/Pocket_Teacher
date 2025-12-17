from flask import Blueprint, render_template
from app.models import Student, FinancialTransaction, db
from sqlalchemy import func

# 'web' adında yeni bir modül oluşturuyoruz
web_bp = Blueprint('web', __name__)

@web_bp.route('/dashboard')
def dashboard():
    # 1. İstatistikleri Hesapla
    total_students = Student.query.count()
    supported_count = Student.query.filter_by(account_type='Supported').count()
    
    # Toplam geliri hesapla (SQL: SUM fonksiyonu)
    revenue = db.session.query(func.sum(FinancialTransaction.purchase_amount)).scalar() or 0.0

    # 2. Listeleri Çek
    students = Student.query.all()
    
    # İşlemleri çekerken öğrenci isimlerini de getirmemiz lazım
    raw_transactions = FinancialTransaction.query.order_by(FinancialTransaction.transaction_date.desc()).limit(5).all()
    
    transactions = []
    for t in raw_transactions:
        purchaser = Student.query.get(t.purchaser_id)
        supported = Student.query.get(t.supported_user_id) if t.supported_user_id else None
        
        transactions.append({
            "purchaser_name": f"{purchaser.name} {purchaser.last_name}",
            "amount": t.purchase_amount,
            "supported_name": f"{supported.name} {supported.last_name}" if supported else None
        })

    # 3. HTML Sayfasına Gönder
    # Buradaki değişken isimleri (total_students vb.) HTML içindeki {{ ... }} kısımlarına gider.
    return render_template('dashboard.html', 
                           total_students=total_students,
                           supported_count=supported_count,
                           revenue=revenue,
                           students=students,
                           transactions=transactions)