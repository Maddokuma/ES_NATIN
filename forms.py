from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, TextAreaField
from flask_wtf.file import FileField, FileRequired
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length
from werkzeug.utils import secure_filename
from es_natin.models import Gebruiker

# INLOGGEN 
class InloggenForm(FlaskForm):
    gebruikersnaam  = StringField('Gebruikersnaam', validators=[DataRequired()])
    wachtwoord      = PasswordField('Wachtwoord', validators=[DataRequired()])
    inloggen        = SubmitField('Inloggen')

# GEBRUIKERS 
class GebruikerForm(FlaskForm):
    gebruikersnaam  = StringField('Gebruikersnaam', validators=[DataRequired()])
    wachtwoord      = PasswordField('Wachtwoord', validators=[DataRequired()])
    rol             = SelectField(choices=[('Admin', 'Admin'), ('Student', 'Student')])
    toevoegen        = SubmitField('Toevoegen')

    def validate_gebruikersnaam(self, gebruikersnaam):
        gebruiker = Gebruiker.query.filter_by(gebruikersnaam=gebruikersnaam.data).first()
        if gebruiker:
            raise ValueError('De gebruikersnaam is in gebruik.')


class GebruikersFileForm(FlaskForm):
    upload = FileField(validators=[FileRequired()])
    toevoegen = SubmitField('Toevoegen')

# EXAM 
class ExamForm(FlaskForm):
    examnaam    = StringField('Examnaam', validators=[DataRequired()])
    vak         = StringField('Vak', validators=[DataRequired()])
    klas        = StringField('Klas', validators=[DataRequired()])
    datum       = DateField('Datum', validators=[DataRequired()])
    duur        = IntegerField('Duur', validators=[DataRequired()])
    status      = SelectField(choices=[('Gesloten', 'Gesloten'),('Open', 'Open')])
    toevoegen   = SubmitField('Toevoegen')

class VraagForm(FlaskForm):
    vraaginfo   = TextAreaField('Vraaginfo', validators=[DataRequired()])
    keuzeA      = TextAreaField('A', validators=[DataRequired()])
    keuzeB      = TextAreaField('B', validators=[DataRequired()])
    keuzeC      = TextAreaField('C', validators=[DataRequired()])
    keuzeD      = TextAreaField('D', validators=[DataRequired()])
    antwoord    = SelectField(choices=[('A', 'A'),('B', 'B'), ('C', 'C'),('D', 'D')])
    punt        = IntegerField('Punt', validators=[DataRequired()])
    toevoegen   = SubmitField('Toevoegen')

class VragenFileForm(FlaskForm):
    upload = FileField(validators=[FileRequired()])
    toevoegen = SubmitField('Toevoegen')

class QuizForm(FlaskForm):
    beantwoordkeuze = SelectField(choices=[ ('', ''), ('A', 'A'),('B', 'B'), ('C', 'C'),('D', 'D')], validators=[DataRequired()])
    toevoegen      = SubmitField('Indienen')

class FeedbackForm(FlaskForm):
    feedbackinfo   = TextAreaField('Feedbackinfo', validators=[DataRequired()])
    toevoegen      = SubmitField('Indienen')
