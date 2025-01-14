import os


class Config:
	BASE_DIR = os.path.abspath(os.path.dirname(__file__))
	CSRF_ENABLE = True
	CSRF_SESSION_KEY = 'f13269ab4f664beef25f52047e6d4a8434a3b6f9d0c7d521e5b1b09ef74dac0c'
	SECRET_KEY = '20cf319a39adca7524457a211dc98f6eb747201256b2ae60da67ea24577cfc2a'
	UPLOAD_DIR = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
	RECAPTCHA_PUBLIC_KEY = '6LeKlasqAAAAANj9A_iTT5Jp3lZRO3sMOVrQ76ql'
	RECAPTCHA_PRIVATE_KEY = '6LeKlasqAAAAAOf8hhRW6y_txw4N7t-CayefrBrh'
	MAIL_SERVER = 'smtp.gmail.com'
	MAIL_PORT = 587
	MAIL_USERNAME = 'farhad.biyouk1999@gmail.com'
	MAIL_PASSWORD = 'rlqetbpbahhiifzm'
	MAIL_USE_TLS = True
	MAIL_USE_SSL = False


class ProConfig(Config):
	DEBUG = False
	SQLALCHEMY_DATABASE_URI = ...


class DevConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(Config.BASE_DIR, 'app.db')
