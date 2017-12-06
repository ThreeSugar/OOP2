#on the command line, please change directory with 'cd' to wherever this app is
#then enter 'python routes.py' on the command line to activate website

import os
from flask import Flask, render_template, url_for, request, session, redirect, send_from_directory, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import select
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message

from models import LoginForm, RegisterForm, User, db, Video, SelectForm, EditForm, \
VideoComment, VideoSearch, VideoLikes, VideoDislikes, VideoSaved, VideoViews, \
Anonymous, FireForm

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin

import pyrebase


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



#FIREBASE

config = {
    "apiKey": "AIzaSyDasXfTEmJNbK5446JZlumx1bmZ4rmxeQE",
    "authDomain": "lifestyle28-14407.firebaseapp.com",
    "databaseURL": "https://lifestyle28-14407.firebaseio.com",
    "projectId": "lifestyle28-14407",
    "storageBucket": "gs://lifestyle28-14407.appspot.com",
    "messagingSenderId": "260841418499"
  }

  #this is to register as an admin with full read/write access

firebase = pyrebase.initialize_app(config)
firedb = firebase.database()  

#FIREBASE AUTH

auth = firebase.auth()
user = auth.sign_in_with_email_and_password("john@john.com", "password")


#FIREFORM TEST
@app.route('/firebase', methods=['GET', 'POST'])
def firebase():
    form = FireForm()
    userlist = []
    if form.validate_on_submit():
        info = {"place": form.place.data, "email": form.email.data}
        firedb.child("booking").child("user").push(info, user['idToken'] )
        userz = firedb.child("booking").child("user").get(user['idToken'])
        test = firedb.child("booking").child("user").order_by_child("email").equal_to("clever@clever.com").get(user['idToken'])
        print(test.val())
        for u in userz.each():
            userlist.append(u.val())

        return render_template('fireform.html', form=form, userlist=userlist)
        
    else:
         return render_template('fireform.html', form=form, userlist=userlist)

    return render_template('fireform.html', form=form, userlist=userlist)





#ADMIN OVERALL

admin.add_view(ModelView(User, db.session))
path = os.path.join(os.path.dirname(__file__), 'static/assets')
admin.add_view(FileAdmin(path, name='Videos'))

###


#HOMEPAGE (DO NOT TOUCH)
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
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

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


#PROFILE

@app.route('/profile')
def profile():
    return render_template('profile.html')

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
    food = Video.query.filter_by(category = 'food').order_by("date desc").limit(5) #string literal query
    exercise = Video.query.filter_by(category = 'exercise').order_by("date desc").limit(5)
    music = Video.query.filter_by(category = 'music').order_by("date desc").limit(5)
    edu = Video.query.filter_by(category = 'educational').order_by("date desc").limit(5)

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

    
####


### (DO NOT TOUCH)

if __name__ == '__main__':
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.anonymous_user = Anonymous


    @login_manager.user_loader
    def load_user(uid):
        return User.query.get(int(uid))

    app.run(debug=True)
