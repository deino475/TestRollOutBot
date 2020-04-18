import requests
import os
from models import db
from dotenv import load_dotenv

load_dotenv(verbose = True)

def geolocate(text):
	url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + text + '&key=' + os.getenv('GEOLOCATION_API_KEY')
	r = requests.get(url)
	data = r.json()
	if 'results' not in data:
		return None
	lat = data['results'][0]['geometry']['location']['lat']
	lng = data['results'][0]['geometry']['location']['lng']
	return {'lat' : lat, 'lng' : lng}

def search_for_zip(text):
	list_of_tokens = text.split(" ")
	for token in list_of_tokens:
		if token.isdigit():
			return token
	return False

def search_for_address(text):
	text = text.split(" ")
	address_array = []
	address_endings = ['alley','aly','annex','anex','anx','arcade',
		'arc','avenue','ave','bayou','byu','boulevard','blvd','branch','br','bridge','brg','brook',
		'brk','center','ctr','circle','cir','court','ct','drive','dr','expressway','expy','fld','flts',
		'frge','freeway','fwy','gtwy','highway','hwy','lane','ln','lodge','ldg','manor','mnr','meadow',
		'mdw','mdws','park','pkwy','parkway','place','pl','plaza','plz','road','rd','route','rte','skyway',
		'skwy','street','st','terrace','ter','trafficway','trfy','way']
	address_started = 0
	list_index = len(text)
	while list_index >= 1:
		list_index -= 1
		word = text[list_index]
		if address_started == 0:
			if word.lower() in address_endings:
				address_started = 1
				address_array.append(word)
		elif address_started == 1:
			address_array.append(word)
			if word.isdigit():
				address_started = 2
		elif address_started == 2:
			pass
		else:
			pass

	if len(address_array) == 0:
		return False
	address_array.reverse()
	return "+".join(address_array)

def get_trash_schedule(coords):
	url = "http://api.rollouthouston.com/upcoming?latitude={}&longitude={}".format(coords['lat'],coords['lng'])
	r = requests.get(url)
	data = r.json()
	if 'schedule' not in data:
		return "I'm sorry. I can't find your trash schedule."

	days = {
	   '-1' : 'not sure',
		'1' : 'Monday',
		'2' : 'Tuesday',
		'3' : 'Wednesday',
		'4' : 'Thursday',
		'5' : 'Friday'
	}

	weeks = {
	   '-1' : 'not sure',
		'1' : 'first',
		'2' : 'second',
		'3' : 'third',
		'4' : 'fourth'
	}

	schedule = data['schedule']
	waste_day = days[str(schedule['wasteDay'])]
	junk_week = weeks[str(schedule['junkWeekOfMonth'])]
	junk_day = days[str(schedule['junkDay'])]
	recycling_days = days[str(schedule['recyclingDay'])]
	if schedule['recyclingOnEvenWeeks'] == True:
		recycling_weeks = "even"
	else:
		recycling_weeks = "odd"

	message = "Trash day is on {}. Recycling trash day is on the {} week {}.\
	Heavy trash and yard waste is on the {} {} of the month.".format(waste_day, recycling_weeks, recycling_days, junk_week, junk_day)
	return message

def render(user, text):
	if user.state == 0:
		return return_address_question(user, text)
	if user.state == 1:
		return return_zip_code_question(user, text)
	if user.state == 2:
		return return_trash_schedule(user, text)


def return_address_question(user, text):
	user.state += 1
	db.session.commit()

	return "Hi. This is the Roll Out Chatbot. What is your address (ie 123 Main St)?"

def return_zip_code_question(user, text):
	if search_for_address(text) == False:
		return "This is an invalid address. Please send a valid address (ie 123 Main St)."
	user.address = text
	user.state += 1
	db.session.commit()

	return "What is your zip code?"


def return_trash_schedule(user, text):
	if search_for_zip(text) == False:
		return "This is an invalid zip code. Please send a valid zip code."

	geocodable_addr = "{}+{}".format(user.address, text).replace(" ","+")
	coords = geolocate(geocodable_addr)
	schedule_message = get_trash_schedule(coords)

	user.state = 1
	db.session.commit()

	return "{}. If you want to search again, please text a valid addres (ie 123 Main St).".format(schedule_message)