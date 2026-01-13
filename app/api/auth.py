from flask import Blueprint, request, jsonify
from app.models import Student

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    
    student = Student.query.filter_by(email=email).first()
    
    if student:
        return jsonify({
            "message": "Giriş başarılı!",
            "user": {
                "student_id": student.student_id,
                "name": student.name,
                "full_name": f"{student.name} {student.last_name}",
                "account_type": student.account_type,
                "city": student.city.city_name
            }
        }), 200
    else:
        return jsonify({"message": "Kullanıcı bulunamadı"}), 404