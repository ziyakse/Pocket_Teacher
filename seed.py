# seed.py
from app import create_app, db
from app.models import City, Student, Course, Module, Section, Question, AdaptiveState
from datetime import date

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    # Temel Veriler
    istanbul = City(city_name="Istanbul", country_name="Turkey", is_disadvantaged=False)
    denis = Student(name="Denis", last_name="Sarphi", email="denis@example.com", city_id=1, birth_date=date(2013, 5, 12), grade=5, account_type="Premium")
    
    db.session.add(istanbul)
    db.session.add(denis)
    db.session.commit()

    # Ders ve Modül
    math_course = Course(course_name="Maths", grade_level=5)
    db.session.add(math_course)
    db.session.commit()

    module1 = Module(module_name="Numbers and Counting", course_id=math_course.course_id, content_type="Mixed")
    db.session.add(module1)
    db.session.commit()

    section = Section(module_id=module1.module_id, section_name="Level 1 Pool", section_content="Initial Pool")
    db.session.add(section)
    db.session.commit()

    # --- 20 TANE 1. SEVİYE SORU EKLEME DÖNGÜSÜ ---
    print("20 adet başlangıç sorusu oluşturuluyor...")
    for i in range(1, 21):
        q = Question(
            section_id=section.section_id,
            question_text=f"Soru {i}: {i} + {i} kaçtır?", # Basit toplama
            question_answer=str(i+i),
            difficulty_score=1, # Hepsi Seviye 1
            topic="Basic Math"
        )
        db.session.add(q)
    
    db.session.commit()
    print("Veritabanı hazır! 20 adet Seviye 1 soru eklendi.")