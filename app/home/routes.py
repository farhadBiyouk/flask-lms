from flask import render_template, Blueprint, request
from ..users.models import Course

blueprint = Blueprint('homes', __name__)


@blueprint.route('/')
def home():
	page = request.args.get('page', default=1, type=int)
	courses = Course.query.paginate(page=page, per_page=5)
	return render_template('home.html', courses=courses)
