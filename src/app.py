from decouple import config

from flask import Flask, render_template, request

from src.models import DB, User
from src.predict import predict_user
from src.twitter import get_user_and_tweets


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

    @app.route('/add_user', methods=['POST'])
    def add_user():
        user = request.form.get('user_name')

        try:
            response = get_user_and_tweets(user)
            if not response:
                return 'Nothing was added.' \
                       '<br><br><a href="/" class="button warning">Go Back!</a>'
            else:
                return f'User: {user} successfully added!' \
                       '<br><br><a href="/" class="button warning">Go Back!</a>'
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

    @app.route('/compare', methods=['POST'])
    def predict():
        user0 = request.form.get('user0')
        user1 = request.form.get('user1')
        tweet_text = request.form.get('tweet_text')

        prediction = predict_user(user0, user1, tweet_text)
        message = '"{}" is more likely to be said by @{} than @{}'.format(
            tweet_text, user0 if prediction else user1,
            user1 if prediction else user0
        )

        return message + '<br><br><a href="/" class="button warning">Go Back!</a>'

    @app.route('/refresh')
    def refresh():
        DB.drop_all()
        DB.create_all()
        return 'Database Refreshed!'

    return app


if __name__ == '__main__':
    create_app().run()
