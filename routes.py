#on the command line, please change directory with 'cd' to wherever this app is
#then enter 'python routes.py' on the command line to activate website

import os
from flask import Flask, render_template, url_for, request, session, redirect, send_from_directory, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import select, func, or_, and_, between
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message
import datetime

from hashids import Hashids
import requests

from models import *

from flask_login import LoginManager, login_user, login_required, logout_user, current_user, user_unauthorized
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin

from flask_uploads import UploadSet, configure_uploads, IMAGES

# import pyrebase

app = Flask(__name__)
admin = Admin(app, name = 'LifeStyle28', template_mode = 'bootstrap3')

#EMAIL SETTINGS
app.config.update(
	DEBUG=True,
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = 'threesugar123@gmail.com',
	MAIL_PASSWORD = 'lifestyle28',
    MAIL_DEFAULT_SENDER = 'threesugar123@gmail.com'
	)

mail = Mail(app)


Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/database.db'
# 'postgresql://postgres:class@localhost/flaskvids'


app.secret_key = "development-key"
db.init_app(app)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(APP_ROOT, 'static')

photos = UploadSet('photos', IMAGES)

photodest = os.path.join(APP_ROOT, 'static/raymond/img')

app.config['UPLOADED_PHOTOS_DEST'] = photodest
configure_uploads(app, photos)


#
# #FIREBASE/CYNTHIA
#
# API_KEY = 'AIzaSyC-untCAlzyRtrAuJ6ShicN0aHCHMD94jg'
#
# hashid_salt = 'impossible to guess'
# hashids = Hashids(salt=hashid_salt, min_length=4)
#
# config = {
#     "apiKey": "AIzaSyCiUhFnF68ufmbjxHWnPoMaaxGEKlfJPNc",
#     "authDomain": "gym-finder-9e3b6.firebaseapp.com",
#     "databaseURL": "https://gym-finder-9e3b6.firebaseio.com",
#     "storageBucket": "gym-finder-9e3b6.appspot.com"
#   }
#
#   #this is to register as an admin with full read/write access
#
# firebase = pyrebase.initialize_app(config)
# firedb = firebase.database()
#


# #FIREFORM TEST
# @app.route('/firebase', methods=['GET', 'POST'])
# def firebase():
#     form = FireForm()
#     userlist = []
#     if form.validate_on_submit():
#         info = {"place": form.place.data, "email": form.email.data}
#         firedb.child("booking").child("user").push(info, user['idToken'] )
#         userz = firedb.child("booking").child("user").get(user['idToken'])
#         test = firedb.child("booking").child("user").order_by_child("email").equal_to("clever@clever.com").get(user['idToken'])
#         print(test.val())
#         for u in userz.each():
#             userlist.append(u.val())

#         return render_template('fireform.html', form=form, userlist=userlist)
        
#     else:
#          return render_template('fireform.html', form=form, userlist=userlist)

#     return render_template('fireform.html', form=form, userlist=userlist)

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
            cart = Cart.query.filter(Cart.user_id == None).all()
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
                show_cart_price=show_cart_price, cart_count=cart_count, cal_bmr=cal_bmr, cal_cal=cal_cal)


#ADMIN OVERALL

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(BlogPost, db.session))
path = os.path.join(os.path.dirname(__file__), 'static/assets')
# admin.add_view(FileAdmin(path, name='Videos'))
admin.add_view(ItemView(Item, db.session))
admin.add_view(ModelView(Recipe, db.session))
admin.add_view(ModelView(Cart, db.session))
admin.add_view(ModelView(Orders, db.session))
admin.add_view(ModelView(Comments, db.session))
admin.add_view(ModelView(BMR, db.session))


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
        return render_template('index.html', success=True, show = True)

    return render_template('index.html')

###

#LOGIN/REGISTER/SIGNUP (DO NOT TOUCH)
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!')
            return render_template('login.html', form=form)

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
            return render_template('signup.html', form = form)

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
    inbox = UserMail.query.filter_by(target=current_user.username).order_by("date desc").all()
    return render_template('inbox.html', inbox=inbox)

@app.route('/inbox/mark/<id>')
def mark_read(id):
        inbox = UserMail.query.filter_by(target=current_user.username).all()
        inboxes = UserMail.query.filter_by(id=id).first()
        marker = inboxes.seen

        if marker == True:
            inboxes.seen = False
            db.session.commit()
            return redirect(url_for('inbox'))

        elif marker == False:
            inboxes.seen = True
            db.session.commit()
            return redirect(url_for('inbox'))

        return redirect(url_for('inbox'))

@app.route('/inbox/flag/<id>')
def mark_flag(id):
        inbox = UserMail.query.filter_by(target=current_user.username).all()
        inboxes = UserMail.query.filter_by(id=id).first()
        marker = inboxes.flag

        if marker == True:
            inboxes.flag = False
            db.session.commit()
            return render_template('inbox.html', inbox=inbox, marker=marker)

        elif marker == False:
            inboxes.flag = True
            db.session.commit()
            return render_template('inbox.html', inbox=inbox, marker=marker)

        return render_template('inbox.html', inbox=inbox, marker=marker)


@app.route('/inbox/flag/view')
def viewflagged():
    flagged = UserMail.query.filter_by(flag=True).filter_by(target=current_user.username)\
    .order_by("date desc").all()

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
        return redirect(url_for('inbox'))

    return render_template('replyflagged.html', view_msg=view_msg, form=form)


@app.route('/inbox/send', methods=['GET', 'POST'])
def send():
    form = SendMessage()
    if form.validate_on_submit():
        new_msg = UserMail(sender=current_user.username, target=form.to.data, subject=form.subject.data,
        message=form.message.data, seen=False, flag=False)
        db.session.add(new_msg)
        db.session.commit()
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
        return redirect(url_for('inbox'))

    return render_template('message.html', view_msg=view_msg, form=form)

@app.route('/inbox/sent')
def sentinbox():
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
        return redirect(url_for('inbox'))

    return render_template('sendmessage.html', view_msg=view_msg, form=form)

@app.route('/inbox/delete/<id>')
def deleteinbox(id):
    view_msg = UserMail.query.filter_by(id=id).first()
    db.session.delete(view_msg)
    db.session.commit()
    return redirect(url_for('inbox'))


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
        #flash('Video successfully edited!')
        return redirect(url_for('vidmanage')) #render template will cause a 'function not iterable error'

    return render_template('videdit.html', form = form)


@app.route('/dashboard/video/manage/delete/<int:id>')
@login_required
def viddelete(id):
    video = Video.query.get_or_404(id)
    db.session.delete(video)
    db.session.commit()
    delete = True
    #flash('You have successfully deleted the video.')
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


####


#VIDEO

@app.route('/video')
def video():
    return render_template('videos.html')

@app.route('/video/beginners')
def beginnervideo():
    return render_template('beginnervid.html')

@app.route('/video/advanced')
def advancedvideo():
    return render_template('advancedvid.html')

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

    #CUSTOM LOGIN TO REDIRECT BACK TO VIDEO

    vidform = LoginForm()
    if vidform.validate_on_submit():
        user = User.query.filter_by(email=vidform.email.data).first()
        if user is not None and user.check_password(vidform.password.data):
                login_user(user)
                return redirect(url_for('videoz', videoid = vid))
        else:
            error = True
            #flash('Invalid username or password!')


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

    return render_template('displayvid1.html', link=link, name=name, cat=cat, desc=desc, \
                            date=date, title=title, vid = vid, comms = comms, form=form, related=related, \
                            tlikes = tlikes, tdislike = tdislike, \
                            curr_save = curr_save, vidform=vidform, error=error, tviews=tviews)



@app.route('/video/likes/<videoid>')
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

    return redirect(url_for('videoz', videoid = vid))


@app.route('/video/dislikes/<videoid>')
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

    return redirect(url_for('videoz', videoid = vid))

@app.route('/video/save/<videoid>')
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
         return redirect(url_for('videoz', videoid = vid))

    elif saved is not None:
         curr_save = False
         db.session.delete(saved)
         db.session.commit()
         return redirect(url_for('videoz', videoid = vid))

    return redirect(url_for('videoz', videoid = vid))

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
    comments = VideoComment(videoid = videoid.id, username = current_user.username, \
    comment = request.form['text'])
    db.session.add(comments)
    db.session.commit()
    return redirect(url_for('videoz', videoid = vid))

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


####### HASSAN (BLOG) ####

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

#ADD ADMIN SALE QUANTITY (SOLD OUT)
#ADD USER TIME TO DELIVER
#ADD PAYPAL CHECKOUT
#ADD RECIPE EDIT INGREDIENT

#SHOP PAGE
@app.route('/shop')
def shop():
    items = Item.query.all()
    cart = Cart.query.all()
    return render_template("raymond/shop.html", items=items, cart=cart)

@app.route('/addCart', methods=['POST'])
def addCart():
    item_id = request.form['item_id']

    user = User.query.filter_by(username=current_user.username).first()
    uid = user.uid
    items = Item.query.filter_by(id=item_id).first()
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




    # except AttributeError:
    #     items = Item.query.filter_by(id=item_id).first()
    #     new_item = Cart(item_id=items.id, name=items.name, quantity=1, price=items.price, subtotal=items.price)
    #     db.session.add(new_item)
    #     db.session.commit()

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
            cart = Cart.query.filter(Cart.user_id == None).all()
            for c in cart:
                count += 1
        return count

    return jsonify({'count' : cart_count()})
    # return redirect(request.referrer)

@app.route('/filter', methods=['POST'])
def filter():
    filter = request.form['filter']
    if filter is "":
        items = Item.query.all() #[item1, item2]
    else:
        items = Item.query.filter(Item.category == filter).all()
    return render_template("raymond/shop-view.html", items=items, filter=filter)

@app.route('/search', methods=['POST'])
def search():
    filter = request.form['filter']
    if filter is "":
        items = Item.query.all()
    else:
        items = Item.query.filter(func.lower(Item.name).contains(func.lower(filter))).all()
    return render_template("raymond/shop-view.html", items=items)

#BMR
@app.route('/bmr/calculate', methods=['POST'])
def bmr_calculate():

    gender = request.form['gender']
    weight = request.form['weight']
    height = request.form['height']
    age = request.form['age']
    exercise = request.form['exercise']

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
    return redirect(url_for('shop'))

@app.route('/bmr/reset', methods=['POST'])
def bmr_reset():
    bmi = BMR.query.first()
    bmi.gender = 0
    bmi.weight = 0
    bmi.height = 0
    bmi.age = 0
    bmi.exercise = 0
    bmi.bmi = 0
    bmi.cal = 0

    db.session.commit()
    return redirect(url_for('shop'))

#CART PAGE
@app.route('/cart')
def cart():
    try:
        user = User.query.filter_by(username=current_user.username).first()
        uid = user.uid
        cart = Cart.query.filter(Cart.user_id==uid).all()
    except:
        cart = Cart.query.filter(Cart.user_id==None).all()

    # cart = Cart.query.all()

    return render_template("raymond/cart.html", cart=cart)

@app.route('/cart/<int:item_id>/update', methods=['POST'])
def updateCart(item_id):
    items = Cart.query.filter_by(item_id=item_id).first()
    quantity = request.form['newquantity']
    items.quantity = quantity
    items.subtotal = "{0:.2f}".format(float(items.quantity)*items.price)
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/cart/<int:item_id>/delete')
def deleteCart(item_id):
    items = Cart.query.filter_by(item_id=item_id).first()
    db.session.delete(items)
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    user = User.query.filter_by(username=current_user.username).first()
    uid = user.uid
    cart = Cart.query.filter(Cart.user_id==uid).all()
    date = datetime.datetime.now()
    check = Orders.query.all()

    if not check:
        cart_count = 0
        for c in cart:
            cart_count += 1

        for c in cart:
            checkout = Orders(order_id=1, user_id=uid, item_id=c.item_id, name=c.name, quantity=c.quantity,
                              items_quantity=cart_count, price=c.price,
                              subtotal=c.subtotal, date=date, delivered="Not Delivered")
            db.session.add(checkout)
            db.session.delete(c)
            db.session.commit()
    else:
        # total items in orders
        count = 0
        orders = Orders.query.all()
        for o in orders:
            count += 1

        order_count = count + 1

        # total items in cart
        cart_count = 0
        for c in cart:
            cart_count += 1

        # get last entry in orders
        row = Orders.query.filter(Orders.id == count).first()
        qty = row.order_id
        qty += 1

        for c in cart:
            checkout = Orders(order_id=qty, user_id=uid, item_id=c.item_id, name=c.name, quantity=c.quantity, items_quantity=cart_count, price=c.price,
                              subtotal=c.subtotal, date=date, delivered="Not Delivered")
            db.session.add(checkout)
            db.session.delete(c)
            db.session.commit()

    return redirect(url_for('shop'))

#ITEM PAGE
@app.route('/item/<int:item_id>')
def item(item_id):
    item = Item.query.filter_by(id=item_id).one()

    comment = Comments.query.filter(Comments.item_id == item_id).all()

    return render_template('raymond/item.html', item=item, comment=comment)

#RECIPE PAGE
@app.route('/shop_recipe')
def shop_recipe():

    return render_template('raymond/recipe.html')

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
    # return render_template("raymond/shopadmin.html", items=items)
    return render_template('raymond/shopadmin-table.html', items=items)

@app.route('/deleteItem', methods=['POST'])
def deleteItem():
    item_id = request.form['delete_id']
    del_item = Item.query.filter_by(id=item_id).first()
    db.session.delete(del_item)
    db.session.commit()
    items = Item.query.all()
    return render_template('raymond/shopadmin-table.html', items=items)

@app.route('/shopadmin')
def shopadmin():
    items = Item.query.all()
    return render_template("raymond/shopadmin.html", items=items)

@app.route('/ordersadmin')
def ordersadmin():

    #check if user id is same, then check if order id is same

    #get max userid
    max_userid = db.session.query(db.func.max(Orders.user_id)).scalar()
    max_orderid = db.session.query(db.func.max(Orders.order_id)).scalar()
    max_id = db.session.query(db.func.max(Orders.id)).scalar()

    list = [] #[[4,1],[4,2]]
    group = [] #[[<obj 1>,<obj 1>,<obj 1>,<obj 1>],[<obj 1>,<obj 1>,<obj 1>,<obj 1>]]

    for i in range(max_orderid+1):
        o = Orders.query.filter(Orders.order_id == i).first()
        if o:
            o_userid = o.user_id
            o_orderid = o.order_id
            list.append([o_userid,o_orderid])

    for i in list:
        q_userid = Orders.query.filter(and_(Orders.user_id==i[0], Orders.order_id==i[1])).all()
        group.append(q_userid)

    #check if userid not in orders
    #if not, new orderid = 1
    #else retrieve latest userid latest entry
    #select row with orderid
    #orderid+=1

    #TESTT


    # return str(group)

    # pass
    return render_template("raymond/ordersadmin.html", group=group, list=list)

@app.route('/deliver/<group_id>')
def deliver(group_id):
    max_orderid = db.session.query(db.func.max(Orders.order_id)).scalar()

    # oid = group_id.order_id
    query_gid = Orders.query.filter(Orders.order_id==group_id).all()
    for i in query_gid:
        i.delivered = 'Ongoing Delivery'
        db.session.commit()


    return render_template("raymond/ordersadmin.html")
    # return str(group_id)

#
# #CYNTHIA
#
# @app.route('/gym')
# def gym_page():
#     return render_template('cynthia/index.html')
#
# @app.route('/gym/find', methods=["POST"])
# def find_gyms():
#     if request.method == 'POST':
#         location = request.form["location"]
#         geo_coding_url = 'https://maps.googleapis.com/maps/api/geocode/json?address='+ location + '&key=' + API_KEY
#         geo_coding_response = requests.get(geo_coding_url).json()
#         location_coordinates = geo_coding_response["results"][0]["geometry"]["location"]
#         lng = str(location_coordinates["lng"])
#         lat = str(location_coordinates["lat"])
#         places_search_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=' + lat + ',' + lng + '&rankby=distance&type=gym&keyword=gym&key=AIzaSyC-untCAlzyRtrAuJ6ShicN0aHCHMD94jg'
#         places_response = requests.get(places_search_url).json()
#         return render_template('cynthia/gyms.html', gyms=places_response)
#
# @app.route('/gym/more/<place_id>', methods=["GET", "POST"])
# def gym_info(place_id):
#     if request.method == 'GET':
#         place_api_url = 'https://maps.googleapis.com/maps/api/place/details/json?placeid=' + place_id + '&key=AIzaSyDHHLWzJzlZZFDye9JbxiCu4RXei_bzMbE'
#         place_details_response = requests.get(place_api_url).json()
#         return render_template('cynthia/gym.html', gym=place_details_response)
#     if request.method == 'POST':
#         new_booking_id = None
#         try:
#             bookings = firedb.child("bookings").get().val()
#             booking_id = [entry for entry in bookings][-1]['id']
#             new_booking_id = int(booking_id) + 1
#         except:
#             new_booking_id = 0
#
#         new_booking_ref = firedb.child("bookings").child(new_booking_id)
#         booking_id_string = hashids.encode(new_booking_id)
#         booking_confirm_url = 'session/confirm/' + booking_id_string
#         booking_details = dict()
#         booking_details['id'] = int(new_booking_id)
#         booking_details['name'] = request.form["name"]
#         booking_details['phone_number'] = request.form["phone"]
#         booking_details['email'] = request.form['email']
#         booking_details['date_time'] = request.form['date_time']
#         booking_details['id_string'] = booking_id_string
#         new_booking_ref.set(booking_details)
#         return redirect(booking_confirm_url)
#
#
# @app.route('/session/confirm/<booking_id>')
# def display_confirmation(booking_id):
#     real_booking_id = hashids.decode(booking_id)[0]
#     booking_ref = firedb.child('bookings').child(real_booking_id)
#     result = booking_ref.get().val()
#     booking_details = dict(result)
#     return render_template('cynthia/confirm.html', booking_details=booking_details)
#

### (DO NOT TOUCH)

if __name__ == '__main__':
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.anonymous_user = Anonymous
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(uid):
        return User.query.get(int(uid))

    app.run(debug=True)
    # app.run(port='80')
