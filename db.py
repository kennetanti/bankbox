from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from hashlib import md5
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(64))
    is_admin = db.Column(db.Boolean())
    sessionhash = db.Column(db.String(64), unique=True)
    balance = db.Column(db.Integer())

    def __init__(self, username, email, password, is_admin=False):
        self.username = username
        self.email = email
        self.password = md5(password).hexdigest()
        self.sessionhash = md5(username+self.password+email).hexdigest()
        self.is_admin = is_admin

    def __repr__(self):
        return '<User %r>' % self.username

    def login(self, password, ip, user_agent):
        phash = md5(password).hexdigest()
        authenticated = self.password == phash
        la = LoginAttempts(self, authenticated, ip, user_agent)
        db.session.add(la)
        db.session.commit()
        if self.password == phash:
            return self.sessionhash
        return "logout"

class LoginAttempts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    success = db.Column(db.Boolean())
    time_at = db.Column(db.DateTime())
    ip = db.Column(db.String(256))
    user_agent = db.Column(db.String(256))
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('login_attempts', lazy='dynamic'))
    def __init__(self, user, success, ip, user_agent):
        self.success = success
        self.user = user
        self.ip = ip
        self.user_agent = user_agent
        self.time_at = datetime.utcnow()

class Ledger(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    success = db.Column(db.Boolean())
    time_init = db.Column(db.DateTime())
    time_final = db.Column(db.DateTime())
    amount = db.Column(db.Integer())
    ending_balance = db.Column(db.Integer())
    reason = db.Column(db.String(64))
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('ledger', lazy='dynamic'))
    def __init__(self, user, amount, reason):
        self.user = user
        self.amount = amount
        self.reason = reason
        self.success = False
        self.time_init = datetime.utcnow()
        self.time_final = None

class BitKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    privkey = db.Column(db.String(256))
    pubkey = db.Column(db.String(256))
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('bitkeys', lazy='dynamic'))
    finished = db.Column(db.Boolean())
    def __init__(self, user, privkey, pubkey):
        self.user = user
        self.privkey = privkey
        self.pubkey = pubkey
        self.finished = False

class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    privkey = db.Column(db.String(256))
    pubkey = db.Column(db.String(256))
    balance = db.Column(db.Integer())
    def __init__(self, privkey, pubkey):
        self.privkey = privkey
        self.pubkey = pubkey
        self.balance = 0
