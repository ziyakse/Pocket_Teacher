from flask import Blueprint, request, jsonify
from app.models import Student

# Blueprint: Uygulamayı parçalara bölmemizi sağlar
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    # Mobil uygulamadan gelen JSON verisini al
    data = request.get_json()
    email = data.get('email')
    
    # Not: Gerçek projede şifre kontrolü (hash) de yapılır. 
    # Şimdilik sadece email ile kullanıcıyı buluyoruz.
    student = Student.query.filter_by(email=email).first()
    
    if student:
        # Başarılı giriş
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
        # Kullanıcı bulunamadı
        return jsonify({"message": "Kullanıcı bulunamadı"}), 404