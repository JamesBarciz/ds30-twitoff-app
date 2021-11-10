# I chose `decouple` over `dotenv` just for aesthetic purposes
from decouple import config

from flask import Flask, render_template, request

# All of my locally-imported files reference the parent folder as this is needed for Heroku
# If this is causing problems locally comment these out and uncomment the modular imports below
from src.models import DB, User
from src.predict import predict_user
from src.twitter import get_user_and_tweets

## Uncomment below if relative imports are finicky for your system/IDE
# from models import DB, User
# from predict import predict_user
# from twitter import get_user_and_tweets


def create_app():
    app = Flask(__name__)

    # The line below will assume you have a SQLite3 database file in your environment variables called DATABASE_URI
    # When this app is pushed to Heroku we will assign the config vars for this to a Postgres instance
    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    DB.init_app(app)

    @app.route('/')
    def base():
        # If there are no users in the database we must set the value of `users` to an empty list
        if not User.query.all():
            return render_template('base.html', users=[])

        # Otherwise...
        return render_template('base.html', users=User.query.all())

    @app.route('/add_user', methods=['POST'])
    def add_user():
        # In order to use this we must allow `POST` method in the app route
        user = request.form.get('user_name')

        try:  # Will attempt to add a user to the DB or update their tweets since adding
            response = get_user_and_tweets(user)

            # `response` will be a value of 0 or greater.  If it is 0, no tweets were added
            if not response:
                return 'Nothing was added.' \
                       '<br><br><a href="/" class="button warning">Go Back!</a>'

            # If `response` has a tweet count of 1 or more...
            else:
                return f'User: {user} successfully added!' \
                       '<br><br><a href="/" class="button warning">Go Back!</a>'

        # If none of the above was able to work, we raise an Exception with the reason why
        except Exception as e:
            return str(e)

    @app.route('/user/<name>', methods=['GET'])
    def user(name=None, message=''):
        """
        This route's purpose is only to display the tweets that were obtained for a particular user
        """

        try:  # Attempt to render the tweets on the webpage
            tweets = User.query.filter(User.name == name).one().tweets

        # If no tweets are obtained, we will raise an Exception on the webpage
        except Exception as e:
            message = f'Error adding @{name}: {e}'
            tweets = []
        return render_template('user.html', title=name, tweets=tweets, message=message)

    @app.route('/compare', methods=['POST'])
    def predict():
        user0 = request.form.get('user0')  # The first user inputted (top)
        user1 = request.form.get('user1')  # The second user inputted (bottom)
        tweet_text = request.form.get('tweet_text')  # What was input into the text box

        # Uses the code in `predict.py` to build a logistic regression model and return a prediction
        prediction = predict_user(user0, user1, tweet_text)

        # If `prediction` is 1 (the first user) it will return `user0` first
        message = '"{}" is more likely to be said by @{} than @{}'.format(
            tweet_text, user0 if prediction else user1,
            user1 if prediction else user0
        )

        return message + '<br><br><a href="/" class="button warning">Go Back!</a>'

    @app.route('/refresh')
    def refresh():
        """
        A hidden route which will wipe the database clean and rebuild from the schema in `models.py`
        """
        DB.drop_all()
        DB.create_all()
        return 'Database Refreshed!'

    return app


# The code below is another way to run the app without using `export FLASK_APP=src:APP flask run`
# Just hit the `PLAY` button up top or enter `python3 src/app.py` in the terminal
if __name__ == '__main__':
    create_app().run()
