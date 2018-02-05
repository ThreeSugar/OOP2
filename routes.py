#on the command line, please change directory with 'cd' to wherever this app is
#then enter 'python routes.py' on the command line to activate website

import os
import random
from flask import Flask, render_template, url_for, request, session, redirect, send_from_directory, flash, \
jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import select, func, or_, and_, between, desc
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message
import datetime
import pprint

from hashids import Hashids
from lib import message_builder
import requests

from models import *

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin

from flask_uploads import UploadSet, configure_uploads, IMAGES

import pyrebase

app = Flask(__name__)
admin = Admin(app, name = 'LifeStyle28', template_mode = 'bootstrap3')


#EMAIL SETTINGS
app.config.update(
	DEBUG=True,
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = 'findgym2@gmail.com',
	MAIL_PASSWORD = 'uaplwjtchijsoknk',
    MAIL_DEFAULT_SENDER = 'findgym2@gmail.com'
	)

mail = Mail(app)

def sendmail(mail, msg_subject, msg_sender, msg_recipients, message_html):
    message = Message(msg_subject, sender = msg_sender, recipients = msg_recipients)
    message.html = message_html
    mail.send(message)
    return True

Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/database.db'

gyms_email_address = 'thisappemail@gmail.com'


app.secret_key = "development-key"
db.init_app(app)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(APP_ROOT, 'static')

photos = UploadSet('photos', IMAGES)

photodest = os.path.join(APP_ROOT, 'static/raymond/img')

app.config['UPLOADED_PHOTOS_DEST'] = photodest
configure_uploads(app, photos)

#FIREBASE/CYNTHIA

API_KEY = 'AIzaSyC-untCAlzyRtrAuJ6ShicN0aHCHMD94jg'

hashid_salt = 'impossible to guess'
hashids = Hashids(salt=hashid_salt, min_length=4)

config = {
  "apiKey": "AIzaSyDrw2z11cWBjIVNWYKYcLCdjR0wCJ3w7HY",
  "authDomain": "gym-finder-78813.firebaseapp.com",
  "databaseURL": "https://gym-finder-78813.firebaseio.com",
  "storageBucket": "gym-finder-78813.appspot.com"
}

  #this is to register as an admin with full read/write access

firebase = pyrebase.initialize_app(config)
firedb = firebase.database()  

#HELPERS
@app.context_processor 
def utility_processor():
    def render_user_id():  #this function is avaliable to all templates, just display it with {{ -yourfunction- }}
        user = User.query.filter_by(username=current_user.username).first()
        uid = user.uid
        return uid

    def check_inbox():
        read = []
        inbox = UserMail.query.filter_by(seen=False).filter_by(target=current_user.username).all()
        for i in inbox:
            read.append(i)
        return len(read)

    def tag_read(id):
        seen = False
        inbox = UserMail.query.filter_by(id=id).first()
        if inbox.seen:
            seen = True 
        else:
            seen = False
        return seen

    def tag_flag(id):
        flag = False
        inbox = UserMail.query.filter_by(id=id).first()
        if inbox.flag:
            flag = True 
        else:
            flag = False
        return flag

    def check_playlist_save(play_id, vid_id):
        is_saved = SavePlaylistVids.query.filter_by(playlist_id=play_id).filter_by(video_id=vid_id).first()
        if is_saved is not None:
            return True
        else:
            return False
        
    def show_cart_price():
        price = 0
        cart = Cart.query.all()
        for c in cart:
            price += c.subtotal

        return "{0:.2f}".format(price)

    def cart_count():
        try:
            count = 0
            user = User.query.filter_by(username=current_user.username).first()
            uid = user.uid
            cart = Cart.query.filter(Cart.user_id==uid).all()
            for c in cart:
                count += 1
        except:
            count = 0
            cart = Cart.query.filter(Cart.user_id == 0).all()
            for c in cart:
                count += 1
        return count

    def cal_bmr():
        bmr = BMR.query.first()
        return "{0:.0f}".format(bmr.bmr)

    def cal_cal():
        bmr = BMR.query.first()
        return "{0:.0f}".format(bmr.cal)
    

    return dict(render_user_id=render_user_id, check_inbox=check_inbox, tag_read=tag_read, tag_flag=tag_flag, 
                check_playlist_save = check_playlist_save, show_cart_price=show_cart_price, cart_count=cart_count,
                cal_bmr=cal_bmr, cal_cal=cal_cal)


#ADMIN OVERALL

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(BlogPost, db.session))
path = os.path.join(os.path.dirname(__file__), 'static/assets')
admin.add_view(FileAdmin(path, name='Videos'))
admin.add_view(ItemView(Item, db.session))
admin.add_view(ModelView(Recipe, db.session))
admin.add_view(ModelView(RecipeIngredients, db.session))
admin.add_view(ModelView(Cart, db.session))
admin.add_view(ModelView(Orders, db.session))
admin.add_view(ModelView(Comments, db.session))
admin.add_view(ModelView(BMR, db.session))
admin.add_view(ModelView(FitnessLib, db.session))


###


#HOMEPAGE (DO NOT TOUCH)
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index(): #did not use wtforms for this because wtforms might accidentally break the layout of the site
    if request.method == 'POST':
        msg = Message(subject= "Feedback",
                              recipients=['threesugar123@gmail.com'])
        msg.html = 'From: {} ({}) <br> <br> Subject: {} <br> <br> Message: {}'.format(request.form['name'], 
        request.form['email'], request.form['subject'], request.form['message'])
        mail.send(msg)
        flash('Thank you for your feedback!')
        return redirect(url_for('index'))

    return render_template('index.html')

###

#LOGIN/REGISTER/SIGNUP (DO NOT TOUCH)
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data): #SHA256 hashed 50,000 times
                login_user(user)
                return redirect(url_for('dashboard'))
        else: 
            flash('Invalid username or password!')
            return redirect(url_for('login'))

    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if current_user.is_authenticated == True:
        return redirect(url_for('index'))

    if form.validate_on_submit():
        new_user = User(firstname=form.firstname.data, lastname= form.lastname.data, 
        username=form.username.data, email=form.email.data, password = form.password.data)

        try:
            db.session.add(new_user)
            db.session.commit()

        except IntegrityError: #because of db's unique constraint
            flash('Email or Username has already been taken!')
            return redirect(url_for('signup'))

        return redirect(url_for('login'))

    return render_template('signup.html', form = form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

#PROFILE
@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.filter_by(username=current_user.username).first()
    uid = user.uid
    username = user.username
    user_profile = Profile.query.filter_by(userid=uid).first()

    if user_profile is None:
        profile_init = Profile(userid = uid, username = username, desc = 'Write your description here.',
        interests = 'Write your interests here.', location='Write your location here.')
        db.session.add(profile_init)
        db.session.commit()

    user_profile = Profile.query.filter_by(userid=uid).first()
    
    return render_template('profile.html', user_profile=user_profile)

@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    user_profile = Profile.query.filter_by(username=username).first()
    user = User.query.filter_by(username=username).first()
    user_email = user.email

    form = SendMessage(to = username)
    if form.validate_on_submit():
        new_msg = UserMail(sender=current_user.username, target=form.to.data, subject=form.subject.data,
        message=form.message.data, seen=False)
        db.session.add(new_msg)
        db.session.commit() 
        flash("Your message was successfully sent.", 'success')
        return redirect(url_for('inbox'))

    if current_user.is_authenticated:
        return render_template('otherprofile.html', form=form, user_profile=user_profile, user_email=user_email)

    else:
        return render_template('userprofile.html', user_profile=user_profile, user_email=user_email)


@app.route('/profile/edit/<id>', methods=['GET', 'POST'])
@login_required
def editprofile(id):
    user = Profile.query.filter_by(userid=id).first()
    form = EditProfile(obj=user, desc=user.desc, interests=user.interests, location=user.location)
    uid = user.userid
    user_profile = Profile.query.filter_by(userid=uid).first()
    
    if form.validate_on_submit():
        user.desc = form.desc.data
        user.interests = form.interests.data
        user.location = form.location.data
        db.session.commit()
        return redirect(url_for('dashboard')) 
        
    return render_template('editprofile.html', form=form)

#MESSAGE

@app.route('/inbox')
def inbox():
    savestate = SaveInboxState.query.filter_by(username=current_user.username).first()
    inbox = UserMail.query.filter_by(target=current_user.username).order_by("date desc").all()
    subjectasc = True
    dateasc = True

    if savestate is None:
        savestate_init = SaveInboxState(username=current_user.username, subjectasc = False, subjectdesc = False, \
        dateasc = False, datedesc = True)
        db.session.add(savestate_init)
        db.session.commit()

    else:

        if savestate.subjectasc:
            inbox = UserMail.query.filter_by(target=current_user.username).order_by("subject asc").all()
            subjectasc = True
        
        elif savestate.subjectdesc:
            inbox = UserMail.query.filter_by(target=current_user.username).order_by("subject desc").all()
            subjectasc = False
        
        elif savestate.dateasc:
            inbox = UserMail.query.filter_by(target=current_user.username).order_by("date asc").all()
            dateasc = True
        
        elif savestate.datedesc:
            inbox = UserMail.query.filter_by(target=current_user.username).order_by("date desc").all()
            dateasc = False

    return render_template('inbox.html', inbox=inbox, subjectasc=subjectasc, dateasc=dateasc)

#SORT INBOX

@app.route('/inbox/sort/ascending/<type>', methods=['GET', 'POST'])
def sortasc(type):
    inbox = UserMail.query.filter_by(target=current_user.username).order_by(str(type) + " " + "asc").all() # a list containing objects
    sort_type = str(type)
    savestate = SaveInboxState.query.filter_by(username=current_user.username).first()
    subjectasc = True
    dateasc = True

    if sort_type == 'date':
        savestate.dateasc = True
        savestate.datedesc = False
        savestate.subjectasc = False
        savestate.subjectdesc = False
        db.session.commit()

    elif sort_type == 'subject':
        savestate.subjectasc = True
        savestate.subjectdesc = False
        savestate.dateasc = False
        savestate.datedesc = False
        db.session.commit()
    
    return jsonify({'inbox': render_template('filterinbox.html', inbox=inbox, subjectasc=subjectasc, dateasc=dateasc)}) 

@app.route('/inbox/sort/descending/<type>', methods=['GET', 'POST'])
def sortdesc(type):
    inbox = UserMail.query.filter_by(target=current_user.username).order_by(str(type) + " " + "desc").all()
    sort_type = str(type)
    savestate = SaveInboxState.query.filter_by(username=current_user.username).first()
    subjectasc = False
    dateasc = False

    if sort_type == 'date':
        savestate.dateasc = False
        savestate.datedesc = True
        savestate.subjectasc = False
        savestate.subjectdesc = False
        db.session.commit()

    elif sort_type == 'subject':
        savestate.subjectasc = False
        savestate.subjectdesc = True
        savestate.dateasc = False
        savestate.datedesc = False
        db.session.commit()

    return jsonify({'inbox': render_template('filterinbox1.html', inbox=inbox, dateasc=dateasc, subjectasc=subjectasc)}) 

#SORT FLAGGED

@app.route('/inbox/flag/sort/ascending/<type>', methods=['GET', 'POST'])
def sortflagasc(type):
    flagged = UserMail.query.filter_by(flag=True).filter_by(target=current_user.username)\
    .order_by(str(type) + " " + "asc").all()

    sort_type = str(type)
    savestate = SaveFlaggedState.query.filter_by(username=current_user.username).first()

    subjectasc = True
    dateasc = True
   
    if sort_type == 'date':
        savestate.dateasc = True
        savestate.datedesc = False
        savestate.subjectasc = False
        savestate.subjectdesc = False
        db.session.commit()

    elif sort_type == 'subject':
        savestate.subjectasc = True
        savestate.subjectdesc = False
        savestate.dateasc = False
        savestate.datedesc = False
        db.session.commit()

    return jsonify({'flagged': render_template('_filterflag.html', flagged=flagged, subjectasc=subjectasc, dateasc=dateasc)}) 

@app.route('/inbox/flag/sort/descending/<type>', methods=['GET', 'POST'])
def sortflagdesc(type):
    flagged = UserMail.query.filter_by(flag=True).filter_by(target=current_user.username)\
    .order_by(str(type) + " " + "desc").all()

    sort_type = str(type)
    savestate = SaveFlaggedState.query.filter_by(username=current_user.username).first()

    subjectasc = False
    dateasc = False

    if sort_type == 'date':
        savestate.dateasc = False
        savestate.datedesc = True
        savestate.subjectasc = False
        savestate.subjectdesc = False
        db.session.commit()

    elif sort_type == 'subject':
        savestate.subjectasc = False
        savestate.subjectdesc = True
        savestate.dateasc = False
        savestate.datedesc = False
        db.session.commit()

    return jsonify({'flagged': render_template('_filterflag1.html', flagged=flagged, subjectasc=subjectasc, dateasc=dateasc)}) 


#SORT SENT

@app.route('/inbox/send/sort/ascending/<type>', methods=['GET', 'POST'])
def sortsentasc(type):
    sent = UserMail.query.filter_by(sender=current_user.username).order_by(str(type) + " " + "asc").all()

    sort_type = str(type)
    savestate = SaveSentState.query.filter_by(username=current_user.username).first()

    subjectasc = True
    dateasc = True

    if sort_type == 'date':
        savestate.dateasc = True
        savestate.datedesc = False
        savestate.subjectasc = False
        savestate.subjectdesc = False
        db.session.commit()

    elif sort_type == 'subject':
        savestate.subjectasc = True
        savestate.subjectdesc = False
        savestate.dateasc = False
        savestate.datedesc = False
        db.session.commit()

    return jsonify({'sent': render_template('_filtersent.html', sent=sent, subjectasc=subjectasc, dateasc=dateasc)}) 

@app.route('/inbox/send/sort/descending/<type>', methods=['GET', 'POST'])
def sortsentdesc(type):
    sent = UserMail.query.filter_by(sender=current_user.username).order_by(str(type) + " " + "desc").all()
    sort_type = str(type)
    savestate = SaveSentState.query.filter_by(username=current_user.username).first()

    subjectasc = False
    dateasc = False

    if sort_type == 'date':
        savestate.dateasc = False
        savestate.datedesc = True
        savestate.subjectasc = False
        savestate.subjectdesc = False
        db.session.commit()

    elif sort_type == 'subject':
        savestate.subjectasc = False
        savestate.subjectdesc = True
        savestate.dateasc = False
        savestate.datedesc = False
        db.session.commit()

    return jsonify({'sent': render_template('_filtersent1.html', sent=sent, subjectasc=subjectasc, dateasc=dateasc)}) 

#MARK

@app.route('/inbox/mark', methods=['GET', 'POST'])
def mark_read():
        read = request.get_json()
        read_id = read['read_id']
        inboxes = UserMail.query.filter_by(id=read_id).first()
        marker = inboxes.seen

        if marker == True:
            inboxes.seen = False
            db.session.commit()
            return jsonify({'noread' : 'noread', 'read_id' : inboxes.id})

        elif marker == False:
            inboxes.seen = True
            db.session.commit()
            return jsonify({'read' : 'read', 'read_id' : inboxes.id})

        

@app.route('/inbox/flag', methods=['GET', 'POST'])
def mark_flag():
        flag = request.get_json()
        flag_id = flag['flag_id']
        inboxes = UserMail.query.filter_by(id=flag_id).first()
        marker = inboxes.flag

        if marker == True:
            inboxes.flag = False
            db.session.commit()
            return jsonify({'noflag' : 'noflag', 'flag_id' : inboxes.id})

        elif marker == False:
            inboxes.flag = True
            db.session.commit()
            return jsonify({'flag' : 'flag', 'flag_id' : inboxes.id})

@app.route('/inbox/flag/remove', methods=['GET', 'POST'])
def removeflag():
    flag = request.get_json()
    flag_id = flag['flag_id']
    selected_msg = UserMail.query.filter_by(flag=True).filter_by(target=current_user.username).filter_by(id=flag_id).first()
    selected_msg.flag = False
    db.session.commit()

    flagged = UserMail.query.filter_by(flag=True).filter_by(target=current_user.username).\
            order_by("date desc").all()

    savestate = SaveSentState.query.filter_by(username=current_user.username).first()

    subjectasc = True
    dateasc = True

    if savestate is None:
        savestate_init = SaveFlaggedState(username=current_user.username, subjectasc = False, subjectdesc = False, \
        dateasc = False, datedesc = True)
        db.session.add(savestate_init)
        db.session.commit()

    else:

        if savestate.subjectasc:
            flagged = UserMail.query.filter_by(flag=True).filter_by(target=current_user.username).\
            order_by("subject asc").all()
        
        elif savestate.subjectdesc:
            flagged = UserMail.query.filter_by(flag=True).filter_by(target=current_user.username).\
            order_by("subject desc").all()
            subjectasc=False
        
        elif savestate.dateasc:
            flagged = UserMail.query.filter_by(flag=True).filter_by(target=current_user.username).\
            order_by("date asc").all()
        
        elif savestate.datedesc:
            flagged = UserMail.query.filter_by(flag=True).filter_by(target=current_user.username).\
            order_by("date desc").all()
            dateasc=False

    return jsonify({'removeflag' : render_template('_removeflag.html', flagged=flagged, subjectasc=subjectasc, dateasc=dateasc)})

@app.route('/inbox/flag/view')
def viewflagged():
    savestate = SaveFlaggedState.query.filter_by(username=current_user.username).first()
    flagged = UserMail.query.filter_by(flag=True).filter_by(target=current_user.username).\
            order_by("date desc").all()

    if savestate is None:
        savestate_init = SaveFlaggedState(username=current_user.username, subjectasc = False, subjectdesc = False, \
        dateasc = False, datedesc = True)
        db.session.add(savestate_init)
        db.session.commit()

    else:

        if savestate.subjectasc:
            flagged = UserMail.query.filter_by(flag=True).filter_by(target=current_user.username).\
            order_by("subject asc").all()
        
        elif savestate.subjectdesc:
            flagged = UserMail.query.filter_by(flag=True).filter_by(target=current_user.username).\
            order_by("subject desc").all()
        
        elif savestate.dateasc:
            flagged = UserMail.query.filter_by(flag=True).filter_by(target=current_user.username).\
            order_by("date asc").all()
        
        elif savestate.datedesc:
            flagged = UserMail.query.filter_by(flag=True).filter_by(target=current_user.username).\
            order_by("date desc").all()

    return render_template('flagged.html', flagged=flagged)

@app.route('/inbox/flag/view/<id>', methods=['GET', 'POST'])
def flaggedmsg(id):
    view_msg = UserMail.query.filter_by(id=id).first()
    db.session.commit()

    form = SendMessage(to = view_msg.sender)
    if form.validate_on_submit():
        new_msg = UserMail(sender=current_user.username, target=form.to.data, subject=form.subject.data,
        message=form.message.data, seen=False)
        db.session.add(new_msg)
        db.session.commit()
        flash("Your message was successfully sent.", 'success')
        return redirect(url_for('inbox'))

    return render_template('replyflagged.html', view_msg=view_msg, form=form)


@app.route('/inbox/send', methods=['GET', 'POST'])
def send():
    form = SendMessage()
    if form.validate_on_submit():
        new_msg = UserMail(sender=current_user.username, target=form.to.data, subject=form.subject.data,
        message=form.message.data, seen=False, flag=False)
        vaild_user = User.query.filter_by(username=form.to.data).first()
        if vaild_user:
            db.session.add(new_msg)
            db.session.commit()
            flash("Your message was successfully sent.", 'success')
            return redirect(url_for('inbox'))
        else:
            flash("This user does not exist.", 'error')
            return redirect(url_for('inbox'))


    return render_template('send.html', form=form)

@app.route('/inbox/view/<id>', methods=['GET', 'POST'])
def viewinbox(id):
    view_msg = UserMail.query.filter_by(id=id).first()
    view_msg.seen = True
    db.session.commit()

    form = SendMessage(to = view_msg.sender)
    if form.validate_on_submit():
        new_msg = UserMail(sender=current_user.username, target=form.to.data, subject=form.subject.data,
        message=form.message.data, seen=False)
        db.session.add(new_msg)
        db.session.commit()
        flash("Your message was successfully sent.", 'success')
        return redirect(url_for('inbox'))

    return render_template('message.html', view_msg=view_msg, form=form)

@app.route('/inbox/sent')
def sentinbox():
    savestate = SaveSentState.query.filter_by(username=current_user.username).first()
    sent = UserMail.query.filter_by(sender=current_user.username).order_by("date desc").all()

    if savestate is None:
        savestate_init = SaveSentState(username=current_user.username, subjectasc = False, subjectdesc = False, \
        dateasc = False, datedesc = True)
        db.session.add(savestate_init)
        db.session.commit()
    else:

        if savestate.subjectasc:
            sent = UserMail.query.filter_by(sender=current_user.username).order_by("subject asc").all()
        
        elif savestate.subjectdesc:
            sent = UserMail.query.filter_by(sender=current_user.username).order_by("subject desc").all()
        
        elif savestate.dateasc:
            sent = UserMail.query.filter_by(sender=current_user.username).order_by("date asc").all()
        
        elif savestate.datedesc:
            sent = UserMail.query.filter_by(sender=current_user.username).order_by("date desc").all()

    return render_template('sentmsg.html', sent=sent)

@app.route('/inbox/sent/view/<id>', methods=['GET', 'POST'])
def viewsent(id):
    view_msg = UserMail.query.filter_by(id=id).first()

    form = SendMessage(to = view_msg.sender)
    if form.validate_on_submit():
        new_msg = UserMail(sender=current_user.username, target=form.to.data, subject=form.subject.data,
        message=form.message.data, seen=False)
        db.session.add(new_msg)
        db.session.commit()
        flash("Your message was successfully sent.", 'success')
        return redirect(url_for('inbox'))

    return render_template('sendmessage.html', view_msg=view_msg, form=form)

@app.route('/inbox/delete/<id>')
def deleteinbox(id):
    view_msg = UserMail.query.filter_by(id=id).first()
    db.session.delete(view_msg)
    db.session.commit() 
    return redirect(url_for('inbox'))

@app.route('/inbox/sent/delete/<id>')
def deletesent(id):
    view_msg = UserMail.query.filter_by(sender=current_user.username).filter_by(id=id).first()
    db.session.delete(view_msg)
    db.session.commit() 
    return redirect(url_for('sentinbox'))

#VIDEO ADMIN (CRUD)

@app.route('/dashboard/video')
@login_required
def dashboardvid():
    return render_template('viddash.html')

@app.route('/dashboard/video/manage')
@login_required
def vidmanage():
    videos = Video.query.filter_by(username = current_user.username).all()
    form = VideoSearch()
    return render_template('vidmanage.html', videos = videos, form=form)

@app.route('/dashboard/video/manage/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def videdit(id):
    video = Video.query.get_or_404(id)
    form = EditForm(obj=video, desc = video.description, options = video.category) #default values for form so that users don't have to retype everything
    if form.validate_on_submit():
        video.title = form.title.data
        video.description = form.desc.data
        video.category = form.options.data
        db.session.commit()
        flash('Video successfully edited!')
        return redirect(url_for('vidmanage')) #render template will cause a 'function not iterable error'

    return render_template('videdit.html', form = form)


@app.route('/dashboard/video/manage/delete/<int:id>')
@login_required
def viddelete(id):
    video = Video.query.get_or_404(id)
    db.session.delete(video)
    db.session.commit()
    flash('Video successfully deleted!')
    return redirect(url_for('vidmanage'))

@app.route('/dashboard/video/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = SelectForm()
    target = os.path.join(APP_ROOT, 'static/assets') #os ensures that the correct path will be rendered regardless of OS.
    print(target)
    print(request.files.getlist('file'))
    
    
    for file in request.files.getlist('file'):
        print(file)
        filename = file.filename
        destination = '/'.join([target, filename])

        try:
            new_vid = Video(link= filename, username = current_user.username, title =  form.title.data, description = form.desc.data, category= form.options.data)
            db.session.add(new_vid)
            db.session.commit()
            print('Accept incoming file: ', filename)
            print('Save it to: ', destination)
            file.save(destination)
            return redirect(url_for('vidmanage'))
        
        except IntegrityError: 
            error = True
            db.session.rollback()
            return render_template('dashvid.html', form=form, error=error) 
            #link has unique constraint because might run into filename conflict in local env


    return render_template('dashvid.html', form=form)     



#VIDEO

@app.route('/video/explore')
def explorevideo():
    form = VideoSearch()
    allvid = Video.query.order_by("date desc").limit(6)
    food = Video.query.filter_by(category = 'food').order_by("date desc").limit(6) #string literal query
    exercise = Video.query.filter_by(category = 'exercise').order_by("date desc").limit(6)
    music = Video.query.filter_by(category = 'music').order_by("date desc").limit(6)
    edu = Video.query.filter_by(category = 'educational').order_by("date desc").limit(6)

    if current_user.is_authenticated: 
        savedvid = VideoSaved.query.filter_by(savedname = current_user.username).order_by("saveddate desc").limit(3)
        return render_template('freevid.html', food=food, exercise=exercise, music=music, edu=edu, \
                                allvid=allvid, form=form, savedvid = savedvid)

    else:
        return render_template('freevid.html', food=food, exercise=exercise, music=music, edu=edu, \
                                allvid=allvid, form=form)

                     
@app.route('/video/<videoid>', methods=['GET', 'POST'])
def videoz(videoid):
    form = VideoSearch()
    videoid = Video.query.filter_by(id = videoid).first()
    vid = videoid.id
    title = videoid.title
    link = videoid.link
    name = videoid.username
    cat = videoid.category
    desc = videoid.description
    date = videoid.date
    comms = VideoComment.query.filter_by(videoid = vid).all() #videoid and id are two very different columns

    error = False
    signup_error = False

    #CUSTOM LOGIN TO REDIRECT BACK TO VIDEO

    vidform = LoginForm()
    if vidform.validate_on_submit():
        user = User.query.filter_by(email=vidform.email.data).first()
        if user is not None and user.check_password(vidform.password.data):
                login_user(user)
                return redirect(url_for('videoz', videoid = vid))
        else:
            error = True
            signup_error = False

    vidsignup = RegisterForm()
   
    if vidsignup.validate_on_submit():

        registered_user = User.query.filter_by(email=vidsignup.email.data).first()

        if registered_user is not None:
            error = False
            signup_error = True

        else:
            new_user = User(firstname=vidsignup.firstname.data, lastname= vidsignup.lastname.data, 
            username=vidsignup.username.data, email=vidsignup.email.data, password = vidsignup.password.data)

            try:
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
        
            except IntegrityError: #because of db's unique constraint 
                error = False
                signup_error = True
                                
            except:
                error = False
                signup_error = True
            
    #LIKE/DISLIKE FUNCTION

    likes = []
    dislikes = []

    vidlike = VideoLikes.query.filter_by(videoid = vid).filter_by(likes = 1).all()

    viddislike = VideoDislikes.query.filter_by(videoid = vid).filter_by(dislikes = 1).all()

    for v in vidlike:
        likes.append(v)
    
    for d in viddislike:
        dislikes.append(d)

    tlikes = len(likes)
    tdislike = len(dislikes)

    #SAVE FUNCTION

    curr_save = False
    
    if current_user.is_authenticated: #to fix a mysterious AnonMixin error that popped out for no reason
        saved = VideoSaved.query.filter_by(videoid = vid).filter_by(savedname = current_user.username).first()
        curr_save = False

        if saved is None:
            curr_save =  False

        elif saved is not None:
            curr_save = True


    #VIEW FUNCTION
    userview = VideoViews.query.filter_by(videoid=vid).filter_by(username=current_user.username).first()
    guestview = VideoViews.query.filter_by(videoid=vid).filter_by(username="Guest").first()
   
    if guestview is None and current_user.is_authenticated == False:
        guestinit = VideoViews(videoid=vid, username = "Guest")
        db.session.add(guestinit)
        db.session.commit()
        guestview = VideoViews.query.filter_by(videoid=vid).filter_by(username="Guest").first()
        guestview.views = 0 #make .views != null so that the += later on can work.
        db.session.add(guestview)
        db.session.commit()
        
    if guestview is not None and current_user.is_authenticated == False:
        guestview = VideoViews.query.filter_by(videoid=vid).filter_by(username="Guest").first()
        guestview.views += 1
        db.session.add(guestview)
        db.session.commit()
       
    if userview is None and current_user.is_authenticated == True:
        userinit = VideoViews(videoid=vid, username = current_user.username)
        db.session.add(userinit)
        db.session.commit()
        userview = VideoViews.query.filter_by(videoid=vid).filter_by(username=current_user.username).first()
        userview.views = 0 
        db.session.add(userview)
        db.session.commit()

    if userview is not None and current_user.is_authenticated == True: #the order of this statement matters for some reason
        userview = VideoViews.query.filter_by(videoid=vid).filter_by(username=current_user.username).first()
        userview.views += 1
        db.session.add(userview)
        db.session.commit()

    g = select([VideoViews.username]).where(VideoViews.username == "Guest")
    usersview = VideoViews.query.filter_by(videoid=vid).filter(~VideoViews.username.in_(g)).all()
    guestview = VideoViews.query.filter_by(videoid=vid).filter_by(username="Guest").all()

    uview = 0
    gview = 0

    for u in usersview:
        uview += u.views

    for g in guestview:
        gview += g.views

    tviews = uview + gview
    
    #FILTER RELATED
    
    s = select([Video.title]).where(Video.title == videoid.title)
    print(s) #debug purposes
    related = Video.query.filter_by(category = videoid.category).filter( ~Video.title.in_(s)).order_by("date desc").limit(5)
    # ~Video.title.in_(s) == Video.title NOT IN (select([Video.title]).where(Video.title == videoid.title))
    # 'NOT IN' omits all query results that contains videoid.title

    #ADD VIDEO DIRECTLY TO PLAYLIST

    all_playlist = FitnessPlaylist.query.filter_by(username=current_user.username).all()
    playform = AddToPlaylist()
    
    return render_template('displayvid1.html', link=link, name=name, cat=cat, desc=desc, \
                            date=date, title=title, vid = vid, comms = comms, form=form, related=related, \
                            tlikes = tlikes, tdislike = tdislike, \
                            curr_save = curr_save, vidform=vidform, vidsignup=vidsignup, error=error, \
                            signup_error=signup_error, tviews=tviews, all_playlist=all_playlist, \
                            playform=playform)

#CUSTOM LOGOUT
@app.route('/video/logout')
def vid_logout():
    logout_user()
    return redirect(url_for('explorevideo'))

#CUSTOM SIGNUP
@app.route('/video/signup', methods=['GET', 'POST'])
def vid_signup():
    form = RegisterForm()
    if current_user.is_authenticated == True:
        return redirect(url_for('vid_login'))

    if form.validate_on_submit():
        new_user = User(firstname=form.firstname.data, lastname= form.lastname.data, 
        username=form.username.data, email=form.email.data, password = form.password.data)

        try:
            db.session.add(new_user)
            db.session.commit()

        except IntegrityError: #because of db's unique constraint
            flash('Email or Username has already been taken!', 'error')
            return redirect(url_for('vid_signup'))

        flash('Account successfully registered!', 'success')
        return redirect(url_for('vid_login'))

    return render_template('videosignup.html', form=form)

#CUSTOM LOGIN
@app.route('/video/login', methods=['GET', 'POST'])
def vid_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data): #SHA256 hashed 50,000 times
                login_user(user)
                return redirect(url_for('explorevideo'))
        else: 
            flash('Invalid username or password!')
            return redirect(url_for('vid_login'))
    return render_template('videologin.html', form=form)


@app.route('/video/likes/<videoid>', methods=['GET', 'POST'])
def likevideo(videoid):
    videoid = Video.query.filter_by(id = videoid).first()
    vid = videoid.id

    vidlike = VideoLikes.query.filter_by(videoid = vid).\
    filter_by(username = current_user.username).filter_by(likes = 1).first()

    viddislike = VideoDislikes.query.filter_by(videoid = vid).\
    filter_by(username = current_user.username).filter_by(dislikes = 1).first()

    if vidlike is None and viddislike is None:    
        likes = VideoLikes(videoid = vid, username = current_user.username, likes = 1)
        db.session.add(likes)
        db.session.commit()

    elif vidlike is None and viddislike is not None:
        likes = VideoLikes(videoid = vid, username = current_user.username, likes = 1)
        db.session.add(likes)
        db.session.commit()

        db.session.delete(viddislike)
        db.session.commit()

    else:  #user can only like the video once 
        db.session.delete(vidlike)
        db.session.commit()

    likes = []
    dislikes = []

    vidlike = VideoLikes.query.filter_by(videoid = vid).filter_by(likes = 1).all()

    viddislike = VideoDislikes.query.filter_by(videoid = vid).filter_by(dislikes = 1).all()

    for v in vidlike:
        likes.append(v)
    
    for d in viddislike:
        dislikes.append(d)

    tlikes = len(likes)
    tdislike = len(dislikes)

    return jsonify({'likes' : tlikes, 'dislikes':tdislike})


@app.route('/video/dislikes/<videoid>', methods=['GET', 'POST'])
def dislikevideo(videoid):
    videoid = Video.query.filter_by(id = videoid).first()
    vid = videoid.id

    viddislike = VideoDislikes.query.filter_by(videoid = vid).\
    filter_by(username = current_user.username).filter_by(dislikes = 1).first()

    vidlike = VideoLikes.query.filter_by(videoid = vid).\
    filter_by(username = current_user.username).filter_by(likes = 1).first()


    if viddislike is None and vidlike is None:    
        dislikes = VideoDislikes(videoid = vid, username = current_user.username, dislikes = 1)
        db.session.add(dislikes)
        db.session.commit()

    elif viddislike is None and vidlike is not None:
        dislikes = VideoDislikes(videoid = vid, username = current_user.username, dislikes = 1)
        db.session.add(dislikes)
        db.session.commit()

        db.session.delete(vidlike)
        db.session.commit()

    else:  #user can only dislike the video once 
        db.session.delete(viddislike)
        db.session.commit()

    likes = []
    dislikes = []

    vidlike = VideoLikes.query.filter_by(videoid = vid).filter_by(likes = 1).all()

    viddislike = VideoDislikes.query.filter_by(videoid = vid).filter_by(dislikes = 1).all()

    for v in vidlike:
        likes.append(v)
    
    for d in viddislike:
        dislikes.append(d)

    tlikes = len(likes)
    tdislike = len(dislikes)

    return jsonify({'likes' : tlikes, 'dislikes' : tdislike})

@app.route('/video/save/<videoid>', methods=['GET', 'POST'])
def savevid(videoid):
    videoid = Video.query.filter_by(id = videoid).first()
    vid = videoid.id
    title = videoid.title
    link = videoid.link
    name = videoid.username
    cat = videoid.category
    desc = videoid.description
    date = videoid.date

    saved = VideoSaved.query.filter_by(videoid = vid).filter_by(savedname = current_user.username).first()

    svid = VideoSaved(videoid = vid, title = title, link = link, username = name, 
        savedname = current_user.username,
        category = cat, description = desc, date = date)

    curr_save = False

    if saved is None:
         curr_save = True
         db.session.add(svid)
         db.session.commit()
         return jsonify({'save':'saved'})
    
    elif saved is not None:
         curr_save = False
         db.session.delete(saved)
         db.session.commit()
         return jsonify({'save':'save'})
        

@app.route('/video/delete/<videoid>')
def deletevid(videoid):
    saved = VideoSaved.query.filter_by(videoid = videoid).filter_by(savedname = current_user.username).first()
    db.session.delete(saved)
    db.session.commit()
    return redirect(url_for('explorevideo'))


@app.route('/video/comment/<videoid>', methods=['GET', 'POST']) #the argument for 
#this route comes from the above video/<videoid> route where {{url_for('videocomment', videoid = vid)}}

def videocomment(videoid):
    videoid = Video.query.filter_by(id = videoid).first()
    vid = videoid.id
    comment = request.get_json()
    comment_value = comment['value']
    comments = VideoComment(videoid = videoid.id, username = current_user.username, \
    comment = comment_value)
    db.session.add(comments)
    db.session.commit()

    insert_comment = VideoComment.query.filter_by(comment = comment_value).first()
    return jsonify({'result' : 'success', 'comment' : insert_comment.comment, 'user': insert_comment.username})

# Not explictly written, but id column (PK) of table Video and videoid column of table VideoComment 
# has a relationship and should have been joined together via a FK.

@app.route('/video/search', methods=['GET', 'POST'])
def videosearch():
    form = VideoSearch()
    if form.validate_on_submit():
        search = Video.query.filter(Video.title.ilike('%' + form.search.data + '%')).all() #ilike is case insensitive
        return render_template('vidsearch.html', search = search, form=form)
    else:
        return redirect(url_for('explorevideo'))

@app.route('/video/search/<option>', methods=['GET', 'POST'])
def videofilter(option):
    form = VideoSearch()
    search_json = request.get_json()
    searchy = search_json['value']
    search = Video.query.filter_by(category=option).filter(Video.title.ilike('%' + searchy + '%')).all()
    return jsonify({'search': render_template('filtersearch.html', search=search)}) 

@app.route('/video/addtoplaylist/<id>', methods=['GET', 'POST'])
def add_to_playlist(id):
    selected_vid = Video.query.filter_by(id=id).first()
    playid_json = request.get_json()
    play_id = playid_json['value']

    playlist_id = SavePlaylistVids.query.filter_by(playlist_id=play_id).all()
    order_array = []
    for play in playlist_id:
        order_array.append(int(play.id))
    new_order_no = len(order_array) + 1
   
    add_playlist = SavePlaylistVids(playlist_id=play_id, video_id=selected_vid.id, \
                                    title=selected_vid.title, desc = selected_vid.description, \
                                    order_no = new_order_no)
    db.session.add(add_playlist)
    db.session.commit()
    return jsonify({'result' : 'success'})

@app.route('/video/createplaylist', methods=['GET', 'POST'])
def create_playlist():
    data_json = request.get_json()
    video_id_value = data_json['value']
    form_data = data_json['form_data']
    videoid = Video.query.filter_by(id = video_id_value).first()
    vid = videoid.id
    playform = NewPlaylist()
    new_playlist = FitnessPlaylist(title = str(form_data['title']), desc = str(form_data['desc']), username = current_user.username)
    db.session.add(new_playlist)
    db.session.commit()
    all_playlist = FitnessPlaylist.query.filter_by(username=current_user.username).all()
    return jsonify({'playlist' : render_template('_playlistmodal.html', all_playlist=all_playlist, vid=vid, playform=playform)})
       
   
@app.route('/video/deletefromplaylist/<id>', methods=['GET', 'POST'])
def delete_from_playlist(id):
    selected_vid = Video.query.filter_by(id=id).first()
    playid_json = request.get_json()
    play_id = playid_json['value']
    delete_vid = SavePlaylistVids.query.filter_by(playlist_id=play_id)\
                .filter_by(video_id=id).first()

    db.session.delete(delete_vid)
    db.session.commit()
    return jsonify({'result' : 'success'})
   
#FITNESS LIBRARY

@app.route('/fitness')
def fitgen():
    return render_template('genfit.html')

@app.route('/fitness/<type>')
def fitresults(type):
    result = FitnessLib.query.filter_by(category = type).all()
    return render_template('libvid.html', result=result)

@app.route('/fitness/play/<title>')
def libload(title):
    lib_answer = FitnessLib.query.filter_by(title = title).first()
    lib_type = lib_answer.category
    result = FitnessLib.query.filter_by(category = lib_type).all()
    return render_template('libvidload.html', result=result, lib_answer=lib_answer)


#SAVED VIDEO PLAYLIST
@app.route('/dashboard/savedvideo')
def savedvideo():
    return render_template('savedvideo.html')

@app.route('/dashboard/savedvideo/view')
def viewsavedvideo():
    saved = VideoSaved.query.filter_by(savedname = current_user.username).all()
    return render_template('viewsavedvid.html', saved=saved)

@app.route('/dashboard/playlist/view', methods=['GET', 'POST'])
def viewplaylist():
    playlist = FitnessPlaylist.query.filter_by(username = current_user.username)
    form = NewPlaylist()
    if form.validate_on_submit():
        new_playlist = FitnessPlaylist(title = form.title.data, desc = form.desc.data, username = current_user.username)
        db.session.add(new_playlist)
        db.session.commit()
        flash('Playlist successfully created.')
        return redirect(url_for('viewplaylist'))

    return render_template('viewplaylist.html', form=form, playlist=playlist)

@app.route('/dashboard/playlist/delete/<id>')
def deleteplaylist(id):
    selected_playlist = FitnessPlaylist.query.filter_by(id=id).first()
    db.session.delete(selected_playlist)
    db.session.commit()
    db.session.query(SavePlaylistVids).filter_by(playlist_id = id).delete()
    db.session.commit()
    return redirect(url_for('viewplaylist'))

@app.route('/dashboard/playlist/viewvideo/<id>', methods=['GET', 'POST'])
def playlist_vid(id):
    playlist_vids = SavePlaylistVids.query.filter_by(playlist_id=id).order_by('order_no asc') #array of objects
    counter = 1
    number = 0

    for a in playlist_vids:  #manual recalibration of 'order_no' after deletion 
        playlist_vids[number].order_no = counter
        db.session.commit()
        counter += 1
        number += 1

    try:
        first_vid = playlist_vids[0]
        first_playlist_vid = Video.query.filter_by(id=first_vid.video_id).first()
        selected_playlist = FitnessPlaylist.query.filter_by(id=id).first()
        play_id = selected_playlist.id
        savedvids = VideoSaved.query.filter_by(savedname=current_user.username).all()
        
        return render_template('viewplaylistvid.html', savedvids=savedvids, playlist_vids=playlist_vids, play_id=play_id, \
                            first_playlist_vid = first_playlist_vid, first_vid = first_vid)
    
    except IndexError:
        selected_playlist = FitnessPlaylist.query.filter_by(id=id).first()
        play_id = selected_playlist.id
        savedvids = VideoSaved.query.filter_by(savedname=current_user.username).all()
        return render_template('viewemptyplaylist.html', savedvids=savedvids, playlist_vids=playlist_vids, play_id=play_id, \
    )


@app.route('/dashboard/playlist/viewvideo/add/<id>', methods=['GET', 'POST'])
def add_playlist_vid(id):
    playlist_json = request.get_json()
    checked_value = playlist_json['checkedvalue_array']
    selected_playlist = FitnessPlaylist.query.filter_by(id=id).first()
    play_id = selected_playlist.id
    sorted_vid = SavePlaylistVids.query.filter_by(playlist_id=play_id).order_by('order_no asc')
    counter = 1
    s = SavePlaylistVids.query.distinct(SavePlaylistVids.order_no).all() #if table is completely empty. i don't even know if i even need this
    if not s:
        savedvids = VideoSaved.query.filter_by(savedname=current_user.username).all()
        for v in checked_value:
                get_video = Video.query.filter_by(id = int(v)).first()
                save = SavePlaylistVids(playlist_id = play_id, video_id= int(v), title = get_video.title, \
                desc = get_video.description, order_no = counter, playlist_vid_id = counter)
                counter +=1
                db.session.add(save)
                db.session.commit()
                
        return jsonify({'playlist': render_template('_playlist.html', savedvids = savedvids, sorted_vid=sorted_vid) })
    
    else:
        savedvids = VideoSaved.query.filter_by(savedname=current_user.username).all()
        sorted_vid = SavePlaylistVids.query.filter_by(playlist_id=play_id).order_by('order_no asc')
        for v in checked_value:
                playlist_id = SavePlaylistVids.query.filter_by(playlist_id=id).all()
                order_array = []
                for play in playlist_id:
                    order_array.append(int(play.id))

                get_video = Video.query.filter_by(id = int(v)).first()
                new_order_no = len(order_array) + 1
                save = SavePlaylistVids(playlist_id = play_id, video_id= int(v), title = get_video.title, \
                desc = get_video.description, order_no = new_order_no, playlist_vid_id = new_order_no)
                db.session.add(save)
                db.session.commit()

        return jsonify({'playlist': render_template('_playlist.html', savedvids = savedvids, sorted_vid=sorted_vid) })


@app.route('/dashboard/playlist/viewvideo/addvid/<id>', methods=['GET', 'POST'])
def add_playlist_load(id):
    playlist_json = request.get_json()
    checked_value = playlist_json['checkedvalue_array']
    selected_playlist = FitnessPlaylist.query.filter_by(id=id).first()
    play_id = selected_playlist.id
    sorted_vid = SavePlaylistVids.query.filter_by(playlist_id=play_id).order_by('order_no asc')
    counter = 1
    s = SavePlaylistVids.query.distinct(SavePlaylistVids.order_no).all() #if table is completely empty. 
    if not s:
        savedvids = VideoSaved.query.filter_by(savedname=current_user.username).all()
        for v in checked_value:
                get_video = Video.query.filter_by(id = int(v)).first()
                save = SavePlaylistVids(playlist_id = play_id, video_id= int(v), title = get_video.title, \
                desc = get_video.description, order_no = counter, playlist_vid_id = counter)
                counter +=1
                db.session.add(save)
                db.session.commit()
                
        return jsonify({'playlist': render_template('_addplaylist.html', savedvids = savedvids, sorted_vid=sorted_vid) })
    
    else:
        savedvids = VideoSaved.query.filter_by(savedname=current_user.username).all()
        sorted_vid = SavePlaylistVids.query.filter_by(playlist_id=play_id).order_by('order_no asc')
        for v in checked_value:
                playlist_id = SavePlaylistVids.query.filter_by(playlist_id=id).all()
                order_array = []
                for play in playlist_id:
                    order_array.append(int(play.id))

                get_video = Video.query.filter_by(id = int(v)).first()
                new_order_no = len(order_array) + 1
                save = SavePlaylistVids(playlist_id = play_id, video_id= int(v), title = get_video.title, \
                desc = get_video.description, order_no = new_order_no, playlist_vid_id = new_order_no)
                db.session.add(save)
                db.session.commit()

        return jsonify({'playlist': render_template('_addplaylist.html', savedvids = savedvids, sorted_vid=sorted_vid) })

@app.route('/dashboard/playlist/viewvideo/deletevid/<id>', methods=['GET', 'POST']) 
def delete_playlist_load(id):
    selected_vid = SavePlaylistVids.query.filter_by(id=id).first()
    play_id = selected_vid.playlist_id
    db.session.delete(selected_vid)
    db.session.commit()
    sorted_vid = SavePlaylistVids.query.filter_by(playlist_id=play_id).order_by('order_no asc')
    savedvids = VideoSaved.query.filter_by(savedname=current_user.username).all()
    return jsonify({'playlist': render_template('_addplaylist.html', savedvids = savedvids, sorted_vid=sorted_vid) })


@app.route('/dashboard/playlist/viewvideo/delete/<id>', methods=['GET', 'POST']) 
def delete_playlist_vid(id):
    selected_vid = SavePlaylistVids.query.filter_by(id=id).first()
    play_id = selected_vid.playlist_id
    db.session.delete(selected_vid)
    db.session.commit()
    sorted_vid = SavePlaylistVids.query.filter_by(playlist_id=play_id).order_by('order_no asc')
    savedvids = VideoSaved.query.filter_by(savedname=current_user.username).all()
    return jsonify({'playlist': render_template('_playlist.html', savedvids = savedvids, sorted_vid=sorted_vid) })


@app.route('/dashboard/playlist/viewvideo/play/<id>', methods=['GET', 'POST'])
def load_playlist_vid(id):
    load_vid_id = SavePlaylistVids.query.filter_by(id = id).first()
    if load_vid_id is not None:
        load_vid = Video.query.filter_by(id=load_vid_id.video_id).first()
        
        get_playlist_vid_id = load_vid_id.playlist_id
        playlist_vids = SavePlaylistVids.query.filter_by(playlist_id=get_playlist_vid_id).order_by('order_no asc')

        check_user_state = PlaylistSession.query.filter_by(username=current_user.username).first()

        if check_user_state is None:
            save_user_state = PlaylistSession(playlist_id = get_playlist_vid_id, username = current_user.username,\
            playlist_vid_id = id)
            db.session.add(save_user_state)
            db.session.commit()
        
        elif check_user_state is not None:
            db.session.delete(check_user_state)
            db.session.commit()
            save_user_state = PlaylistSession(playlist_id = get_playlist_vid_id, username = current_user.username,\
            playlist_vid_id = id)
            db.session.add(save_user_state)
            db.session.commit()

        counter = 1
        number = 0

        for a in playlist_vids:  #manual recalibration of 'order_no' after deletion 
            playlist_vids[number].order_no = counter
            db.session.commit()
            counter += 1
            number += 1

        selected_playlist = FitnessPlaylist.query.filter_by(id=get_playlist_vid_id).first()

        play_id = selected_playlist.id
        savedvids = VideoSaved.query.filter_by(savedname=current_user.username).all()
            
        return render_template('loadplaylistvid.html', savedvids=savedvids, playlist_vids=playlist_vids, \
                                play_id=play_id, load_vid=load_vid, load_vid_id=load_vid_id)

    else:
        get_playlist_id = PlaylistSession.query.filter_by(username=current_user.username).first()
        playlist_id = get_playlist_id.playlist_id
        return redirect(url_for('playlist_vid', id = playlist_id))


@app.route('/updateorder', methods=['GET', 'POST'])
def update_order():
    answer = request.get_json()
    answer_value = answer['value'] #is array
    number = 0
    counter = 1
    for i in answer_value:
        selected_vid = SavePlaylistVids.query.filter_by(id=answer_value[number]).first()
        selected_vid.order_no = counter
        db.session.commit()
        number += 1
        counter += 1
    return 'success'

# @app.route('/fitness/<type>')
# def fitresults(type):
#     lucky_no = random.randint(1,4)
#     result = FitnessGen.query.filter_by(category=type).filter_by(genid=lucky_no).first()
#     return render_template('resultfit.html', result=result)

#######HASSAN (BLOG) #### 

@app.route('/blog')
def blog():
    blog_post = BlogPost.query.all()
    return render_template('hassan/blog.html', blog_post=blog_post)

@app.route('/blog/view/<id>')
def view_blog(id):
    blog = BlogPost.query.filter_by(id=id).first()
    return render_template('hassan/viewpost.html', blog=blog)

@app.route('/protected/blog/view')
def blog_view():
    all_post = BlogPost.query.all()
    return render_template('hassan/viewblog.html', all_post=all_post)

@app.route('/protected/blog/edit/<id>', methods=['POST', 'GET'])
def blog_edit(id):
    edit_post = BlogPost.query.filter_by(id=id).first()
    form = EditBlog(author = edit_post.author, description=edit_post.description, content=edit_post.content)
    if form.validate_on_submit():
        edit_post.author = form.author.data
        edit_post.description = form.description.data
        edit_post.content = form.content.data
        db.session.commit()
        return redirect(url_for('blog_view'))

    return render_template('hassan/editblog.html', form=form)


### XIONG JIE (RECIPE) ### 

@app.route('/recipe', methods=['GET', 'POST'])
def recipe():
    return render_template('xiongjie/mainrecipe.html')

@app.route('/recipe/view')
def view_recipe():
    return render_template('xiongjie/recipe_single.html')

@app.route('/recipe/manage')
def manage_recipe():
    all_recipe = RecipePost.query.all()
    return render_template('xiongjie/managerecipe.html', all_recipe=all_recipe)

@app.route('/recipe/edit/<id>')
def edit_recipe(id):
    # managerecipe.html
    pass

@app.route('/recipe/new', methods=['GET', 'POST'])
def new_recipe():
    if request.method == 'POST':
        recipe = RecipePost(title=request.form['title'], author=current_user.username,  difficulty=request.form['level'], \
        category=request.form['category'], description = request.form['desc'], \
        time=request.form['time'], ingredients = request.form['ingredients'],\
        instruction=request.form['instruction'], nutri=request.form['nutri'])
        db.session.add(recipe)
        db.session.commit()
        return 'success'

    return render_template('xiongjie/newrecipe.html')


#RAYMOND 

@app.route('/shop')
def shop():
    items = Item.query.all()
    cart = Cart.query.all()
    bmi = BMR.query.first()
    return render_template("raymond/shop.html", items=items, cart=cart, bmi=bmi)

@app.route('/addCart', methods=['GET', 'POST'])
def addCart():
    item_json = request.get_json()
    print(item_json)
    item_id = item_json['item_id']
    items = Item.query.filter_by(id=item_id).first()

    if current_user.is_authenticated == True:
        user = User.query.filter_by(username=current_user.username).first()
        uid = user.uid

        check = Cart.query.filter_by(user_id=uid).all()

        check_item = False

        for c in check:
            if c.item_id == items.id:
                c.quantity += 1
                db.session.commit()
                check_item = True
                break

        if check_item == False:
            new_item = Cart(user_id=uid, item_id=items.id, name=items.name, quantity=1, price=items.price,
                            subtotal=items.price)
            db.session.add(new_item)
            db.session.commit()
    else:
        check = Cart.query.filter_by(user_id=0).all()

        check_item = False

        for c in check:
            if c.user_id == 0 and c.item_id == items.id:
                c.quantity += 1
                db.session.commit()
                check_item = True
                break

        if check_item == False:
            new_item = Cart(user_id=0, item_id=items.id, name=items.name, quantity=1, price=items.price,
                            subtotal=items.price)
            db.session.add(new_item)
            db.session.commit()

    def cart_count():
        try:
            count = 0
            user = User.query.filter_by(username=current_user.username).first()
            uid = user.uid
            cart = Cart.query.filter(Cart.user_id==uid).all()
            for c in cart:
                count += 1
        except:
            count = 0
            cart = Cart.query.filter(Cart.user_id == 0).all()
            for c in cart:
                count += 1
        return count

    cart = Cart.query.all()
    count = cart_count()

    # return render_template('raymond/shop-cart.html', cart=cart, count=cart_count())
    # return jsonify({'count' : cart_count()})
    # return redirect(request.referrer)
    return jsonify({'cart': render_template('raymond/_shopcart.html', cart=cart), 'count': count})

@app.route('/filter', methods=['GET', 'POST'])
def filter():
    filter_json = request.get_json()
    filter = filter_json['filter']
    if filter is "":
        items = Item.query.all() #[item1, item2]
        return jsonify({'filter': render_template("raymond/shop-view.html", items=items, filter=filter)})
    elif filter == "recipes":
        items = Recipe.query.all()
        return jsonify({'filter': render_template("raymond/shop-recipe.html", items=items, filter=filter)})
    else:
        items = Item.query.filter_by(category=filter)
        return jsonify({'filter': render_template("raymond/shop-view.html", items=items, filter=filter)})


@app.route('/search', methods=['GET', 'POST'])
def search():
    filter_json = request.get_json()
    filter = filter_json['filter']
    if filter is "":
        items = Item.query.all()
        return jsonify({'filter': render_template("raymond/shop-view.html", items=items, filter=filter)})
    # else:
    #     items = Recipe.query.filter(func.lower(Recipe.name).contains(func.lower(filter))).all()
    #     return render_template("raymond/shop-recipe.html", items=items)
    else:
        items = Item.query.filter(func.lower(Item.name).contains(func.lower(filter))).all()
        return jsonify({'filter': render_template("raymond/shop-view.html", items=items, filter=filter)})

@app.route('/filterCalories', methods=['POST'])
def filterCalories():
    filter = request.form['filter']
    items = Recipe.query.filter(Recipe.calories <= filter).all()
    return render_template('raymond/shop-recipesort.html', items=items)

#BMR
@app.route('/bmrcalculate', methods=['GET', 'POST'])
def bmr_calculate():

    bmi_json = request.get_json()
   
    gender = bmi_json['gender']
    weight = bmi_json['weight']
    height = bmi_json['height']
    age = bmi_json['age']
    exercise = bmi_json['exercise']

    bmi_save = BMR(gender=gender, weight=weight, height=height, age=age, exercise=exercise)
    db.session.add(bmi_save)
    db.session.commit()

    bmi = BMR.query.first()
    bmi.gender = gender
    bmi.weight = weight
    bmi.height = height
    bmi.age = age
    bmi.exercise = exercise

    bmr = 0
    rec_cal = 0

    if gender == "0":
        bmr = (10 * float(weight)) + (6.25 * float(height)) - (5 * float(age)) + 5
    elif gender == "1":
        bmr = (10 * float(weight)) + (6.25 * float(height)) - (5 * float(age)) - 161

    if exercise == "1":
        rec_cal = bmr * 1.2
    elif exercise == "2":
        rec_cal = bmr * 1.375
    elif exercise == "3":
        rec_cal = bmr * 1.55
    elif exercise == "4":
        rec_cal = bmr * 1.725
    elif exercise == "5":
        rec_cal = bmr * 1.9

    bmi.bmr = bmr
    bmi.cal = rec_cal

    db.session.commit()

    bmi_query = BMR.query.first()
    bmr = int(bmi_query.bmr)
    cal = int(bmi_query.cal)
    return jsonify({ 'bmr' : bmr, 'cal' : cal })

#CART PAGE
@app.route('/cart')
def cart():
    try:
        user = User.query.filter_by(username=current_user.username).first()
        uid = user.uid
        cart = Cart.query.filter(Cart.user_id==uid).all()
    except:
        cart = Cart.query.filter(Cart.user_id==0).all()

    return render_template("raymond/cart.html", cart=cart)

@app.route('/cart/<int:item_id>/update', methods=['POST'])
def updateCart(item_id):
    itemsCart = Cart.query.filter_by(item_id=item_id).first()
    items = Item.query.filter_by(id=item_id).first()
    quantity = request.form['newquantity']
    if int(items.quantity) < int(quantity):
        items.quantity = items.quantity
    else:
        itemsCart.quantity = quantity
    itemsCart.subtotal = "{0:.2f}".format(float(itemsCart.quantity)*itemsCart.price)
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/cart/<int:item_id>/delete', methods=['GET','POST'])
def deleteCart(item_id):
    item_json = request.get_json()
    item_id = item_json['item_id']
    items = Cart.query.filter_by(item_id=item_id).first()
    db.session.delete(items)
    db.session.commit()

    cart = Cart.query.all()
    def cart_count():
        try:
            count = 0
            user = User.query.filter_by(username=current_user.username).first()
            uid = user.uid
            cart = Cart.query.filter(Cart.user_id==uid).all()
            for c in cart:
                count += 1
        except:
            count = 0
            cart = Cart.query.filter(Cart.user_id == 0).all()
            for c in cart:
                count += 1
        return count

    count = cart_count()
    return jsonify({'cart': render_template('raymond/_shopcart.html', cart=cart), 'count': count})

@app.route('/checkout')
def checkout():
    if current_user.is_authenticated == True:
        user = User.query.filter_by(username=current_user.username).first()
        uid = user.uid
        cart = Cart.query.filter(Cart.user_id==uid).all()
        date = datetime.datetime.now()
        uid_check = Orders.query.filter(Orders.user_id==uid).all()

        max_cart = db.session.query(db.func.max(Cart.id)).scalar()
        max_oid = db.session.query(db.func.max(Orders.oid)).scalar()

        if not uid_check:
            check = Orders.query.all()
            if not check:
                for c in cart:
                    checkout = Orders(oid=1, order_id=1, user_id=uid, item_id=c.item_id, name=c.name, quantity=c.quantity,
                                      items_quantity=max_cart, price=c.price,
                                      subtotal=c.subtotal, date=date, delivered="Order Received")
                    db.session.add(checkout)
                    db.session.delete(c)
                    item = Item.query.filter_by(id=c.item_id).first()
                    item.quantity -= c.quantity
                    db.session.commit()
            else:
                oid_count = max_oid + 1
                for c in cart:
                    checkout = Orders(oid=oid_count, order_id=1, user_id=uid, item_id=c.item_id, name=c.name, quantity=c.quantity,
                                      items_quantity=max_cart, price=c.price,
                                      subtotal=c.subtotal, date=date, delivered="Order Received")
                    db.session.add(checkout)
                    db.session.delete(c)
                    item = Item.query.filter_by(id=c.item_id).first()
                    item.quantity -= c.quantity
                    db.session.commit()
        else:
            oid_count = max_oid + 1

            user_id = Orders.query.filter(Orders.user_id==uid).all()
            order_id = user_id[-1].order_id
            orderid_count = order_id + 1

            for c in cart:
                checkout = Orders(oid=oid_count ,order_id=orderid_count, user_id=uid, item_id=c.item_id, name=c.name, quantity=c.quantity, items_quantity=max_cart, price=c.price,
                                  subtotal=c.subtotal, date=date, delivered="Order Received")
                db.session.add(checkout)
                db.session.delete(c)
                item = Item.query.filter_by(id=c.item_id).first()
                item.quantity -= c.quantity
                db.session.commit()

        return redirect(url_for('orders'))
    else:
        return redirect(url_for('login'))


#ITEM PAGE
@app.route('/item/<int:item_id>')
def item(item_id):
    item = Item.query.filter_by(id=item_id).one()

    comment = Comments.query.filter(Comments.item_id == item_id).all()

    return render_template('raymond/item.html', item=item, comment=comment)

#RECIPE PAGE
@app.route('/shop/recipe/<int:item_id>')
def shop_recipe(item_id):
    item = Recipe.query.filter_by(id=item_id).one()
    recipe_items = RecipeIngredients.query.filter_by(recipe_id=item_id).all()

    return render_template('raymond/recipe.html',item=item, recipe_items=recipe_items)

@app.route('/shop/recipe/add/<item_id>')
def addRecipetoCart(item_id):
    recipe_items = RecipeIngredients.query.filter_by(recipe_id=item_id).all()

    if current_user.is_authenticated == True:
        user = User.query.filter_by(username=current_user.username).first()
        uid = user.uid
        for i in recipe_items:
            item_id = i.item_id
            item = Item.query.filter_by(id=item_id).first()
            cart = Cart(user_id=uid,item_id=item.id,name=item.name,quantity=1,price=item.price,subtotal=item.price)
            db.session.add(cart)
            db.session.commit()
    else:
        for i in recipe_items:
            item_id = i.item_id
            item = Item.query.filter_by(id=item_id).first()
            cart = Cart(user_id=0, item_id=item.id, name=item.name, quantity=1, price=item.price, subtotal=item.price)
            db.session.add(cart)
            db.session.commit()

    return redirect(url_for('cart'))

@app.route('/item/<int:item_id>/add', methods=['POST'])
@login_required
def addComment(item_id):

    rating = request.form['rating']
    comment = request.form['comment']

    user = User.query.filter_by(username=current_user.username).first()
    uid = user.uid
    uname = user.username

    addComment = Comments(user_id=uid, item_id=item_id, name=uname, rating=rating, comment=comment)
    db.session.add(addComment)

    #shopping view
    item = Item.query.filter_by(id=item_id).first()
    count = Comments.query.filter_by(item_id=item_id).count()

    if item.totalratings is None:
        item.totalratings = 0 

    item.totalratings = int(item.totalratings)+int(rating)
    item.rating = int(item.totalratings / count)
    item.rating_count = count

    db.session.commit()

    return redirect(url_for('item', item_id=item_id))

#ADMIN
@app.route('/addItem', methods=['POST'])
def addItem():
    name = request.form['name']
    info = request.form['info']
    price = request.form['price']
    description = request.form['description']
    category = request.form['category']
    calories = request.form['calories']
    quantity = request.form['quantity']

    item = Item(name=name, info=info, price=price, description=description, category=category, calories=calories,
                quantity=quantity, totalratings=0)

    db.session.add(item)
    db.session.commit()

    img = request.files['image']
    img.filename = str(item.id) + ".jpg"
    filename = photos.save(img)

    items = Item.query.all()
    return render_template('raymond/shopadmin-table.html', items=items)

@app.route('/deleteItem', methods=['POST'])
def deleteItem():
    item_id = request.form['delete_id']
    del_item = Item.query.filter_by(id=item_id).first()
    db.session.delete(del_item)
    db.session.commit()

    img = str(item_id) + ".jpg"
    os.remove('static/raymond/img/' + img)

    items = Item.query.all()
    return render_template('raymond/shopadmin-table.html', items=items)

@app.route('/shopadmin')
def shopadmin():
    items = Item.query.all()
    recipes = Recipe.query.all()
    max_id = db.session.query(db.func.max(Recipe.id)).scalar()
    if max_id is None:
        max_id = 1
    else:
        max_id += 1
    recipe_items = RecipeIngredients.query.filter_by(recipe_id=max_id).all()
    return render_template("raymond/shopadmin.html", items=items, recipes=recipes, recipe_items=recipe_items)

@app.route('/updateItem', methods=['POST'])
def updateItem():
    itemid = request.form['itemid']
    items = Item.query.filter_by(id=itemid).first()
    return render_template("raymond/shopadmin-itemupdate.html", items=items)

@app.route('/updateItemButton', methods=['POST'])
def updateItemButton():

    item_id = request.form['item_id']
    name = request.form['name']
    info = request.form['info']
    price = request.form['price']
    description = request.form['description']
    category = request.form['category']
    calories = request.form['calories']
    quantity = request.form['quantity']

    item = Item.query.filter_by(id=item_id).first()
    item.name = name
    item.info = info
    item.price = price
    item. description = description
    item.category = category
    item.calories = calories
    item.quantity = quantity

    db.session.commit()

    items = Item.query.all()

    return render_template("raymond/shopadmin-table.html", items=items)

@app.route('/addRecipe', methods=['POST'])
def addRecipe():
    name = request.form['name']
    info = request.form['info']
    ingredients = request.form['ingredients']
    preperation = request.form['preperation']

    max_id = db.session.query(db.func.max(Recipe.id)).scalar()

    recipeItems = RecipeIngredients.query.filter_by(recipe_id = max_id+1).all()

    calories = 0
    price = 0
    for i in recipeItems:
        calories +=i.calories
        price += i.price

    recipe = Recipe(name=name, info=info, calories=calories, price=price, preperation=preperation, ingredients=ingredients)
    db.session.add(recipe)
    db.session.commit()

    img = request.files['image']
    img.filename = "r-" + str(recipe.id) + ".jpg"
    filename = photos.save(img)

    recipes = Recipe.query.all()

    return render_template('raymond/shopadmin-recipe.html', recipes=recipes)
    # return str(calories)


@app.route('/deleteRecipe', methods=['POST'])
def deleteRecipe():
    item_id = request.form['delete_id']

    del_recipe = Recipe.query.filter_by(id=item_id).first()
    db.session.delete(del_recipe)
    db.session.commit()

    del_recipeitem = RecipeIngredients.query.filter_by(recipe_id=item_id).all()
    for i in del_recipeitem:
        db.session.delete(i)
        db.session.commit()

    img = "r-" + str(item_id) + ".jpg"
    os.remove('static/raymond/img/' + img)

    recipes = Recipe.query.all()
    return render_template('raymond/shopadmin-recipe.html', recipes=recipes)


@app.route('/addRecipeItem', methods=['POST'])
def addRecipeItem():

    filter_id = request.form['filter_id']
    max_id = db.session.query(db.func.max(Recipe.id)).scalar()
    if max_id is None:
        max_id = 1
    else:
        max_id += 1

    item = Item.query.filter(Item.id==filter_id).first()
    name = item.name
    price = item.price
    info = item.info
    quantity = item.quantity
    calories = item.calories


    ingredient = RecipeIngredients(recipe_id=max_id, item_id=filter_id, name=name, price=price, info=info, quantity=quantity, calories=calories, change=True)
    db.session.add(ingredient)
    db.session.commit()

    recipe_items = RecipeIngredients.query.filter_by(recipe_id=max_id).all()

    return render_template('raymond/shopadmin-recipetable.html', recipe_items=recipe_items)

@app.route('/deleteRecipeItem', methods=['POST'])
def deleteRecipeItem():
    item_id = request.form['delete_id']

    del_recipe = RecipeIngredients.query.filter_by(id=item_id).first()
    db.session.delete(del_recipe)
    db.session.commit()

    max_id = db.session.query(db.func.max(Recipe.id)).scalar()
    if max_id is None:
        max_id = 1
    else:
        max_id += 1

    recipe_items = RecipeIngredients.query.filter_by(recipe_id=max_id).all()

    return render_template('raymond/shopadmin-recipetable.html', recipe_items=recipe_items)

@app.route('/addRecipeSearch', methods=['POST'])
def addRecipeSearch():
    filter = request.form['filter']
    items = Item.query.filter(func.lower(Item.name).contains(func.lower(filter))).all()

    return render_template('raymond/shopadmin-search.html', items=items)

#ORDERS PAGE
@app.route('/ordersadmin')
def ordersadmin():

    #check if user id is same, then check if oid is same

    #get max oid
    max_oid = db.session.query(db.func.max(Orders.oid)).scalar()

    list = [] #[[4,1],[4,2]]
    group = [] #[[<obj 1>,<obj 1>,<obj 1>,<obj 1>],[<obj 1>,<obj 1>,<obj 1>,<obj 1>]]

    for i in range(max_oid+1):
        o = Orders.query.filter(Orders.oid == i).first()
        if o:
            o_userid = o.user_id
            o_oid = o.oid
            list.append([o_userid,o_oid])

    for i in list:
        q_userid = Orders.query.filter(and_(Orders.user_id==i[0], Orders.oid==i[1])).all()
        group.append(q_userid)

    return render_template("raymond/ordersadmin.html", group=group, list=list)

@app.route('/searchOrdersID', methods=['POST'])
def searchOrdersID():

    filter = request.form['filter']

    if filter == '':
        max_oid = db.session.query(db.func.max(Orders.oid)).scalar()

        list = []  # [[4,1],[4,2]]
        group = []  # [[<obj 1>,<obj 1>,<obj 1>,<obj 1>],[<obj 1>,<obj 1>,<obj 1>,<obj 1>]]

        for i in range(max_oid + 1):
            o = Orders.query.filter(Orders.oid == i).first()
            if o:
                o_userid = o.user_id
                o_oid = o.oid
                list.append([o_userid, o_oid])

        for i in list:
            q_userid = Orders.query.filter(and_(Orders.user_id == i[0], Orders.oid == i[1])).all()
            group.append(q_userid)
    else:
        list = []  # [[4,1],[4,2]]
        group = []  # [[<obj 1>,<obj 1>,<obj 1>,<obj 1>],[<obj 1>,<obj 1>,<obj 1>,<obj 1>]]

        o = Orders.query.filter(Orders.oid == filter).first()
        if o:
            o_userid = o.user_id
            o_oid = o.oid
            list.append([o_userid, o_oid])

        for i in list:
            q_userid = Orders.query.filter(and_(Orders.user_id == i[0], Orders.oid == i[1])).all()
            group.append(q_userid)

    return render_template("raymond/ordersadmin-search.html", group=group, list=list)

@app.route('/deliver/<group_id>/<status>')
def deliver(group_id, status):
    query_gid = Orders.query.filter(Orders.oid==group_id).all()
    for i in query_gid:
        i.delivered = status
        db.session.commit()

    return redirect(url_for('ordersadmin'))

@app.route('/orders')
@login_required
def orders():
    # check if user id is same, then check if oid is same

    #order received, delivery scheduled, delivery started, delivery in progress, delivery completed

    # get max oid
    max_oid = db.session.query(db.func.max(Orders.oid)).scalar()

    user = User.query.filter_by(username=current_user.username).first()
    uid = user.uid

    list = []  # [[4,1],[4,2]]
    group = []  # [[<obj 1>,<obj 1>,<obj 1>,<obj 1>],[<obj 1>,<obj 1>,<obj 1>,<obj 1>]]

    for i in range(max_oid + 1):
        o = Orders.query.filter(Orders.oid == i).first()
        if o and o.user_id == uid:
            o_userid = o.user_id
            o_oid = o.oid
            list.append([o_userid, o_oid])

    for i in list:
        q_userid = Orders.query.filter(and_(Orders.user_id == i[0], Orders.oid == i[1])).all()
        group.append(q_userid)

    percent = 0
    status = 'true'
    oid = 0
    for i in range(max_oid + 1):
        o = Orders.query.filter(Orders.oid == i).first()
        if o and o.user_id == uid:
            oid = o.oid
    check = Orders.query.filter(and_(Orders.user_id == uid, Orders.oid == oid)).first()
    if check.delivered == 'Order Received':
        status = 'true'
        percent = 10
    elif check.delivered == 'Delivery Scheduled':
        status = 'true'
        percent = 40
    elif check.delivered == 'Delivery In Progress':
        status = 'true'
        percent = 70
    elif check.delivered == 'Delivery Completed':
        status = 'true'
        percent = 100

    return render_template("raymond/orders.html", group=group, list=list, percent=percent, status=status, uid=uid, order_id=oid)
    # return str(oid)

@app.route('/orderstatus', methods=['POST'])
@login_required
def orderstatus():

    user = User.query.filter_by(username=current_user.username).first()
    uid = user.uid

    percent = 0
    status = 'true'

    order_id = request.form['order_id']
    q_userid = Orders.query.filter(and_(Orders.user_id == uid, Orders.oid == order_id)).first()
    if q_userid.delivered == 'Order Received':
        status = 1
        percent = 10
    elif q_userid.delivered == 'Delivery Scheduled':
        status = 2
        percent = 40
    elif q_userid.delivered == 'Delivery In Progress':
        status = 3
        percent = 70
    elif q_userid.delivered == 'Delivery Completed':
        status = 4
        percent = 100

    return render_template("raymond/orders-status.html", percent=percent, status=status, uid=uid, order_id=order_id)

@app.route('/checkoutform')
def checkoutform():
    cart = Cart.query.all()
    return render_template('raymond/checkoutform.html', cart=cart)


#CYNTHIA

@app.route('/gym')
def gym_page():
    return render_template('cynthia/index.html')

@app.route('/gym/find', methods=["POST"])
def find_gyms():
    if request.method == 'POST':
        location = request.form["location"]
        geo_coding_url = 'https://maps.googleapis.com/maps/api/geocode/json?address='+ location + '&key=' + API_KEY
        geo_coding_response = requests.get(geo_coding_url).json()
        location_coordinates = geo_coding_response["results"][0]["geometry"]["location"]
        lng = str(location_coordinates["lng"])
        lat = str(location_coordinates["lat"])
        places_search_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=' + lat + ',' + lng + '&rankby=distance&type=gym&keyword=gym&key=AIzaSyC-untCAlzyRtrAuJ6ShicN0aHCHMD94jg'
        places_response = requests.get(places_search_url).json()
        pp = pprint.PrettyPrinter(width=50,depth=3)
        pp.pprint(places_response)
        return render_template('cynthia/gyms.html', gyms=places_response)

@app.route('/gym/more/<place_id>', methods=["GET", "POST"])
def gym_info(place_id):
    if request.method == 'GET':
        place_api_url = 'https://maps.googleapis.com/maps/api/place/details/json?placeid=' + place_id + '&key=AIzaSyDHHLWzJzlZZFDye9JbxiCu4RXei_bzMbE'
        place_details_response = requests.get(place_api_url).json()
        return render_template('cynthia/gym.html', gym=place_details_response)
    if request.method == 'POST':
        new_booking_id = None
        try:
            bookings = firedb.child("bookings").get().val()
            booking_id = [entry for entry in bookings][-1]['id']
            new_booking_id = int(booking_id) + 1
        except:
            new_booking_id = 0
        
        new_booking_ref = firedb.child("bookings").child(new_booking_id)
        booking_id_string = hashids.encode(new_booking_id)
        booking_confirm_url = 'session/confirm/' + booking_id_string
        booking_details = dict()
        booking_details['id'] = int(new_booking_id)
        booking_details['gym'] = request.form["gym"]
        booking_details['address'] = request.form["address"]
        booking_details['name'] = request.form["name"]
        booking_details['phone_number'] = request.form["phone"]
        booking_details['email'] = request.form['email']
        booking_details['date_time'] = request.form['date_time']
        booking_details['id_string'] = booking_id_string
        new_booking_ref.set(booking_details)
        user_message = message_builder.user_message(booking_details)
        gym_message = message_builder.gym_message(booking_details)

        # Send a mail to user to show them a confirmation of their booking.
        sendmail(mail, user_message['subject'], 'findgym2@gmail.com', [booking_details['email']], user_message['html'])
        
        # Send a message to the gym to let them know the user has scheduled a session
        sendmail(mail, gym_message['subject'], 'findgym2@gmail.com', [gyms_email_address], gym_message['html'])
        
        return redirect(booking_confirm_url)

@app.route('/session/confirm/<booking_id>')       
def display_confirmation(booking_id):
    real_booking_id = hashids.decode(booking_id)[0]
    booking_ref = firedb.child('bookings').child(real_booking_id)
    result = booking_ref.get().val()
    booking_details = dict(result)
    return render_template('cynthia/confirm.html', booking_details=booking_details)


# email cancel(user & gym)
@app.route('/session/user_cancel/<booking_id>')
def user_delete_and_confirm(booking_id):
    real_booking_id = hashids.decode(booking_id)[0]
    booking_ref = firedb.child("bookings").child(real_booking_id)
    booking_details = booking_ref.get().val()
    booking_ref.remove()
    user_cancel_message = message_builder.user_cancel_message(booking_details)
    user_cancel_confirm_message = message_builder.user_cancel_confirm(booking_details)
    sendmail(mail, user_cancel_message['subject'], 'findgym2@gmail.com', [gyms_email_address], user_cancel_message['html'])
    sendmail(mail, user_cancel_confirm_message['subject'], 'findgym2@gmail.com', [booking_details['email']], user_cancel_confirm_message['html'])
    return render_template('cynthia/confirm_delete.html', booking_details=booking_details)

@app.route('/session/gym_cancel/<booking_id>')
def gym_delete_and_confirm(booking_id):
    real_booking_id = hashids.decode(booking_id)[0]
    booking_ref = firedb.child("bookings").child(real_booking_id)
    booking_details = booking_ref.get().val()
    booking_ref.remove()
    gym_cancel_message = message_builder.gym_cancel_message(booking_details)
    gym_cancel_confirm_message = message_builder.gym_cancel_confirm(booking_details)
    sendmail(mail, gym_cancel_message['subject'], 'findgym2@gmail.com', [booking_details['email']], gym_cancel_message['html'])
    sendmail(mail, gym_cancel_confirm_message['subject'], 'findgym2@gmail.com', [gyms_email_address], gym_cancel_confirm_message['html'])
    return render_template('cynthia/confirm_delete.html', booking_details = booking_details)


# The gym equipment page
@app.route('/gym/tools', methods=["GET"])
def list_tools():
    all_tools = requests.get('https://api.myjson.com/bins/r4kxh').json()
    page_one = [tool for tool in all_tools if(tool['id'] <= 16)]
    next_page = 2
    return render_template('cynthia/equipment.html', tools = page_one, next_page = next_page)

@app.route('/gym/tools/<page_id>', methods=["GET"])
def list_tool_next_page(page_id):
    all_tools = requests.get('https://api.myjson.com/bins/r4kxh').json()
    page_two = [tool for tool in all_tools if(tool['id'] >= 17)]
    return render_template('cynthia/equipment.html', tools = page_two)


### (DO NOT TOUCH)

if __name__ == '__main__':
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.anonymous_user = Anonymous


    @login_manager.user_loader
    def load_user(uid):
        return User.query.get(int(uid))

    app.run(debug=True, threaded=True)
