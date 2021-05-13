from io import TextIOWrapper
import csv
from flask import render_template, url_for, flash, redirect, request, make_response
from flask.wrappers import Response
from sqlalchemy.sql.expression import false
from werkzeug.utils import html
from es_natin import app, db, bcrypt
from es_natin.forms import GebruikerForm, InloggenForm, GebruikersFileForm, ExamForm, VraagForm, VragenFileForm, QuizForm, FeedbackForm
from es_natin.models import Gebruiker, Exam, Vraag, Resultaat, Beantwoord, Feedback
from flask_login import login_user, current_user, logout_user
from sqlalchemy.sql import func
import pdfkit 




# INLOGGEN 
@app.route('/', methods=['GET', 'POST'])
@app.route('/inloggen', methods=['GET', 'POST'])
def inloggen():
    form = InloggenForm()
    if form.validate_on_submit():
        gebruiker = Gebruiker.query.filter_by(gebruikersnaam=form.gebruikersnaam.data).first()
        if gebruiker and gebruiker.wachtwoord==form.wachtwoord.data and gebruiker.rol == "Admin":
            login_user(gebruiker)
            return redirect(url_for('admin_home'))
        elif gebruiker and gebruiker.wachtwoord==form.wachtwoord.data and gebruiker.rol == "Student":
            login_user(gebruiker)
            return redirect(url_for('student_home', studentid=gebruiker.id))
        else:
            flash('Login mislukt!', 'danger')
    return render_template('inloggen.html', title='Inloggen', form=form)

@app.route('/uitloggen')
def uitloggen():
    logout_user()
    return redirect(url_for('inloggen'))



# ADMIN Gebruikers
@app.route('/Admin/Home')
def admin_home():
    aantgeb = Gebruiker.query.count()
    aantadm = Gebruiker.query.filter_by(rol="Admin").count()
    aantstu = Gebruiker.query.filter_by(rol="Student").count()
    aantexam = Exam.query.count()
    aantopen = Exam.query.filter_by(status="Open").count()
    aantgesl = Exam.query.filter_by(status="Gesloten").count()
    aantfeed = Feedback.query.count()
    return render_template('admin/home.html', title='Admin-Home', aantgeb=aantgeb, aantadm=aantadm, aantstu=aantstu, aantexam=aantexam, aantopen=aantopen, aantgesl=aantgesl, aantfeed=aantfeed)

# Gebruikers 
@app.route('/Admin/Gebruiker')
def gebruiker_overzicht():
    admins = Gebruiker.query.filter_by(rol='Admin').all()
    studenten = Gebruiker.query.filter_by(rol='Student').all()
    return render_template('admin/gebruiker-overzicht.html', title='Admin Gebruikers Toevoegen', admins=admins, studenten=studenten, legend='Admin Gebruiker Toevoegen')


@app.route('/Admin/Gebruiker/toevoegen', methods=['GET', 'POST'])
def gebruiker_add():
    form = GebruikerForm()
    if form.validate_on_submit():
        gebruiker = Gebruiker(gebruikersnaam=form.gebruikersnaam.data, wachtwoord=form.wachtwoord.data, rol=form.rol.data)
        db.session.add(gebruiker)
        db.session.commit()
        flash(f'Gebruiker aangemaakt', 'success')
        return redirect(url_for('gebruiker_overzicht'))
    return render_template('admin/gebruiker-add.html', title='Admin Gebruiker Toevoegen', form=form, legend='Gebruiker Toevoegen')

@app.route('/Admin/Gebruiker/<int:gebruiker_id>/bewerken', methods=['GET', 'POST'])
def gebruiker_bewerken(gebruiker_id):
    gebruiker = Gebruiker.query.get_or_404(gebruiker_id)
    form = GebruikerForm()
    if form.validate_on_submit():
        gebruiker.gebruikersnaam = form.gebruikersnaam.data
        gebruiker.wachtwoord = form.wachtwoord.data
        gebruiker.rol = form.rol.data
        db.session.commit()
        flash(f'Gebruiker Bewerkt', 'success')
        return redirect(url_for('gebruiker_overzicht'))
    if request.method == 'GET':
        form.gebruikersnaam.data = gebruiker.gebruikersnaam
        form.wachtwoord.data = gebruiker.wachtwoord
        form.rol.data = gebruiker.rol
    return render_template('admin/gebruiker-add.html', title='Admin Gebruiker Bewerken', form=form, legend='Gebruiker Bewerken')




@app.route('/Admin/Gebruiker/<int:gebruikerid>/verwijderen', methods=['GET', 'POST'])
def gebruiker_verwijderen(gebruikerid):
    gebruiker = Gebruiker.query.get_or_404(gebruikerid)
    db.session.delete(gebruiker)
    db.session.commit()
    flash(f'Gebruiker Verwijderd', 'success')
    return redirect(url_for('gebruiker_overzicht'))


@app.route('/Admin/Student/<int:gebruikerid>/verwijderen', methods=['GET', 'POST'])
def student_verwijderen(gebruikerid):
    gebruiker = Gebruiker.query.get_or_404(gebruikerid)
    resultaten = Resultaat.query.filter_by(student_id=gebruikerid).all()
    feedbacks = Feedback.query.filter_by(student_id=gebruikerid).all()
    with db.session.no_autoflush:
        if db.session.query(Resultaat.id).filter_by(student_id=gebruiker.id).scalar() is not None:
            for resultaat in resultaten:
                beantwoorden = Beantwoord.query.filter_by(resultaat_id=resultaat.id).all()
            for beantwoord in beantwoorden:
                db.session.delete(beantwoord)
            db.session.delete(resultaat)
            db.session.delete(gebruiker)
        else:
            db.session.delete(gebruiker)
        if db.session.query(Feedback.id).filter_by(student_id=gebruiker.id).scalar() is not None:
            for feedback in feedbacks:
                db.session.delete(feedback)
        db.session.commit()
    flash(f'Student Verwijderd', 'success')
    return redirect(url_for('gebruiker_overzicht'))
    

@app.route('/gebruikers-file', methods=['GET', 'POST'])
def gebruikers_file():
    form = GebruikersFileForm()
    if form.validate_on_submit():
        csv_file = form.upload.data
        csv_file = TextIOWrapper(csv_file, encoding='utf-8')
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            gebruiker = Gebruiker(gebruikersnaam=row[0], wachtwoord=row[1], rol=row[2])
            db.session.add(gebruiker)
            db.session.commit()
            print(gebruiker)
        flash(f'Gebruikers-File Toegevoerd', 'success')
        return redirect(url_for('gebruiker_overzicht'))
    return render_template('admin/gebruiker-file.html', title='Admin-Gebruiker', form=form)



                # EXAM
@app.route('/Admin/Examen')
def exam_overzicht():
    geslotens = Exam.query.filter_by(status="Gesloten").order_by(Exam.id.desc()).all()
    opens = Exam.query.filter_by(status="Open").order_by(Exam.id.desc()).all()
    return render_template('exam/exam-overzicht.html', title='Admin-Exam', geslotens=geslotens, opens=opens)

@app.route('/Admin/Exam/toevoegen', methods=['GET', 'POST'])
def exam_add():
    form = ExamForm()
    if form.validate_on_submit():
        exam = Exam(examnaam=form.examnaam.data, vak=form.vak.data,klas=form.klas.data, datum=form.datum.data, duur=form.duur.data, status=form.status.data)
        db.session.add(exam)
        db.session.commit()
        flash(f'Exam aangemaakt', 'success')
        return redirect(url_for('exam_overzicht'))
    return render_template('exam/exam-add.html', title='Admin-Exam', form=form, legend='Gebruikers Toevoegen')

@app.route('/Admin/Examen/<int:examid>/bewerken', methods=['GET', 'POST'])
def exam_bewerken(examid):
    exam = Exam.query.get_or_404(examid)
    form = ExamForm()
    if form.validate_on_submit():
        exam.examnaam = form.examnaam.data
        exam.vak = form.vak.data
        exam.klas = form.klas.data
        exam.datum = form.datum.data
        exam.duur = form.duur.data
        exam.status = form.status.data
        db.session.commit()
        flash(f'Exam Bewerkt', 'success')
        return redirect(url_for('exam_overzicht'))
    if request.method == 'GET':
        form.examnaam.data = exam.examnaam
        form.vak.data = exam.vak
        form.klas.data = exam.klas
        form.datum.data = exam.datum
        form.duur.data = exam.duur
        form.status.data = exam.status
    return render_template('exam/exam-add.html', title='Admin-Exam-Bewerken', form=form, legend='Exam Bewerken')

@app.route('/Admin/Exam/<int:examid>/verwijderen', methods=['GET', 'POST'])
def exam_verwijderen(examid):
    exam = Exam.query.get_or_404(examid)
    vragen = Vraag.query.filter_by(exam_id=examid).all()
    for vraag in vragen:
        db.session.delete(vraag)
    db.session.delete(exam)       
    db.session.commit()
    flash(f'Exam Verwijderd', 'success')
    return redirect(url_for('exam_overzicht'))



                # EXAMEN/VRAGEN
@app.route('/Admin/Exam/<int:examid>/Vragen')
def exam_view(examid):
    exam = Exam.query.get_or_404(examid)
    vragen = Vraag.query.filter_by(exam_id=examid).all()
    examinfo = Exam.query.get(examid)
    return render_template('exam/exam-view.html', title='Admin-Exam', vragen=vragen, examinfo=examinfo)

@app.route('/Admin/Exam/<int:examid>/Vraag/toevoegen', methods=['GET', 'POST'])
def vraag_add(examid):
    exam = Exam.query.get_or_404(examid)
    examinfo = Exam.query.get(examid)
    form = VraagForm()
    if form.validate_on_submit():
        vraag = Vraag(vraaginfo=form.vraaginfo.data, keuze_a=form.keuzeA.data, keuze_b=form.keuzeB.data, keuze_c=form.keuzeC.data, keuze_d=form.keuzeD.data, antwoord=form.antwoord.data, punt=form.punt.data, exam_id=examid)
        db.session.add(vraag)
        db.session.commit()
        flash(f'Vraag aangemaakt', 'success')
        return redirect(url_for('exam_view', examid=examid))
    return render_template('exam/vraag-add.html', title='Vragen-Toevoegen', form=form, examinfo=examinfo, legend='Vragen Toevoegen')

@app.route('/Admin/Vragen/<int:vraagid>/bewerken', methods=['GET', 'POST'])
def vraag_bewerken(vraagid):
    vraag = Vraag.query.get_or_404(vraagid)
    examinfo = vraag.exam
    form = VraagForm()
    if form.validate_on_submit():
        vraag.vraaginfo = form.vraaginfo.data
        vraag.keuze_a   = form.keuzeA.data
        vraag.keuze_b   = form.keuzeB.data
        vraag.keuze_c   = form.keuzeC.data
        vraag.keuze_d  = form.keuzeD.data
        vraag.antwoord  = form.antwoord.data
        vraag.punt      = form.punt.data
        db.session.commit()
        flash(f'Vraag Bewerkt', 'success')
        return redirect(url_for('exam_view', examid = examinfo.id))
    if request.method == 'GET':
        form.vraaginfo.data = vraag.vraaginfo
        form.keuzeA.data    = vraag.keuze_a
        form.keuzeB.data    = vraag.keuze_b
        form.keuzeC.data    = vraag.keuze_c
        form.keuzeD.data    = vraag.keuze_d
        form.antwoord.data  = vraag.antwoord
        form.punt.data      = vraag.punt 
    return render_template('exam/vraag-add.html', title='Vragen-Bewerken', form=form, examinfo=examinfo, legend='Vragen Bewerken')

@app.route('/Admin/Vragen/<int:vraagid>/verwijderen', methods=['GET', 'POST'])
def vraag_verwijderen(vraagid):
    vraag = Vraag.query.get_or_404(vraagid)
    examinfo = vraag.exam
    db.session.delete(vraag)
    db.session.commit()
    flash(f'Vraag Verwijderd', 'success')
    return redirect(url_for('exam_view', examid = examinfo.id))

@app.route('/Admin/Exam/<int:examid>/Vraag/vragen-file', methods=['GET', 'POST'])
def vraag_file(examid):
    exam = Exam.query.get_or_404(examid)
    examinfo = Exam.query.get(examid)
    form = VragenFileForm()
    if form.validate_on_submit():
        csv_file = form.upload.data
        csv_file = TextIOWrapper(csv_file, encoding='utf-8')
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            vragen = Vraag(vraaginfo=row[0], keuze_a=row[1], keuze_b=row[2], keuze_c=row[3], keuze_d=row[4], antwoord=row[5], punt=row[6], exam_id=exam.id)
            db.session.add(vragen)
            db.session.commit()
        flash(f'Vragen File Toegevoerd', 'success')
        return redirect(url_for('exam_view', examid=exam.id))
    return render_template('exam/vraag-file.html', title='Vragen-Toevoegen', form=form, examinfo=examinfo)




# Resultaten 
@app.route('/Admin/Resultaten')
def resultaten_overzicht():
    examen = Exam.query.all()
    return render_template('resultaten/resultaten-overzicht.html', title='Admin-Resultaten', examen=examen)

@app.route('/Admin/Resultaten/<int:examid>/view')
def resultaten_view(examid):
    exam = Exam.query.get_or_404(examid)
    examinfo = Exam.query.get(examid)
    resultaten = Resultaat.query.filter_by(exam_id=examid).all()
    return render_template('resultaten/resultaten-view.html', title='Admin-Resultaten', examinfo=examinfo, resultaten=resultaten)




@app.route('/Admin/Resultaten/Beantwoord/<int:resultaatid>')
def resultaten_beantwoord(resultaatid):
    resultaat = Resultaat.query.get_or_404(resultaatid)
    beantwoorden=Beantwoord.query.filter_by(resultaat_id=resultaatid).all()
    return render_template('resultaten/resultaten-antwoord.html', title='Admin-Resultaten', resultaat=resultaat, beantwoorden=beantwoorden)


# Studenten Gebruikers
@app.route('/Student/<int:studentid>/Home')
def student_home(studentid):
    student = Gebruiker.query.get(studentid)
    examen = Exam.query.filter_by(status='Open').all()
    return render_template('student/home.html', title='Student Home', examen=examen, student=student)


# Quiz
@app.route('/Student/<int:studentid>/Quiz/<int:examid>/', methods=['GET', 'POST'])
def quiz(examid, studentid):    
    exam = Exam.query.get_or_404(examid)
    student = Gebruiker.query.get_or_404(studentid)
    resultaten = Resultaat.query.all()
    # check als student al een examn heeft gemaakt
    if db.session.query(Resultaat.id).filter_by(student_id=student.id, exam_id=exam.id).scalar() is not None:
        # print('Student heeft een exam gemaakt')
        flash(f'Student heeft al exam gemaakt', 'success')
        return redirect(url_for('student_home', studentid=student.id))
    else:
        print('Student heeft NIET een exam gemaakt')
    resultaatinfo = Resultaat(student_id=studentid, exam_id=examid)
    db.session.add(resultaatinfo)
    quizvragen = Vraag.query.filter_by(exam_id=examid).all()
    resultaat = Resultaat.query.filter_by(student_id=studentid, exam_id=examid).first()
    form = QuizForm()
    if form.validate_on_submit():
        beantwoorden = request.form.getlist('beantwoordkeuze')
        # antwoorden opslagen
        for qz, quizvraag in enumerate(quizvragen):
            for beat, beantwoord in enumerate(beantwoorden):
                if qz==beat:
                    if quizvraag.antwoord == beantwoord:
                        beantwoordk = Beantwoord(beantwoordkeuze=beantwoord, punten=quizvraag.punt, vraag_id= quizvraag.id, resultaat_id=resultaat.id)
                        db.session.add(beantwoordk)
                        db.session.commit()
                    elif quizvraag.antwoord != beantwoord:
                        beantwoordk = Beantwoord(beantwoordkeuze=beantwoord, punten="0", vraag_id= quizvraag.id, resultaat_id=resultaat.id)
                        db.session.add(beantwoordk)
                        db.session.commit()
        # cijfer
        result = db.session.query(func.sum(Beantwoord.punten)).filter(Beantwoord.resultaat_id== resultaat.id).all()
        myString = str(result)
        newString1 = myString.replace('[(', '')
        newString2 = newString1.replace(',)]', '')
        print("Sum of all the elements of an array: " + newString2)
        resultaat.cijfer=newString2
        db.session.commit()
        return redirect(url_for('pdf', studentid=student.id, resultaatid=resultaat.id))
    return render_template('student/quiz.html', title='QUIZ', quizvragen=quizvragen , form=form, exam=exam)

@app.route('/pdf/<int:studentid>/<int:resultaatid>')
def pdf(studentid, resultaatid):
    student = Gebruiker.query.get_or_404(studentid)
    resultaat = Resultaat.query.get_or_404(resultaatid)
    rendered = render_template("student/pdf.html", student=student, resultaat=resultaat)
    pdf = pdfkit.from_string(rendered, False)
    response = make_response(pdf)
    response.headers["Content-Type"] = 'application/pdf'
    response.headers["Content-Disposition"] = 'inline; filename=output.pdf'
    return response

@app.route('/Student/<int:studentid>/Eind')
def student_eind(studentid):
    student = Gebruiker.query.get_or_404(studentid)
    return render_template('student/eind.html', title='Student Eind', student=student)

@app.route('/Admin/Feedback/')
def feedback_overzicht():
    feedbacks = Feedback.query.all()
    return render_template('feedback/feedback-overzicht.html', title='Admin-Feedback', feedbacks=feedbacks)

@app.route('/Student/<int:studentid>/Feedback', methods=['GET', 'POST'])
def feedback_toevoegen(studentid):
    student = Gebruiker.query.get_or_404(studentid)
    form = FeedbackForm()
    if form.validate_on_submit():
        feedback = Feedback(feedbackinfo=form.feedbackinfo.data, student_id=studentid)
        db.session.add(feedback)
        db.session.commit()
        flash(f'Feedback Toegevoerd', 'success')
        return redirect(url_for('student_eind', studentid=student.id))
    return render_template('feedback/feedback-add.html', title='Feedback', form=form, student=student)