from flask_sqlalchemy import SQLAlchemy


DB = SQLAlchemy()


class User(DB.Model):
    id = DB.Column(DB.BIGINT, primary_key=True, nullable=False)
    name = DB.Column(DB.String(15), unique=True, nullable=False)

    def __repr__(self):
        return f'[User: {self.name}]'


class Tweet(DB.Model):
    id = DB.Column(DB.BIGINT, primary_key=True, nullable=False)
    text = DB.Column(DB.Unicode(300), nullable=False)
    user_id = DB.Column(DB.BIGINT, DB.ForeignKey('user.id'), nullable=False)
    user = DB.relationship('User', backref=DB.backref('tweets', lazy=True))

    def __repr__(self):
        return f'[Tweet: {self.text}]'
