from email.policy import default

from ..extensions import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from slugify import slugify


@login_manager.user_loader
def user_loader(user_id):
	return User.query.get(user_id)


class Category(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	courses = db.relationship('Course', backref='category')


class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True, nullable=False)
	name = db.Column(db.String(120))
	email = db.Column(db.String(200))
	password = db.Column(db.String(50))
	avatar = db.Column(db.String)
	token = db.Column(db.String(150), default='')
	admin = db.Column(db.Boolean, default=False)
	date_created = db.Column(db.DateTime, default=datetime.now())
	basket = db.relationship('Basket', backref='user')
	comment = db.relationship('Comment', backref='user')
	
	def __repr__(self):
		return f'{self.__class__.__name__}: {self.id} - {self.email}'


class Course(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
	title = db.Column(db.String)
	slug = db.Column(db.String)
	price = db.Column(db.Integer, default=0)
	content = db.Column(db.Text)
	image = db.Column(db.String, nullable=True)
	comment_count = db.Column(db.Integer)
	view_count = db.Column(db.Integer)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	students = db.Column(db.String, default='')
	date_created = db.Column(db.DateTime, default=datetime.now())
	date_updated = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
	episodes = db.relationship('Episode', backref='course')
	comments = db.relationship('Comment', backref='course')
	
	def get_teacher(self, id):
		return User.query.get(id).name
	
	@staticmethod
	def generate_slug(target, value, new_value, initiator):
		if value and (not target.slug and value != new_value):
			target.slug = slugify(value)


db.event.listen(Course.title, 'set', Course.generate_slug)


class Episode(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
	title = db.Column(db.String)
	content = db.Column(db.Text)
	type = db.Column(db.String)
	number = db.Column(db.Integer)
	time = db.Column(db.String)
	video_url = db.Column(db.String)
	view_count = db.Column(db.Integer)
	date_created = db.Column(db.DateTime, default=datetime.now())
	date_updated = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())


class Basket(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	
	def get_course(self):
		return Course.query.get(self.course_id)


class Comment(db.Model):
	id = db.Column(db.Integer, primary_key=True, index=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
	text = db.Column(db.Text)
	status = db.Column(db.Boolean, default=False)
	created_at = db.Column(db.DateTime, default=datetime.now())
