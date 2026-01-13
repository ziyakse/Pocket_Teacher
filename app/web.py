from flask import Blueprint, render_template
from app.models import Student, FinancialTransaction, db
from sqlalchemy import func

web_bp = Blueprint('web', __name__)

@web_bp.route('/dashboard')
def dashboard():
    total_students = Student.query.count()
    supported_count = Student.query.filter_by(account_type='Supported').count()
    
    revenue = db.session.query(func.sum(FinancialTransaction.purchase_amount)).scalar() or 0.0

    students = Student.query.all()
    
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

    return render_template('dashboard.html', 
                           total_students=total_students,
                           supported_count=supported_count,
                           revenue=revenue,
                           students=students,
                           transactions=transactions)