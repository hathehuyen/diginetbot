from pymongo import MongoClient
from bson import objectid
from werkzeug.security import generate_password_hash, check_password_hash

client = MongoClient('localhost', 27017)
db = client.diginetbot

sessions_db = db.sessions
users_db = db.users
logs_db = db.logs


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

    def insert_one(self, username: str, password: str):
        self.id = users_db.insert_one({'username': username, 'password': generate_password_hash(password)}).inserted_id
        self.username = username
        self.password = generate_password_hash(password)

    def update_one(self, username: str, password: str):
        self.id = users_db.update_one({'username': username, 'password': generate_password_hash(password)}).inserted_id
        self.username = username
        self.password = generate_password_hash(password)


class SessionObj(object):
    def __init__(self):
        self.id = None
        self.user_id = None
        self.status = None
        self.settings = None

    def find_one(self, session_id: str=None, user_id: str=None):
        if session_id:
            session = sessions_db.find_one({'_id': objectid.ObjectId(session_id)})
            if session:
                self.id = session['_id']
                self.user_id = session['user_id']
                self.status = session['status']
                self.settings = session['settings']
        elif user_id:
            session = sessions_db.find_one({'user_id': objectid.ObjectId(user_id)})
            if session:
                self.id = session['_id']
                self.user_id = session['user_id']
                self.status = session['status']
                self.settings = session['settings']

    def save(self):
        result = sessions_db.update_one({'_id': self.id},
                                        {'$set': {'status': self.status, 'settings': self.settings}})
        if not self.id:
            self.id = result.inserted_id
            return self.id
        else:
            return self.id


class LogObj(object):
    def __init__(self):
        self.id = None
        self.user_id = None
        self.session_id = None
        self.text = None

    def save(self):
        result = logs_db.update_one({'_id': self.id}, {"$set": {'user_id': self.user_id, 'session_id': self.session_id,
                                                                'text': self.text}}, upsert=True)
        return result.inserted_id

    def get_logs(self, session_id):
        return logs_db.find({'session_id': session_id})
