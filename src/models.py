from flask_sqlalchemy import SQLAlchemy


DB = SQLAlchemy()


class User(DB.Model):
    # In class, we create a `most_recent_tweet_id` attribute but, this cannot be done in the workaround
    # as there is no way to interact with my API aside from requesting a Twitter user
    id = DB.Column(DB.BIGINT, primary_key=True, nullable=False)
    name = DB.Column(DB.String(15), unique=True, nullable=False)

    def __repr__(self):
        return f'[User: {self.name}]'


class Tweet(DB.Model):
    id = DB.Column(DB.BIGINT, primary_key=True, nullable=False)
    text = DB.Column(DB.Unicode(500), nullable=False)
    user_id = DB.Column(DB.BIGINT, DB.ForeignKey('user.id'), nullable=False)
    embeddings = DB.Column(DB.PickleType, nullable=False)
    user = DB.relationship('User', backref=DB.backref('tweets', lazy=True))

    def __repr__(self):
        return f'[Tweet: {self.text}]'
