import smtplib
from flask import Flask, render_template, redirect, url_for,request,render_template_string,flash,Session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
import wave
import math
from flask import jsonify 
from datetime import date
from flask_uploads import UploadSet, configure_uploads, AUDIO
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import contextlib
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['wav', 'mp3'])

import speech_recognition as sr
app = Flask(__name__)
app.secret_key = 'random string'

r = sr.Recognizer()
wavaudio = UploadSet('files', AUDIO)
filename1=" "
name=" "
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/mayur/flaskblock/random/building_user_login_system-master/finish/site.db'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


#creating the tables
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

    @classmethod
    def is_user_name_taken(cls, username):
      return db.session.query(db.exists().where(User.username==username)).scalar()
    
    @classmethod
    def is_email_taken(cls, email):
      return db.session.query(db.exists().where(User.email==email)).scalar()


    
class audiototext(UserMixin, db.Model):
    id= db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15))
    filename = db.Column(db.String(50))
    duration = db.Column(db.Integer)
    uploaddate     = db.Column(db.Integer)
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

app.config['UPLOADED_FILES_DEST'] = 'static/audio'
configure_uploads(app, wavaudio)
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/success1')
def success1():
    return render_template('success.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return '<h1>Invalid username or password</h1>'
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html', form=form)

@app.route('/upload3/', methods=['GET', 'POST'])
def upload3():
	content = request.form.get('user_input')
	mail=smtplib.SMTP('smtp.gmail.com',587)
	mail.starttls()
	receiver=request.form.get('fname')
	print(receiver)
	if receiver=='':
		receiver='mayurwaghmode17@gmail.com'
	mail.login('waghmodemayur17@gmail.com','Iamsmart')
	mail.sendmail('waghmodemayur17@gmail.com',receiver,content)
	mail.quit()
	flash('You were successfully logged in')
	return render_template('upload3.html',audiotext = content,filename = filename1,audiofile=name)

@app.route('/upload1/', methods=['GET', 'POST'])
def upload():
	if request.method == 'POST' and 'au' in request.files:
	      filename = wavaudio.save(request.files['au'])
	      global name
	      name=filename
	      global filename1
	      filename1="/static/audio/"+filename
	      a = sr.Recognizer()
	      today = date.today()
	      d1 = today.strftime("%d/%m/%Y")
	      audio = 'static/audio/{}'.format(filename)
	      with sr.AudioFile(audio) as source:
	        audio = a.record(source)
	        print ('Done!')
	      try:
	        text = a.recognize_google(audio)
	        with open("output.txt","w") as f:
		  
	          f.write(filename1)
	          content=text
	          filename=audio='static/audio/{}'.format(filename)
		                     
	        with contextlib.closing(wave.open(filename,'r')) as f1:
	          frames = f1.getnframes()
	          rate = f1.getframerate()
	          duration = frames / float(rate)
	          print(duration)
	        
	      except Exception as e:
	        return (e)
	      new_file =audiototext(username=current_user.username, filename=name, duration=duration, uploaddate=d1)
	      db.session.add(new_file)
	      db.session.commit()
	      print(current_user.username)
	      print(filename)
	      print(duration)
	      today = date.today()
	      d1 = today.strftime("%d/%m/%Y")
	      print(d1)
	      return render_template('upload3.html',audiotext=text,filename = filename1,file=name)
	else:
	    	return render_template('upload.html',username=current_user.username)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if User.is_user_name_taken(form.data['username']):
        return jsonify({'username': 'This username is already taken!'}), 409
    if User.is_email_taken(form.data['email']):
       	return jsonify({'email': 'This email is already taken!'}), 409
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('success1'))
   
    return render_template('signup.html', form=form)
	
        #return '<h1>New user has been created!</h1>'
   
@app.route('/dashboard')
@login_required
def dashboard():
    name=current_user.username
    duration=0
    usage=audiototext.query.filter_by(username=name)
    for d1 in usage:
    	duration=d1.duration+duration
    return render_template('dashboard.html', name=current_user.username, usage1=usage,duration=math.ceil(duration))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
