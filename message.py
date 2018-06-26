import json
import time
from datetime import timedelta, datetime, date
from flask import g, Blueprint, jsonify, request, Response
import utils

message_page = Blueprint('message_page', __name__)

# set global message id
id = -1

@message_page.route('/message/', methods=['GET'])
def get_message():
    """get messages list
    It achieves the get messages' list function.
    ---
    tags:
      - Message
    responses:
      200:
        description:  get messages' list.
    """
    res = {'code': 400}
    # pagination
    total_num = g.mongo.db.message.count()
    page_num = int(request.args.get('pageNum'))
    page_size = int(request.args.get('pageSize'))
    last = page_num * page_size
    first = last - page_size
    list = g.mongo.db.message.find({}, {'_id': 0}).sort([{'createTime', -1}]).skip(first).limit(page_size)
    message_list = []
    for item in list:
        message_list.append(utils.to_json(item))
    res['code'] = 200
    res['messageList'] = message_list
    res['totalNum'] = total_num
    return jsonify(res)

@message_page.route('/message/user/', methods=['GET'])
def get_message_user():
    """get messages list of a user
    It achieves the get message list of a user function.
    ---
    tags:
      - Message
    responses:
      200:
        description:  get message list of a user.
    """
    # verify the browser token
    user_token = request.cookies.get('token')
    today = time.mktime(date.today().timetuple())
    user_log = g.mongo.db.log.find_one({'token': user_token})
    if not user_log or today > user_log['expireDateSecond']:
        res['code'] = 300
        return jsonify(res)
    # get user id
    user_id = user_log['userId']
    print '-------------------------------------'
    print (user_id)
    print '-------------------------------------'
    messages = g.mongo.db.users.find_one({'userId': user_id})
    message_list = reversed(messages['message'])
    user_message_list = []
    for message_id in message_list:
        message = g.mongo.db.message.find_one({'messageId': message_id}, {'_id': 0})
        user_message_list.append(message)
    # pagination
    total_num = len(user_message_list)
    page_num = int(request.args.get('pageNum'))
    page_size = int(request.args.get('pageSize'))
    last = page_num * page_size
    first = last - page_size
    result = user_message_list[first:last]
    res = {'code': 400}
    res['code'] = 200
    res['messageList'] = result
    res['totalNum'] = total_num
    return jsonify(res)


@message_page.route('/message/add/', methods=['POST'])
def add_message():
    """add messages
    It achieves the add messages function.
    ---
    tags:
      - Message
    responses:
      200:
        description: add message successfully.
    """
    data = request.json
    res = {'code': 400, 'message': ''}
    if data is None or data['message'] is None:
        res['message'] = 'Data lost. Please submit again'
        return jsonify(res)
    # verify the browser token
    user_token = request.cookies.get('token')
    today = time.mktime(date.today().timetuple())
    user_log = g.mongo.db.log.find_one({'token': user_token})
    if not user_log or today > user_log['expireDateSecond']:
        res['code'] = 300
        return jsonify(res)
    # the unique id of the user
    count = g.mongo.db.message.count()
    global id
    if (count == 0):
        id = 0
    else:
        id = count
    now = time.time()
    res['item'] = {'messageId': id, 'content': data['message'], 'createTime': now, 'comment': [],
               'sender': {'userId': user_log['userId'], 'name': user_log['userName'], 'gender': user_log['gender']}}
    g.mongo.db.message.insert({'messageId': id, 'content': data['message'], 'createTime': now, 'comment': [],
               'sender': {'userId': user_log['userId'], 'name': user_log['userName'], 'gender': user_log['gender']}})
    g.mongo.db.users.update({'userId': user_log['userId']}, {'$push': {'message': id}})
    res['code'] = 200
    return jsonify(res)

@message_page.route('/message/delete/', methods=['GET'])
def delete_message():
    """delete messages
    It achieves the delete messages function.
    ---
    tags:
      - Message
    responses:
      200:
        description: delete messages successfully.
    """
    message_id = int(request.args.get('messageId'))
    res = {'code': 400, 'message': ''}
    if message_id is None:
        res['message'] = 'Data lost. Please submit again'
        return jsonify(res)
    # verify the browser token
    user_token = request.cookies.get('token')
    today = time.mktime(date.today().timetuple())
    user_log = g.mongo.db.log.find_one({'token': user_token})
    if not user_log or today > user_log['expireDateSecond']:
        res['code'] = 300
        return jsonify(res)
    message = g.mongo.db.message.find_one({'messageId': message_id}, {'_id': 0})
    # remove relative comments
    comment_list = message['comment']
    if comment_list:
        for comment in comment_list:
            g.mongo.db.comment.remove({'commentId': comment})
    # remove the message
    g.mongo.db.message.remove({'messageId': message_id})
    # update user
    g.mongo.db.users.update({'userId': user_log['userId']}, {'$pull': {'message': message_id}})
    res['code'] = 200
    return jsonify(res)