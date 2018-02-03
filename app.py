import requests
import pyrebase
from hashids import Hashids
from flask import Flask, render_template, url_for, request, redirect
from flask_mail import Mail, Message
from lib import message_builder


hashid_salt = 'impossible to guess'
hashids = Hashids(salt = hashid_salt, min_length = 4)


API_KEY = 'AIzaSyC-untCAlzyRtrAuJ6ShicN0aHCHMD94jg'

firebase_config = {
  "apiKey": "AIzaSyDrw2z11cWBjIVNWYKYcLCdjR0wCJ3w7HY",
  "authDomain": "gym-finder-78813.firebaseapp.com",
  "databaseURL": "https://gym-finder-78813.firebaseio.com",
  "storageBucket": "gym-finder-78813.appspot.com"
}

gyms_email_address = 'thisappemail@gmail.com'

firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()

app = Flask(__name__)
mail = Mail(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'findgym2@gmail.com'
app.config['MAIL_PASSWORD'] = 'uaplwjtchijsoknk'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


def sendmail(mail, msg_subject, msg_sender, msg_recipients, message_html):
    message = Message(msg_subject, sender = msg_sender, recipients = msg_recipients)
    message.html = message_html
    mail.send(message)
    return True


@app.route('/')
def home_page():
    return 'Nothing Here for now'

@app.route('/gym')
def gym_page():
    return render_template('index.html')

# Search for gyms
@app.route('/gym/find', methods = ["POST"])
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
        return render_template('gyms.html', gyms=places_response)

# The gym equipment page
@app.route('/gym/tools', methods=["GET"])
def list_tools():
    all_tools = requests.get('https://api.myjson.com/bins/r4kxh').json()
    page_one = [tool for tool in all_tools if(tool['id'] <= 16)]
    next_page = 2
    return render_template('equipment.html', tools = page_one, next_page = next_page)

@app.route('/gym/tools/<page_id>', methods=["GET"])
def list_tool_next_page(page_id):
    all_tools = requests.get('https://api.myjson.com/bins/r4kxh').json()
    page_two = [tool for tool in all_tools if(tool['id'] >= 17)]
    return render_template('equipment.html', tools = page_two)

# The map, boooking, gym details page
@app.route('/gym/more/<place_id>', methods=["GET", "POST"])
def gym_info(place_id):
    if request.method == 'GET':
        place_api_url = 'https://maps.googleapis.com/maps/api/place/details/json?placeid=' + place_id + '&key=AIzaSyDHHLWzJzlZZFDye9JbxiCu4RXei_bzMbE'
        place_details_response = requests.get(place_api_url).json()
        return render_template('gym.html', gym=place_details_response)
    if request.method == 'POST':
        new_booking_id = None
        try:
            bookings = db.child("bookings").get().val()
            booking_id = [entry for entry in bookings][-1]['id']
            new_booking_id = int(booking_id) + 1
        except:
            new_booking_id = 0
        
        new_booking_ref = db.child("bookings").child(new_booking_id)
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

# email confirm
@app.route('/session/confirm/<booking_id>')       
def display_confirmation(booking_id):
    real_booking_id = hashids.decode(booking_id)[0]
    booking_ref = db.child('bookings').child(real_booking_id)
    result = booking_ref.get().val()
    booking_details = dict(result)
    return render_template('confirm.html', booking_details=booking_details)

# email cancel(user & gym)
@app.route('/session/user_cancel/<booking_id>')
def user_delete_and_confirm(booking_id):
    real_booking_id = hashids.decode(booking_id)[0]
    booking_ref = db.child("bookings").child(real_booking_id)
    booking_details = booking_ref.get().val()
    booking_ref.remove()
    user_cancel_message = message_builder.user_cancel_message(booking_details)
    user_cancel_confirm_message = message_builder.user_cancel_confirm(booking_details)
    sendmail(mail, user_cancel_message['subject'], 'findgym2@gmail.com', [gyms_email_address], user_cancel_message['html'])
    sendmail(mail, user_cancel_confirm_message['subject'], 'findgym2@gmail.com', [booking_details['email']], user_cancel_confirm_message['html'])
    return render_template('confirm_delete.html', booking_details=booking_details)

@app.route('/session/gym_cancel/<booking_id>')
def gym_delete_and_confirm(booking_id):
    real_booking_id = hashids.decode(booking_id)[0]
    booking_ref = db.child("bookings").child(real_booking_id)
    booking_details = booking_ref.get().val()
    booking_ref.remove()
    gym_cancel_message = message_builder.gym_cancel_message(booking_details)
    gym_cancel_confirm_message = message_builder.gym_cancel_confirm(booking_details)
    sendmail(mail, gym_cancel_message['subject'], 'findgym2@gmail.com', [booking_details['email']], gym_cancel_message['html'])
    sendmail(mail, gym_cancel_confirm_message['subject'], 'findgym2@gmail.com', [gyms_email_address], gym_cancel_confirm_message['html'])
    return render_template('confirm_delete.html', booking_details = booking_details)

if __name__ == "__main__":
    app.run(debug=True)

