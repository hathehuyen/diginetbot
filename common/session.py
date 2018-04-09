from common import db
from flask import request
from bson import objectid
from werkzeug.security import generate_password_hash, check_password_hash


class Session(object):
    def __init__(self):
        pass

    @staticmethod
    def start(username, password):
        user = db.users_db.find_one({'username': username})
        # create user if not exist
        if not user:
            user_id = db.users_db.insert_one({'username': username,
                                              'password': generate_password_hash(password)}).inserted_id
        # check user pass word
        elif check_password_hash(user['password'], password):
            user_id = user['_id']
        else:
            return False
        session = db.sessions_db.find_one({'user_id': user_id})
        if session:
            db.sessions_db.update_one({{'user_id': user_id, 'status': 'active'}})
            return session
        else:
            session_id = db.sessions_db.insert_one({'user_id': user_id, 'status': 'active'}).inserted_id
            return db.sessions_db.find_one({'_id': session_id})

    @staticmethod
    def stop(token):
        pass

    @classmethod
    def resume(self, token):
        session = db.sessions_db.find_one({'_id': objectid.ObjectId(token)})
        if session:
            return session
        else:
            return False


# Decorator
def user_session(func):
    def func_wrapper():
        token = request.values['token']
        session = Session.resume(token)
        return func(session)
    return func_wrapper
