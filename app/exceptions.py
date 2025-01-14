from flask import render_template


def page_not_found(e):
	return render_template('404.html'), 404


def sever_error(e):
	return render_template('500.html'), 500