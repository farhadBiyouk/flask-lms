import os.path
import time

from flask import render_template, request, redirect, url_for, flash, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from slugify import slugify

from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from ..extensions import db, bcrypt, mail
from .forms import (SignupForm, SignInForm, ChangeInfoForm, ChangePasswordForm, ChangeInfoByAdminForm,
                    AddCourseForm, AddEpisodeForm, AddNewCategory
                    )
from .models import User, Course, Episode, Category, Basket, Comment
from config import DevConfig
from flask_mail import Message

from uuid import uuid4

blueprint = Blueprint('users', __name__)


@blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
	form = SignupForm()
	if request.method == 'POST':
		if form.validate_on_submit():
			exists_user = User.query.filter_by(email=form.email.data).first()
			if exists_user:
				flash('user already exists, please singup with other email address', 'danger')
				return redirect(url_for('homes.signup'))
			new_user = User(name=request.form['name'], email=form.email.data,
			                password=bcrypt.generate_password_hash(password=form.password.data))
			db.session.add(new_user)
			db.session.commit()
			flash('new user successfully created', 'success')
			return redirect(url_for('homes.home'))
		else:
			return redirect(url_for('users.signup'))
	return render_template('signup.html', form=form)


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
	form = SignInForm()
	if request.method == 'POST':
		if form.validate_on_submit():
			user = User.query.filter_by(email=form.email.data).first()
			if user and bcrypt.check_password_hash(user.password, form.password.data):
				login_user(user)
				next_page = request.args.get('next')
				flash('you logged in successfully', 'success')
				if user.admin:
					return redirect(url_for('users.admin_panel'))
				else:
					return redirect(url_for('users.panel'))
			else:
				flash('Email or password is wrong', 'danger')
	return render_template('singin.html', form=form)


@blueprint.route('/logout')
def logout():
	logout_user()
	flash('you successfully log out ', 'success')
	return redirect(url_for('homes.home'))


@blueprint.route('/panel')
@login_required
def panel():
	return render_template('panel.html')


@blueprint.route('/panel/upload-avatar', methods=['GET', 'POST'])
@login_required
def upload_avatar():
	if request.method == 'POST' and 'avatar' in request.files:
		image = request.files['avatar']
		user = User.query.filter_by(email=current_user.email).first()
		user.avatar = f'uploads/{image.filename}'
		image.save(os.path.join(DevConfig.UPLOAD_DIR, secure_filename(image.filename)))
		db.session.add(user)
		db.session.commit()
		flash('change avatar successfully', 'success')
		return render_template('upload_avatar.html')
	return render_template('upload_avatar.html')


@blueprint.route('/panel/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	user = User.query.filter_by(email=current_user.email).first()
	form = ChangeInfoForm(obj=user)
	if request.method == 'POST':
		if form.validate_on_submit():
			user.name = form.name.data
			user.email = form.email.data
			db.session.add(user)
			db.session.commit()
			flash('your info successfully updated', 'success')
			return redirect(url_for('users.edit_profile'))
		else:
			flash('your input have a error', 'danger')
			return redirect(url_for('users.edit_profile'))
	return render_template('edit_profile.html', form=form)


@blueprint.route('/panel/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
	user = User.query.filter_by(email=current_user.email).first()
	form = ChangePasswordForm()
	if request.method == 'POST':
		if form.validate_on_submit():
			if bcrypt.check_password_hash(user.password, form.old_password.data):
				user.password = bcrypt.generate_password_hash(form.new_password.data)
				db.session.add(user)
				db.session.commit()
				flash('your password successfully changed', 'success')
				return redirect(url_for('users.panel'))
			else:
				flash('the old password wrong', 'danger')
		else:
			flash('data input incorrect', 'danger')
	
	return render_template('change_password.html', form=form)


@blueprint.route('/panel/admin-panel')
@login_required
def admin_panel():
	if not current_user.admin:
		return redirect(url_for('users.panel'))
	return render_template('admin-panel.html')


@blueprint.route('/panel/get-all-users')
@login_required
def get_all_users():
	if not current_user.admin:
		return redirect(url_for('users.panel'))
	users = User.query.all()
	return render_template('list-users.html', users=users)


@blueprint.route('/panel/add-new-user', methods=['GET', 'POST'])
@login_required
def add_new_user():
	if not current_user.admin:
		return redirect(url_for('users.panel'))
	form = SignupForm()
	if request.method == 'POST':
		if form.validate_on_submit():
			exists_user = User.query.filter_by(email=form.email.data).first()
			if exists_user:
				flash('user already exists, please singup with other email address', 'danger')
				return redirect(url_for('homes.signup'))
			new_user = User(name=request.form['name'], email=form.email.data,
			                password=bcrypt.generate_password_hash(password=form.password.data))
			db.session.add(new_user)
			db.session.commit()
			flash('new user successfully created by admin', 'success')
			return redirect(url_for('users.admin_panel'))
		else:
			return redirect(url_for('users.add_new_user'))
	return render_template('new-user.html', form=form)


@blueprint.route('/panel/del_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def del_user(user_id):
	if not current_user.admin:
		return redirect(url_for('users.panel'))
	
	user_obj = User.query.get(user_id)
	db.session.delete(user_obj)
	db.session.commit()
	flash(f'deleted {user_obj.name} successfully', 'success')
	return redirect(url_for('users.get_all_users'))


@blueprint.route('/panel/edit-profile-admin/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_profile_admin(user_id):
	if not current_user.admin:
		return redirect(url_for('users.panel'))
	user = User.query.filter_by(id=user_id).first()
	form = ChangeInfoByAdminForm(obj=user)
	if request.method == 'POST':
		if form.validate_on_submit():
			user.name = form.name.data
			user.email = form.email.data
			user.admin = form.admin.data
			user.password = bcrypt.generate_password_hash(form.new_password.data)
			db.session.add(user)
			db.session.commit()
			flash('your info successfully updated', 'success')
			return redirect(url_for('users.edit_profile_admin', user_id=user.id))
		else:
			flash('your input have a error', 'danger')
			return redirect(url_for('users.edit_profile_admin'))
	return render_template('edit_profile_admin.html', form=form)


@blueprint.route('/panel/add-new-course', methods=['GET', 'POST'])
@login_required
def add_new_course():
	category = Category.query.all()
	form = AddCourseForm()
	if request.method == 'POST':
		if form.validate_on_submit() and 'pic' in request.files:
			pic = request.files['pic']
			pic.save(os.path.join(DevConfig.UPLOAD_DIR, secure_filename(pic.filename)))
			new_course = Course(title=form.title.data, content=form.content.data,
			                    image=f'uploads/{pic.filename}', user_id=current_user.id,
			                    price=request.form.get('price'),
			                    category_id=request.form.get('category')
			                    )
			
			db.session.add(new_course)
			db.session.commit()
			flash('create new course successfully', 'success')
			return redirect(url_for('users.add_new_course'))
		else:
			flash('have error', 'danger')
			return redirect(url_for('users.add_new_course'))
	return render_template('add_new_course.html', form=form, category=category)


@blueprint.route('/all-courses')
def all_courses():
	courses = Course.query.all()
	return render_template('list_course.html', courses=courses)


@blueprint.route('/course/<int:course_id>/<string:slug>')
def single_course(course_id, slug):
	course = Course.query.filter_by(id=course_id, slug=slug).first()
	comments = Comment.query.filter_by(course_id=course.id).all()
	return render_template('single_course.html', course=course, comments=comments)


@blueprint.route('/course/del/<int:course_id>/<string:slug>', methods=['GET', 'POST'])
@login_required
def del_course(course_id, slug):
	if not current_user.admin:
		return redirect(url_for('users.panel'))
	
	course_obj = Course.query.filter_by(id=course_id, slug=slug).first()
	db.session.delete(course_obj)
	db.session.commit()
	flash(f'deleted {course_obj.title} successfully', 'success')
	return redirect(url_for('users.all_courses'))


@blueprint.route('/course/edit/<int:course_id>/<string:slug>', methods=['GET', 'POST'])
def edit_course(course_id, slug):
	category = Category.query.all()
	
	course_obj = Course.query.filter_by(id=course_id, slug=slug).first()
	form = AddCourseForm(obj=course_obj)
	if request.method == 'POST':
		if form.validate_on_submit():
			image = request.files['pic'] if request.files['pic'].filename != '' else course_obj.image
			if isinstance(image, FileStorage):
				image.save(os.path.join(DevConfig.UPLOAD_DIR, secure_filename(image.filename)))
			
			course_obj.title = form.title.data
			course_obj.content = form.content.data
			course_obj.price = request.form['price']
			course_obj.slug = slugify(form.title.data)
			course_obj.image = image if request.files['pic'].filename == '' else f'uploads/{image.filename}'
			course_obj.category_id = request.form.get('category')
			db.session.add(course_obj)
			db.session.commit()
			flash(f'successfully edited course: {course_obj.title}', 'success')
			return redirect(url_for('users.all_courses'))
	return render_template('edit_course.html', form=form, course=course_obj, category=category)


@blueprint.route('/panel/add-episode', methods=['GET', 'POST'])
def add_episode():
	courses = Course.query.all()
	form = AddEpisodeForm()
	if request.method == 'POST':
		if form.validate_on_submit():
			title = form.title.data
			content = form.content.data
			number = form.number.data
			time = form.time.data
			video_url = form.video_url.data
			courses_ids = request.form.get('course')
			type = request.form.get('type')
			
			new_episode = Episode(title=title, content=content, number=number, time=time, video_url=video_url,
			                      course_id=courses_ids, type=type
			                      )
			db.session.add(new_episode)
			db.session.commit()
			flash('add new episode successfully', 'success')
			return redirect(url_for('users.add_episode'))
	return render_template('add_episode.html', form=form, courses=courses)


@blueprint.route('/course/episode/<int:course_id>/<int:ep_id>')
def get_episode(course_id, ep_id):
	db_course = Course.query.get(course_id)
	episode = Episode.query.filter_by(course_id=db_course.id, id=ep_id).first()
	return render_template('single_episode.html', episode=episode)


@blueprint.route('/course/episode/edit/<int:course_id>/<int:ep_id>', methods=["GET", 'POST'])
def edit_episode(course_id, ep_id):
	db_course = Course.query.get(course_id)
	episode = Episode.query.filter_by(course_id=db_course.id, id=ep_id).first()
	form = AddEpisodeForm(obj=episode)
	if request.method == 'POST':
		if form.validate_on_submit():
			episode.title = form.title.data
			episode.content = form.content.data
			episode.number = form.number.data
			episode.time = form.time.data
			episode.video_url = form.video_url.data
			episode.courses_ids = db_course.id
			episode.type = request.form.get('type')
			
			db.session.add(episode)
			db.session.commit()
			flash('episode successfully updated', 'success')
			return redirect(url_for('users.edit_episode', course_id=course_id, ep_id=ep_id))
	return render_template('edit_episode.html', form=form)


@blueprint.route('/course/episode/del/<int:course_id>/<int:ep_id>', methods=['GET', 'POST'])
@login_required
def del_episode(course_id, ep_id):
	db_course = Course.query.get(course_id)
	episode = Episode.query.filter_by(course_id=db_course.id, id=ep_id).first()
	db.session.delete(episode)
	db.session.commit()
	flash(f'deleted {episode.title} successfully', 'info')
	return redirect(url_for('users.single_course', course_id=course_id, slug=db_course.slug))


@blueprint.route('/panel/admin-panel/add-category', methods=['GET', 'POST'])
def add_category():
	form = AddNewCategory()
	if request.method == 'POST':
		if form.validate_on_submit():
			new_cat = Category(name=form.name.data)
			db.session.add(new_cat)
			db.session.commit()
			flash('add new category successfully', 'success')
			return redirect(url_for('users.add_category'))
	return render_template('add_category.html', form=form)


@blueprint.route('/category/<string:cat_name>')
def get_course_by_category(cat_name):
	cat = Category.query.filter_by(name=cat_name).one()
	page = request.args.get('page', default=1, type=int)
	courses = Course.query.filter_by(category_id=cat.id).paginate(page=page, per_page=3)
	return render_template('category_filter.html', courses=courses)


@blueprint.route('/search/')
def search_course():
	list_course = []
	search_word = request.args.get('q')
	courses_all = Course.query.all()
	
	for crs in courses_all:
		if search_word in crs.title or search_word in crs.content:
			list_course.append(crs)
	
	return render_template('result_search.html', courses=list_course)


@blueprint.route('/add-to-basket', methods=['POST'])
def add_to_basket():
	course_id = request.form.get('course_id')
	slug = request.form.get('slug')
	user_id = current_user.id
	basket = Basket.query.filter_by(user_id=user_id).all()
	if basket != []:
		for product in basket:
			if product.course_id == course_id:
				flash('course was added to basket', 'warning')
				return redirect(url_for('users.single_course', course_id=course_id, slug=slug))
	
	new_basket = Basket(user_id=user_id, course_id=course_id)
	db.session.add(new_basket)
	db.session.commit()
	flash('added course to basket successfully', 'success')
	return redirect(url_for('users.checkout'))


@blueprint.route('/checkout', methods=['GET', "POST"])
def checkout():
	basket = Basket.query.filter_by(user_id=current_user.id).all()
	total_price = 0
	for product in basket:
		total_price += int(product.get_course().price)
	return render_template('checkout.html', basket=basket, total_price=total_price)


@blueprint.route('/basket/del/<int:course_id>')
def del_basket(course_id):
	Basket.query.filter_by(id=course_id).delete()
	db.session.commit()
	flash(f'deleted course from basket successfully', 'success')
	return redirect(url_for('users.checkout'))


@blueprint.route('/basket/checkout/payment')
def payment():
	basket = Basket.query.filter_by(user_id=current_user.id).all()
	total_price = 0
	list_id = []
	
	for product in basket:
		total_price += int(product.get_course().price)
		list_id.append(str(product.get_course().id))
	
	time.sleep(5)
	
	for item in list_id:
		items = Course.query.filter_by(id=int(item)).first()
		items.students = ','.join(str(items.students) + ','.join(str(current_user.id)))
		
		db.session.add(items)
		db.session.commit()
		
		Basket.query.filter_by(user_id=current_user.id).delete()
		db.session.commit()
		return redirect(url_for('homes.home'))
	
	return redirect(url_for('users.checkout'))


@blueprint.route('/course/<int:course_id>/comment', methods=['GET', 'POST'])
def create_comment(course_id):
	course = Course.query.filter_by(id=course_id).first()
	if request.method == 'POST':
		new_comment = Comment(course_id=course_id, user_id=current_user.id, text=request.form.get('text'))
		db.session.add(new_comment)
		db.session.commit()
		return redirect(url_for('users.single_course', course_id=course_id, slug=course.slug))


@blueprint.route('/user/forget', methods=['GET', 'POST'])
def forget_password():
	if request.method == 'POST':
		user_obj = User.query.filter_by(id=current_user.id).first()
		user_obj.token = str(uuid4())
		db.session.add(user_obj)
		db.session.commit()
		
		msg = Message(subject='Reset password', sender=DevConfig.MAIL_USERNAME, recipients=[DevConfig.MAIL_USERNAME])
		msg.body = "please click button for continue for reset password"
		msg.html = f'<a href="http://localhost:5000/resetpassword/{user_obj.token}/{user_obj.id}"></a>'
		mail.send(msg)
		print(msg.body)
		print(msg.html)
		flash('sent forget password successfully', 'success')
		return render_template('forget.html')
	return render_template('forget.html')


@blueprint.route('/resetpassword/<token>/<user_id>', methods=['GET', 'POST'])
def reset_password(token, user_id):
	if request.method == 'POST':
		user_db = User.query.filter_by(token=token, id=user_id).first()
		new_password = request.form.get('password1')
		new_password2 = request.form.get('re-password1')
		if new_password == new_password2:
			user_db.password = bcrypt.generate_password_hash(new_password)
			user_db.token = ''
			db.session.add(user_db)
			db.session.commit()
			flash('changed password successfully', 'success')
			return redirect(url_for('users.login'))
		else:
			flash('passwords not match', 'danger')
	return render_template('reset_password.html')
