import json
import random
from datetime import datetime
from app import create_app
from app.models import db, Student, Course, Module, Section, Question, City

app = create_app()

def get_curriculum_for_grade(grade):
    """
    Her sınıf seviyesi için GERÇEKÇİ ve FARKLI ünite isimleri döndürür.
    """
    if grade == 1:
        return [
            ("Matematik", ["Rakamlar ve Sayma", "Doğal Sayılarla Toplama", "Doğal Sayılarla Çıkarma", "Geometrik Şekiller", "Ölçme"]),
            ("Türkçe", ["Harf Bilgisi", "Okuma Yazma", "Hece Bilgisi", "Kelimede Anlam", "Cümle Bilgisi"]),
            ("Hayat Bilgisi", ["Okulumuzda Hayat", "Evimizde Hayat", "Sağlıklı Hayat", "Güvenli Hayat", "Doğada Hayat"]),
            ("İngilizce", ["Greeting", "Family", "Numbers", "Colors", "Body Parts"])
        ]
    elif grade == 2:
        return [
            ("Matematik", ["Doğal Sayılar (100'e kadar)", "Toplama ve Çıkarma", "Çarpma İşlemine Giriş", "Bölme İşlemi", "Geometrik Cisimler"]),
            ("Türkçe", ["Zıt Anlamlı Kelimeler", "Eş Anlamlı Kelimeler", "Noktalama İşaretleri", "Metin Türleri", "Yazım Kuralları"]),
            ("Hayat Bilgisi", ["Kendimizi Tanıyalım", "Evdeki Sorumluluklar", "Sağlıklı Büyüme", "Ulaşım Araçları", "Ülkemiz"]),
            ("İngilizce", ["Words", "Friends", "In the Classroom", "Numbers (1-20)", "Animals"])
        ]
    elif grade == 3:
        return [
            ("Matematik", ["3 Basamaklı Sayılar", "Romen Rakamları", "Çarpım Tablosu", "Bölme İşlemi", "Kesirler"]),
            ("Fen Bilimleri", ["Gezegenimizi Tanıyalım", "Beş Duyumuz", "Kuvveti Tanıyalım", "Maddeyi Tanıyalım", "Canlılar Dünyası"]),
            ("Türkçe", ["Sözcük Bilgisi", "Cümle Bilgisi", "Paragraf", "Şekil ve Semboller", "Hikaye Unsurları"]),
            ("Hayat Bilgisi", ["Arkadaşlık", "Kroki ve Yönler", "Tasarruf", "Doğa ve Çevre", "Milli Bayramlar"]),
            ("İngilizce", ["Greeting", "My Family", "People I Love", "Feelings", "Toys and Games"])
        ]
    elif grade == 4:
        return [
            ("Matematik", ["Doğal Sayılar (4-5-6 Basamaklı)", "Kesirlerle İşlemler", "Zaman Ölçme", "Veri Toplama", "Uzunluk Ölçme"]),
            ("Fen Bilimleri", ["Yer Kabuğu", "Besinlerimiz", "Kuvvetin Etkileri", "Maddenin Özellikleri", "Aydınlatma"]),
            ("Sosyal Bilgiler", ["Birey ve Toplum", "Kültür ve Miras", "İnsanlar ve Yerler", "Bilim ve Teknoloji", "Üretim Dağıtım"]),
            ("Türkçe", ["Deyimler ve Atasözleri", "Gerçek ve Mecaz Anlam", "Neden Sonuç", "Öznel Nesnel", "Metin Analizi"]),
            ("İngilizce", ["Classroom Rules", "Nationality", "Cartoon Characters", "Free Time", "My Day"])
        ]
    elif grade == 5:
        return [
            ("Matematik", ["Milyonlar", "Kesirler ve Ondalıklar", "Yüzdeler", "Temel Geometri", "Veri Analizi"]),
            ("Fen Bilimleri", ["Güneş Dünya Ay", "Canlılar Dünyası", "Kuvvet ve Sürtünme", "Madde ve Değişim", "Işığın Yayılması"]),
            ("Sosyal Bilgiler", ["Haklarımız", "Tarihi Güzellikler", "İklim ve Yaşam", "Teknoloji ve Toplum", "Ekonomi"]),
            ("Türkçe", ["Sözcükte Anlam", "Cümlede Anlam", "Paragraf", "Ses Bilgisi", "Yazım Kuralları"]),
            ("İngilizce", ["Hello", "My Town", "Games and Hobbies", "My Daily Routine", "Health"])
        ]
    elif grade == 6:
        return [
            ("Matematik", ["Doğal Sayılarla İşlemler", "Çarpanlar ve Katlar", "Kümeler", "Tam Sayılar", "Cebirsel İfadeler"]),
            ("Fen Bilimleri", ["Güneş Sistemi", "Vücudumuzdaki Sistemler", "Kuvvet ve Hareket", "Madde ve Isı", "Ses ve Özellikleri"]),
            ("Sosyal Bilgiler", ["Biz ve Değerlerimiz", "Tarihe Yolculuk", "Yeryüzünde Yaşam", "Bilim ve Hayat", "Üretiyorum Tüketiyorum"]),
            ("Türkçe", ["Söz Sanatları", "Zamirler", "Sıfatlar", "Metin Türleri", "Noktalama"]),
            ("İngilizce", ["Life", "Yummy Breakfast", "Downtown", "Weather", "At the Fair"])
        ]
    elif grade == 7:
        return [
            ("Matematik", ["Tam Sayılarla İşlemler", "Rasyonel Sayılar", "Cebirsel İfadeler", "Eşitlik ve Denklem", "Oran ve Orantı"]),
            ("Fen Bilimleri", ["Güneş Sistemi ve Ötesi", "Hücre ve Bölünmeler", "Kuvvet ve Enerji", "Saf Madde", "Işığın Kırılması"]),
            ("Sosyal Bilgiler", ["İletişim ve İlişkiler", "Türk Tarihinde Yolculuk", "Nüfus ve Yerleşme", "Zaman İçinde Bilim", "Ekonomi"]),
            ("Türkçe", ["Fiiller", "Zarflar", "Ek Fiil", "Anlatım Bozuklukları", "Yazım Kuralları"]),
            ("İngilizce", ["Appearance", "Sports", "Biographies", "Wild Animals", "Television"])
        ]
    elif grade == 8:
        return [
            ("Matematik", ["Çarpanlar ve Katlar", "Üslü İfadeler", "Kareköklü İfadeler", "Veri Analizi", "Basit Olayların Olasılığı"]),
            ("Fen Bilimleri", ["Mevsimler ve İklim", "DNA ve Genetik Kod", "Basınç", "Madde ve Endüstri", "Basit Makineler"]),
            ("T.C. İnkılap Tarihi", ["Bir Kahraman Doğuyor", "Milli Uyanış", "Ya İstiklal Ya Ölüm", "Atatürkçülük", "Demokratikleşme"]),
            ("Türkçe", ["Fiilimsiler", "Cümlenin Ögeleri", "Cümle Türleri", "Yazım ve Noktalama", "Sözel Mantık"]),
            ("İngilizce", ["Friendship", "Teen Life", "In the Kitchen", "On the Phone", "The Internet"])
        ]
    else:
        return []

def generate_dynamic_question(course_name, topic, index, grade):
    """
    Soruların TEKRAR ETMEMESİ için her seferinde rastgele değerler ve kalıplar kullanır.
    """
    q_text = ""
    correct = ""
    w1 = ""
    w2 = ""

    if course_name == "Matematik":
        if grade <= 2:
            n1 = random.randint(1, 50)
            n2 = random.randint(1, 50)
            op = random.choice(['+', '-'])
            
            if op == '+': 
                res = n1 + n2
                q_text = f"Soru {index}: {n1} + {n2} işleminin sonucu kaçtır?"
            else:
                big, small = max(n1, n2), min(n1, n2)
                res = big - small
                q_text = f"Soru {index}: {big} - {small} işleminin sonucu kaçtır?"
            
            correct = str(res)
            w1 = str(res + random.randint(1, 5))
            w2 = str(res - random.randint(1, 5))

        elif grade <= 4:
            n1 = random.randint(2, 12)
            n2 = random.randint(2, 12)
            res = n1 * n2
            q_text = f"Soru {index}: {n1} kere {n2} kaç eder?"
            correct = str(res)
            w1 = str(res + random.choice([2, 5, 10]))
            w2 = str(res - 1)

        elif grade <= 6:
            if index % 2 == 0:
                base = random.randint(2, 5)
                exp = random.randint(2, 3)
                res = base ** exp
                q_text = f"Soru {index}: {base} üssü {exp} ({base}^{exp}) işleminin sonucu kaçtır?"
                correct = str(res)
                w1 = str(res + base)
                w2 = str(res * 2)
            else:
                x = random.randint(10, 100)
                q_text = f"Soru {index}: Hangi sayının 5 fazlası {x + 5} eder?"
                correct = str(x)
                w1 = str(x-5)
                w2 = str(x+5)

        else:
            if "Karekök" in topic:
                sq = random.choice([16, 25, 36, 49, 64, 81, 100, 144])
                import math
                res = int(math.sqrt(sq))
                q_text = f"Soru {index}: √{sq} ifadesinin değeri kaçtır?"
                correct = str(res)
                w1 = str(res+1)
                w2 = str(res*2)
            else:
                x = random.randint(2, 10)
                a = random.randint(1, 20)
                b = (2 * x) + a
                q_text = f"Soru {index}: 2x + {a} = {b} ise, x kaçtır?"
                correct = str(x)
                w1 = str(x+1)
                w2 = str(x-2)

    else:
        templates = [
            f"'{topic}' konusunda en önemli kavram hangisidir?",
            f"Aşağıdakilerden hangisi '{topic}' ile ilgilidir?",
            f"'{topic}' hakkında verilen bilgilerden hangisi doğrudur?",
            f"{index}. Soru: '{topic}' denince akla ne gelir?",
            f"Aşağıdaki seçeneklerden hangisi '{topic}' ünitesine aittir?",
            f"'{topic}' konusu için anahtar kelime nedir?",
            f"Bu ünitede ({topic}) hangisini öğreniriz?",
            f"Aşağıdaki ifadelerden hangisi '{topic}' ile çelişir?",
            f"'{topic}' kavramını en iyi açıklayan ifade hangisidir?",
            f"Hangisi '{topic}' ile doğrudan bağlantılı değildir?"
        ]
        
        q_text = random.choice(templates)
        
        if course_name == "İngilizce":
            correct = f"Correct Info about {topic}"
            w1 = "Wrong Grammar"
            w2 = "Unrelated Word"
        elif course_name == "Fen Bilimleri":
            correct = "Bilimsel Gerçek"
            w1 = "Hatalı Gözlem"
            w2 = "Yanlış Deney Sonucu"
        elif course_name == "T.C. İnkılap Tarihi" or course_name == "Sosyal Bilgiler":
            correct = "Tarihi Gerçek"
            w1 = "Yanlış Tarih"
            w2 = "Hatalı Olay"
        else:
            correct = "Doğru Bilgi"
            w1 = "Yanlış Bilgi A"
            w2 = "Yanlış Bilgi B"

    return q_text, correct, w1, w2

def seed_database():
    with app.app_context():
        print("🗑️  Eski veritabanı temizleniyor...")
        db.drop_all()
        db.create_all()

        print("🏙️  Şehir oluşturuluyor...")
        istanbul = City(city_name="İstanbul", country_name="Türkiye", is_disadvantaged=False)
        db.session.add(istanbul)
        db.session.flush()

        print("👤 Öğrenci (Denis) oluşturuluyor...")
        student = Student(
            name="Denis", last_name="Demir", email="denis@example.com",
            city_id=istanbul.city_id, grade=5, birth_date=datetime(2014, 1, 1),
            account_type="Free"
        )
        student.set_password("123")
        db.session.add(student)
        db.session.commit()

        print("📚 1'den 8'e tüm sınıflar için ÖZEL müfredat yükleniyor (Bu işlem 5-10 saniye sürebilir)...")

        for grade in range(1, 9):
            curriculum = get_curriculum_for_grade(grade)
            print(f"   -> {grade}. Sınıf müfredatı işleniyor...")
            
            for course_info in curriculum:
                course_name = course_info[0]
                topics = course_info[1]

                course = Course(course_name=course_name, grade_level=grade)
                db.session.add(course)
                db.session.flush()

                for topic in topics:
                    module = Module(course_id=course.course_id, module_name=topic, content_type="quiz")
                    db.session.add(module)
                    db.session.flush()

                    section = Section(module_id=module.module_id, section_name="Tarama Testi")
                    db.session.add(section)
                    db.session.flush()

                    for i in range(1, 21):
                        q_text, correct, w1, w2 = generate_dynamic_question(course_name, topic, i, grade)
                        
                        options = [correct, w1, w2]
                        random.shuffle(options)

                        question = Question(
                            section_id=section.section_id,
                            question_text=q_text,
                            question_answer=correct,
                            difficulty_score=1, 
                            topic=topic,
                            options=json.dumps(options, ensure_ascii=False)
                        )
                        db.session.add(question)
        
        db.session.commit()
        print("\n✅ TÜM SINIFLAR İÇİN 20'ŞER SORULUK MÜFREDAT HAZIR! 🚀")

if __name__ == "__main__":
    seed_database()