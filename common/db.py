from pymongo import MongoClient
from bson import objectid
from werkzeug.security import generate_password_hash, check_password_hash

client = MongoClient('localhost', 27017)
db = client.diginetbot

sessions_db = db.sessions
users_db = db.users


class UserObj(object):
    def __init__(self):
        self.username = None
        self.password = None
        self.id = None

    def find_one(self, username: str):
        user = users_db.find_one({'username': username})
        if user:
            self.username = username
            self.password = user['password']
            self.id = user['_id']

    def update_one(self, username: str, password: str):
        self.id = users_db.update_one({'username': username, 'password': generate_password_hash(password)}).inserted_id
        self.username = username
        self.password = generate_password_hash(password)


class SessionObj(object):
    def __init__(self):
        self.user_id = None
        self.status = None
        self.settings = None

    def find_one(self, session_id: str):
        session = sessions_db.find_one({'_id': objectid.ObjectId(session_id)})
        if session:
            self.user_id = session['user_id']
            self.status = session['status']
            self.settings = session['settings']
