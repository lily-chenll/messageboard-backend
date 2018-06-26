import json
import time
import ast
from datetime import timedelta, datetime, date
from flask import g, Blueprint, jsonify, request, Response
import utils

user_page = Blueprint('user_page', __name__)

# set global user id
id = -1

@user_page.route('/user/', methods=['GET'])
def verify_user():
    """Verify user
        It achieves the auto-login function.
        ---
        tags:
          - User
        responses:
          200:
            description: verify user successfully.
        """
    token = request.cookies.get('token')
    res = {'code': 400, 'user': ''}
    if token is None:
        return jsonify(res)
    user_log = g.mongo.db.log.find_one({'token': token})
    if user_log is None:
        return jsonify(res)
    # verify the user token whether has been expired
    now = time.mktime(date.today().timetuple())
    if now > user_log['expireDateSecond']:
        res.code = 300
        return jsonify(res)
    res['code'] = 200
    user = g.mongo.db.users.find_one({'userId': user_log['userId']})
    res['user'] = {'id': user['userId'], 'name': user['name'], 'gender': user['gender'], 'birth': user['birthSecond']}
    return jsonify(res)


@user_page.route('/user/verify-name/', methods=['GET'])
def verify_name():
    """Verify user's name
        It achieves the verification function.
        ---
        tags:
          - User
        responses:
          200:
            description: verify user successfully.
        """
    name = request.args.get('name')
    res = {'code': 400, 'message': ''}
    if name is None:
        res['message'] = 'Data lost. Please submit again'
        return jsonify(res)
    # verify whether the name has been registered
    if utils.verify_user_name(name):
        res['message'] = 'The user name has been existed'
        return jsonify(res)
    res['code'] = 200
    return jsonify(res)

@user_page.route('/user/register/', methods=['POST'])
def user_register():
    """Register users
    It achieves the sign up function.
    ---
    tags:
      - User
    responses:
      200:
        description: user sign up successfully.
    """
    data = request.json
    print "========================================="
    print (data)
    print "========================================="
    # status: 200 success, 300: need to log in again, 400: there is some error
    res = {'code': 400, 'message': ''}
    if data is None or data['name'] is None or data['birthSecond'] is None or data['gender'] is None or data['password'] is None:
        res['message'] = 'Data lost. Please submit again'
        return jsonify(res)
    # the unique id of the user
    count = g.mongo.db.users.count()
    global id
    if (count == 0):
        id = 0
    else:
        id = count
    # insert the user
    data['permission'] = 'normal'
    password = data['password']
    data['password'] = utils.encrypt_pass(password)
    data['userId'] = id
    data['message'] = []
    data['comment'] = []
    _id = g.mongo.db.users.insert(data)
    print "-----------------------------------------"
    print _id
    print "-----------------------------------------"
    # generate token and transfer to the brower
    token = utils.generate_auto_token(str(_id))
    expire = date.today() + timedelta(days=7)
    expire_date = time.mktime(expire.timetuple())
    log = {'userId': id, 'userName': data['name'], 'gender': data['gender'], 'token': token, 'expireDateSecond': expire_date}
    g.mongo.db.log.insert(log)
    response = Response()
    temp_user = {'userId': id}
    response.data = json.dumps({'code': 200, 'user': temp_user})
    response.set_cookie('token', value=token, expires=expire_date, httponly=True)
    print "******************************************"
    print response
    print "******************************************"
    return response

@user_page.route('/user/login/', methods=['POST'])
def user_login():
    """Login users
    It achieves the login function.
    ---
    tags:
      - User
    responses:
      200:
        description: user login successfully.
    """
    data = request.json
    print "========================================="
    print (data)
    print "========================================="
    print "----------------------------------------"
    print (request.headers)
    print "----------------------------------------"
    print "----------------------------------------"
    print (g.mongo.db.log.find_one({'userName': data['name']}))
    print "----------------------------------------"
    res = {'code': 400, 'message': ''}
    if data is None or data['name'] is None or data['password'] is None:
        res['message'] = 'Data lost. Please submit again'
        return jsonify(res)
    # verify whether the name has been registered
    if not utils.verify_user_name(data['name']):
        res['message'] = 'The name does not exist. Please register first'
        return jsonify(res)
    user = g.mongo.db.users.find_one({'name': data['name']})
    password = utils.encrypt_pass(data['password'])
    # verify whether the password is correct
    if user['password'] == password:
        token = utils.generate_auto_token(str(user['_id']))
        expire = date.today() + timedelta(days=7)
        expire_date = time.mktime(expire.timetuple())
        g.mongo.db.log.update({'userId': user['userId']}, {'$set': {'expireDateSecond': expire_date}})
        g.mongo.db.log.update({'userId': user['userId']}, {'$set': {'token': token}})
        response = Response()
        response.data = json.dumps({'code': 200, 'user': {'userId': user['userId'], 'userName': user['name'],
                                                          'userBirth': user['birthSecond'], 'userGender': user['gender']}})
        response.set_cookie('token', value=token, expires=expire_date, httponly=True)
        return response
    res['message'] = 'The password is not correct'
    return jsonify(res)

@user_page.route('/user/update/', methods=['POST'])
def user_update():
    """Update users' info
    It achieves the update function.
    ---
    tags:
      - User
    responses:
      200:
        description: user update successfully.
    """
    data = request.json
    print "========================================="
    print (data)
    print "========================================="
    res = {'code': 400, 'message': ''}
    if data is None:
        res['message'] = 'Data lost. Please submit again'
        return jsonify(res)
    # verify whether the browser has cookie
    user_token = request.cookies.get('token')
    now = time.mktime(date.today().timetuple())
    user_log = g.mongo.db.log.find_one({'token': user_token})
    # verify the user token whether has been expired
    if not user_log or now > user_log['expireDateSecond']:
        res['code'] = 300
        return jsonify(res)
    temp_user = {}
    if data['name']:
        temp_user['name'] = data['name']
    if data['password']:
        temp_user['password'] = utils.encrypt_pass(data['password'])
    if temp_user != {}:
        g.mongo.db.users.update({'userId': user_log['userId']}, {'$set': temp_user})
    res['code'] = 200

    return jsonify(res)