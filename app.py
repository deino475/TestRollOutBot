from flask import Flask, Response, request
from functions import db, render
from models import Users
import os
from dotenv import load_dotenv

load_dotenv(verbose = True)
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/', methods = ['GET'])
def index_route():
	return "Hi."

@app.route('/twilio', methods = ['POST'])
def twilio_route():
	phone_number = request.form['From']
	user_message = request.form['Body']

	user = Users.query.filter_by(contact = phone_number).filter_by(platform = "twilio").first()
	if user == None:
		new_user = Users("twilio",phone_number)
		db.session.add(new_user)
		db.session.commit()

		user = Users.query.filter_by(contact = phone_number).filter_by(platform = "twilio").first()

	response_message = render(user, user_message)
	xml = "<Response><Message>{}</Message></Response>".format(response_message)

	return Response(xml, mimetype = "text/xml")

if __name__ == "__main__":
	app.run()