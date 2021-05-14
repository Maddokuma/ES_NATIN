from datetime import datetime
from es_natin import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(gebruiker_id):
    return Gebruiker.query.get(int(gebruiker_id))

class Gebruiker(db.Model, UserMixin):
    id              = db.Column(db.Integer(),  primary_key=True) 
    gebruikersnaam  = db.Column(db.String(60), unique=True, nullable=False)
    wachtwoord      = db.Column(db.String(60), unique=False, nullable=False)
    rol             = db.Column(db.String(20), unique=False, nullable=False)
    resultaten       = db.relationship('Resultaat', backref='student', lazy=True)
    feedbacks       = db.relationship('Feedback', backref='student', lazy=True)

    def __repr__(self):
        return f"Gebruiker('{self.gebruikersnaam}', '{self.rol}')"

class Exam(db.Model):
    id          = db.Column(db.Integer(),  primary_key=True) 
    examnaam    = db.Column(db.String(60), nullable=False)
    vak         = db.Column(db.String(60), nullable=False)
    klas        = db.Column(db.String(60), nullable=False)
    datum       = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
    duur        = db.Column(db.Integer(),  nullable=False)
    status      = db.Column(db.String(60), nullable=False)
    vragen      = db.relationship('Vraag', backref='exam', lazy=True)
    resultaten   = db.relationship('Resultaat', backref='exam', lazy=True)

    def __repr__(self):
        return f"Exam('{self.examnaam}', '{self.vak}', '{self.klas}','{self.datum}','{self.duur}','{self.status}')"


class Vraag(db.Model):
    id              = db.Column(db.Integer(), primary_key=True)
    vraaginfo       = db.Column(db.Text(225),    nullable=False)
    keuze_a         = db.Column(db.Text(225),    nullable=False)
    keuze_b         = db.Column(db.Text(225),    nullable=False)
    keuze_c         = db.Column(db.Text(225),    nullable=False)
    keuze_d         = db.Column(db.Text(225),    nullable=False)
    antwoord        = db.Column(db.Text(225),    nullable=False)
    punt            = db.Column(db.Integer(), nullable=False)
    exam_id         = db.Column(db.Integer(), db.ForeignKey('exam.id'), nullable=False)
    beantwoorden    = db.relationship('Beantwoord', backref='vraag', lazy=True)

    def __repr__(self):
        return f"Vraag('{self.vraaginfo}', '{self.keuze_a}', '{self.keuze_b}', '{self.keuze_c}', '{self.keuze_d}', '{self.antwoord}', '{self.punt}', '{self.exam_id}')"

class Resultaat(db.Model):
    id           = db.Column(db.Integer(), primary_key=True)
    cijfer       = db.Column(db.String(20), nullable=True)
    student_id   = db.Column(db.Integer(), db.ForeignKey('gebruiker.id'),  nullable=False)
    exam_id      = db.Column(db.Integer(), db.ForeignKey('exam.id'), nullable=False)
    beantwoorden = db.relationship('Beantwoord', backref='resultaat', lazy=True)

    def __repr__(self):
        return f"Resultaat('{self.cijfer}')"

class Beantwoord(db.Model):
    id           = db.Column(db.Integer(), primary_key=True)
    beantwoordkeuze   = db.Column(db.String(10),  nullable=False)
    punten       = db.Column(db.Integer(), nullable=False)
    vraag_id     = db.Column(db.Integer(), db.ForeignKey('vraag.id'), nullable=False)
    resultaat_id = db.Column(db.Integer(), db.ForeignKey('resultaat.id'), nullable=False)

    def __repr__(self):
        return f"Beantwoord('{self.beantwoordkeuze}', '{self.punten}')"

class Feedback(db.Model):
    id             = db.Column(db.Integer(), primary_key=True)
    feedbackinfo   = db.Column(db.String(90),  nullable=False)
    student_id     = db.Column(db.Integer(), db.ForeignKey('gebruiker.id'),  nullable=False)

    def __repr__(self):
        return f"Beantwoord('{self.feedbackinfo}', '{self.student.gebruikersnaam}')"

