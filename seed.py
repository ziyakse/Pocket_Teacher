from app import create_app, db
from app.models import City, Student, Course, Module, Section, Question, AdaptiveState
from datetime import date

app = create_app()

with app.app_context():
    # Önce temizlik yapalım (Eski veri varsa siler)
    db.drop_all()
    db.create_all()

    print("Veritabanı temizlendi ve yeniden oluşturuldu.")

    # 1. ŞEHİRLER (H-2 Sosyal Etki için)
    # [cite_start]PDF'te şehir ve dezavantajlı bölge ayrımı önemli [cite: 40-43]
    istanbul = City(city_name="Istanbul", country_name="Turkey", is_disadvantaged=False)
    van = City(city_name="Van", country_name="Turkey", is_disadvantaged=True)
    
    db.session.add_all([istanbul, van])
    db.session.commit()

    # 2. ÖĞRENCİLER
    # [cite_start]PDF UI örneğindeki öğrenci: Denis [cite: 114]
    denis = Student(
        name="Denis", 
        last_name="Sarphi", 
        email="denis@example.com", 
        city_id=istanbul.city_id,
        birth_date=date(2013, 5, 12),
        grade=5,
        account_type="Premium"
    )
    
    # Dezavantajlı bölgedeki öğrenci (Askıda eğitim için)
    ali = Student(
        name="Ali", 
        last_name="Yilmaz", 
        email="ali@example.com", 
        city_id=van.city_id,
        grade=5,
        account_type="Free"
    )

    db.session.add_all([denis, ali])
    db.session.commit()

    # [cite_start]Öğrencinin AI Durumunu Başlat (H-1 Adaptivity) [cite: 44]
    denis_state = AdaptiveState(student_id=denis.student_id)
    db.session.add(denis_state)
    db.session.commit()

    # 3. DERSLER VE MODÜLLER
    # [cite_start]PDF UI örneği: Maths -> Numbers and Counting [cite: 188]
    math_course = Course(course_name="Maths", grade_level=5)
    db.session.add(math_course)
    db.session.commit()

    module1 = Module(module_name="Numbers and Counting (0-20)", course_id=math_course.course_id, content_type="Mixed")
    db.session.add(module1)
    db.session.commit()

    # 4. BÖLÜMLER VE SORULAR
    # [cite_start]PDF Quiz örneği [cite: 257]
    quiz_section = Section(module_id=module1.module_id, section_name="Quiz 1", section_content="Basic Counting Quiz")
    db.session.add(quiz_section)
    db.session.commit()

    q1 = Question(
        section_id=quiz_section.section_id,
        question_text="Which number comes immediately after 17?",
        question_answer="18",
        difficulty_score=1, # Kolay soru
        topic="Counting"
    )
    
    q2 = Question(
        section_id=quiz_section.section_id,
        question_text="Which number is less than 8?",
        question_answer="3",
        difficulty_score=2, 
        topic="Comparison"
    )

    db.session.add_all([q1, q2])
    db.session.commit()

    print(f"Başarılı! Öğrenci '{denis.name}' ve '{math_course.course_name}' dersi eklendi.")