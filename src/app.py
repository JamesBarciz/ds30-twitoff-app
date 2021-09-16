from decouple import config

from flask import Flask, render_template, request

from .models import DB, User
from .twitter import get_user_and_tweets


def create_app():

    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    DB.init_app(app)

    @app.route('/')
    def base():
        if not User.query.all():
            return render_template('base.html', users=[])
        return render_template('base.html', users=User.query.all())

    @app.route('/add_user')
    def add_user():
        user = request.args['username']
        try:
            response = get_user_and_tweets(user)
            if not response:
                return 'Nothing was added.'
            else:
                return f'User: {user} successfully added!'
        except Exception as e:
            return str(e)

    @app.route('/user/<name>', methods=['GET'])
    def user(name=None, message=''):
        try:
            tweets = User.query.filter(User.name == name).one().tweets
            # return str(tweets)
        except Exception as e:
            message = f'Error adding @{name}: {e}'
            tweets = []
        return render_template('user.html', title=name, tweets=tweets, message=message)

    @app.route('/refresh')
    def refresh():
        DB.drop_all()
        DB.create_all()
        return 'Database Refreshed!'

    return app


if __name__ == '__main__':
    create_app().run()
