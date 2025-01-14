from flask_wtf import FlaskForm, RecaptchaField
from wtforms.fields import StringField, PasswordField, EmailField, BooleanField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class SignupForm(FlaskForm):
	name = StringField('name', validators=[DataRequired()])
	email = EmailField('email', validators=[DataRequired(), Email('email is invalid')])
	password = PasswordField('password', validators=[DataRequired()])
	confirm_password = PasswordField('confirm password', validators=[DataRequired(), EqualTo('password')])
	recaptcha = RecaptchaField()


class SignInForm(FlaskForm):
	email = EmailField('email', validators=[DataRequired(), Email('email is invalid')])
	password = PasswordField('password', validators=[DataRequired()])


# recaptcha = RecaptchaField()


class ChangeInfoForm(FlaskForm):
	name = StringField('name')
	email = EmailField('email')


class ChangePasswordForm(FlaskForm):
	old_password = PasswordField('old password', validators=[DataRequired()])
	new_password = PasswordField('new password', validators=[DataRequired()])
	confirm_password = PasswordField('confirm password', validators=[DataRequired(), EqualTo('new_password')])


class ChangeInfoByAdminForm(FlaskForm):
	name = StringField('name')
	email = EmailField('email')
	new_password = PasswordField('new password')
	admin = BooleanField('is_admin', default=False)


class AddCourseForm(FlaskForm):
	title = StringField('title', validators=[DataRequired()])
	content = TextAreaField('content', validators=[DataRequired()])


class AddEpisodeForm(FlaskForm):
	title = StringField('title', validators=[DataRequired('title is require field ')])
	content = TextAreaField('content', validators=[DataRequired('title is require field ')])
	number = IntegerField('number episode', validators=[DataRequired('title is require field ')])
	time = StringField('time', validators=[DataRequired('title is require field and pattern for input 00:00:00 ')])
	video_url = StringField('video url', validators=[DataRequired('title is require field ')])


class AddNewCategory(FlaskForm):
	name = StringField('name', validators=[DataRequired('name is required field')])