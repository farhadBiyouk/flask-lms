from flask import Flask
from flask_login import current_user

from .home.routes import blueprint as home_blueprint
from .users.routes import blueprint as user_blueprint
from .exceptions import page_not_found, sever_error
from .extensions import db, migrate, bcrypt, login_manager, mail
from .users.models import Category, Basket

app = Flask(__name__)


@app.template_filter
def commafy(data):
	return f'{data:,}'


# BluePrint
app.register_blueprint(home_blueprint)
app.register_blueprint(user_blueprint)

# Exception
app.register_error_handler(404, page_not_found)
app.register_error_handler(500, sever_error)

# Config
app.config.from_object('config.DevConfig')

# Database
db.init_app(app)

from .users.models import User

migrate.init_app(app, db)

# Encrypt password

bcrypt.init_app(app)

# Authentication

login_manager.init_app(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'warning'

# email config

mail.init_app(app)


# context processor
@app.context_processor
def get_context_processor():
	return {'categories': Category.query.all()}


@app.context_processor
def get_count_basket():
	if current_user.is_authenticated:
		basket_count = Basket.query.filter_by(user_id=current_user.id).count()
	else:
		basket_count = ''
	return {'basket_count': basket_count}


@app.template_filter("comma_number")
def comma_number(value):
	return f'{value:,}'
