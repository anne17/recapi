import os

from flask import send_from_directory, request, jsonify
from flask_restful import Resource
from flask_login import login_user, current_user

from app import app, api, Config
from user import User
import utils


class Hello(Resource):
    def get(self):
        return {"hello": "true"}

api.add_resource(Hello, '/')


class RecipeList(Resource):
    def get(self):
        return utils.load_data(Config.get("DATA", "database"))

api.add_resource(RecipeList, '/recipe-data')


@app.route('/pdf/<path:path>')
def send_pdf(path):
    data_dir = os.path.join(Config.get("DATA", "media_dir"), "pdf")
    return send_from_directory(data_dir, path)


@app.route('/img/<path:path>')
def send_img(path):
    data_dir = os.path.join(Config.get("DATA", "media_dir"), "img")
    return send_from_directory(data_dir, path)


# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
# https://github.com/maxcountryman/flask-login
@app.route('/login', methods=['GET', 'POST'])
def my_login():
    print("current_user:", current_user)
    if current_user.is_authenticated:
        return 'User authenticated!'
    login_data = request.form

    username = login_data["login"]
    password = login_data["password"]
    remember = login_data["remember"]
    user = User()
    user.id = username
    user.username = username
    if not user.is_authenticated(password):
        return jsonify({"status": "error",
                        "message": "Invalid username or password!"}), 200
    login_user(user, remember=remember)
    return jsonify({"status": "success",
                    "user": user.displayname,
                    "message": "User %s logged in successfully!\n" % username}), 200
    # return redirect(url_for('index'))
    # return render_template('login.html', title='Sign In', form=form)

    # next = request.args.get('next')
    # is_safe_url should check if the url is safe for redirects.
    # See http://flask.pocoo.org/snippets/62/ for an example.
    # if not is_safe_url(next):
    #     return flask.abort(400)
