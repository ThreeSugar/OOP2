from lib import calendar_link_builder

def user_message(booking_details):
    message = {}
    message['html'] = ''
    message_subject = 'Gym Finder: Booking Confirmation'
    
    message_html = 'Hello <strong>' + booking_details['name'] + '</strong>, <br /> <br />'
    message_html += 'You have scheduled a gym session and here details of your booking <br />'
    message_html += '<span> Gym Name: </span> <strong>' + booking_details['gym'] + '</strong> <br />'
    message_html += '<span> Scheduled Time: </span>' + '<strong> ' + booking_details['date_time'] + '</strong> <br /> <br />'
    message_html += '<a href="http://localhost:5000/session/confirm/' + str(booking_details['id_string']) + '\"' + '> View Booking </a> <br />'
    message_html += '<a href="'+ calendar_link_builder.build_link(booking_details) + '\"' + '> Add to Calendar </a> <br />'
    message_html += '<a href="http://localhost:5000/session/user_cancel/' + str(booking_details['id_string']) + '\"' + '> Cancel Booking </a>'
   
    message['subject'] = message_subject
    message['html'] = message_html

    return message

def gym_message(booking_details):
    message = {}
    message['html'] = ''
    message_subject = 'New Session Booking'

    message_html = 'Name: <strong>' + booking_details['name'] + '</strong>, <br /> <br />'
    message_html += 'Email Address: <strong> ' + booking_details['email'] + '</br /> </br />'
    message_html += '<span> Gym Name: </span> <strong>' + booking_details['gym'] + '</strong> <br />'
    message_html += '<span> Scheduled Time: </span>' + '<strong> ' + booking_details['date_time'] + '</strong> <br /> <br />'
    message_html += '<a href="http://localhost:5000/session/confirm/' + str(booking_details['id_string']) + '\"' + '> View Booking </a> <br />'
    message_html += '<a href="http://localhost:5000/session/gym_cancel/' + str(booking_details['id_string']) + '\"' + '> Cancel Booking </a>'

    message['subject'] = message_subject
    message['html'] = message_html
    
    return message

# Message sent to user when the gym cancels
def gym_cancel_message(booking_details):
    message = {}
    message['html'] = ''
    message_subject = 'Appointment Cancellation'
    message_html = 'Hi ' + booking_details['name'] + ', <br /> <br />'
    message_html += 'We are so sorry to inform you that <strong>' + booking_details['gym'] + '</strong> has cancelled your scheduled appointment. <br /> <br />'
    message['subject'] = message_subject
    message['html'] = message_html
    return message

# Message sent to the gym when gym cancels
def gym_cancel_confirm(booking_details):
    message = {}
    message['html'] = ''
    message_subject = 'Appointment Cancellation Confirmation'

    message_html = 'You have cancelled appointment by: <strong>' + booking_details['name'] + '</strong>, <p> A message has been sent to the user </p> <br /> <br />'
    message['subject'] = message_subject
    message['html'] = message_html    
    return message


# Message sent to the gym when user cancels
def user_cancel_message(booking_details):
    message = {}
    message['html'] = ''
    message_subject = 'Appointment Cancellation'
    message_html = 'Hello, <br /> <br />'
    message_html += 'We are so sorry to inform you that <strong>' + booking_details['name'] + '</strong> has cancelled the scheduled appointment. <br /> <br />'
    message['subject'] = message_subject
    message['html'] = message_html
    return message

# Message sent to user when user cancels
def user_cancel_confirm(booking_details):
    message = {}
    message['html'] = ''
    message_subject = 'Appointment Cancellation Confirmation'

    message_html = 'You have cancelled your scheduled appointment with <strong>' + booking_details['gym'] + '</strong>, <p> A message has been sent to the gym </p> <br /> <br />'
    message['subject'] = message_subject
    message['html'] = message_html    
    return message

