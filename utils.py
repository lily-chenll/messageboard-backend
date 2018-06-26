import hashlib
import time
import json
from datetime import timedelta, datetime
from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId


db = MongoClient('localhost', 27017).messageboard


def encrypt_pass(password):
    md5 = hashlib.md5()
    md5.update(password)
    new_password = md5.hexdigest()
    return new_password


def generate_auto_token(id):
    md5 = hashlib.md5()
    current_time = str(time.time())
    md5.update(id)
    md5.update(current_time)
    token = md5.hexdigest()
    return token


def verify_user_name(name):
    user = db.users.find_one({'name': name})
    if not user:
        return False
    return True


def verify_token(request):
    data = {}
    # verify whether the browser has cookie
    user_token = request.cookies.get('token')
    now = time.mktime(date.today().timetuple())
    user_log = g.mongo.db.log.find_one({'token': user_token})
    # verify the user token whether has been expired
    if not user_log or now > user_log['expireDateSecond']:
        data['code'] = 300
        return data
    data['code'] = 200
    data['user_log'] = user_log
    return data


def to_json(item):
    return eval(dumps(item))


