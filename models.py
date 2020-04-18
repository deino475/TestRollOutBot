from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
	id = db.Column(db.Integer, primary_key = True, autoincrement = True)
	platform = db.Column(db.String(30))
	contact = db.Column(db.String(100))
	address = db.Column(db.String(100))
	zip_code = db.Column(db.String(10))
	state = db.Column(db.Integer, default = 0)

	def __init__(self, platform, contact):
		self.platform = platform
		self.contact = contact