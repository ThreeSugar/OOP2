from datetime import *

def get_google_calendar_time(time_string):
  split_time_list = time_string.split(' ')
  split_date_list = split_time_list[0].split('-')
  combined_date_string = ''.join(split_date_list[::-1])
  joined_time_string = ' '.join([i for i in split_time_list if split_time_list.index(i) != 0])
  joined_time_24hr = str(datetime.strptime(joined_time_string, '%I:%M %p')).split(' ')[1]
  google_calendar_dt_format = combined_date_string + 'T' + joined_time_24hr.replace(':','')
  return google_calendar_dt_format + '/' + google_calendar_dt_format  

def build_link(booking_details):
    event_name = booking_details['gym'] + ': ' + 'Session Booking'
    booking_link = 'http://localhost:5000/session/confirm/' + str(booking_details['id_string'])
    calendar_link = 'https://www.google.com/calendar/render?action=TEMPLATE&text='+ event_name + '&dates=' + get_google_calendar_time(booking_details['date_time']) + '&details=' + 'For+details,+link+here:+' + booking_link + '&location=' + booking_details['address'] + '&sf=true&output=xml'
    return calendar_link

# from datetime(python build-in module) import *
# set google calender (time_string)
# split date, time -> ['30-01-2018', '12:55', 'PM']
# split date to array -> ['30', '01', '2018']
# combined_date, take the date and combined them tgt -> 20180130
# joined.time -> 12:55PM
# 7) joined_time_24 = str... -> take the time convert it to 24hrs -> 12:55:00
# 7) str('%I:%M %p')         -> time format it will be
# 7) split                   -> it will be a string, but i don't want string, so i make it to an array
# 7) [1] -> take the array, -> [12:55:00]
# google calendar date format = -> join the date + time(24hrs) tgt
#                               -> replace ':' with '' (empty)
# return the format with a "/" -> ____(before the slash) is the START date & time
#                              -> ____(after the slash) is the END date & time
#       for the Start & End i put it same date & time, Cus idk what the End date & time for the user thus, put it as the same
