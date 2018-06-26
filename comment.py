import json
import time
from datetime import timedelta, datetime, date
from flask import g, Blueprint, jsonify, request, Response
import utils

comment_page = Blueprint('comment_page', __name__)

# set global message id
id = -1


@comment_page.route('/comment/', methods=['GET'])
def get_comment():
    """get comment list
    It achieves the get comment' list function.
    ---
    tags:
      - Comment
    responses:
      200:
        description:  get comment list.
    """
    # get message id
    message_id = int(request.args.get('messageId'))
    comment = g.mongo.db.message.find_one({'messageId': message_id})
    if comment is not None:
        comments = reversed(comment['comment'])
    print "========================================="
    print (comment)
    print "========================================="
    comment_list = []
    if comments:
        for comment_id in comments:
            comment = g.mongo.db.comment.find_one({'commentId': comment_id}, {'_id': 0})
            comment_list.append(comment)
    # pagination
    totalNum = len(comment_list)
    # pageNum = request.args.get('pageNum')
    # pageSize = request.args.get('pageSize')
    res = {'code': 400}
    res['code'] = 200
    res['commentList'] = comment_list
    res['totalNum'] = totalNum
    return jsonify(res)


@comment_page.route('/comment/add/', methods=['POST'])
def add_comment():
    """add comment
    It achieves the add comment function.
    ---
    tags:
      - Comment
    responses:
      200:
        description: add comment successfully.
    """
    data = request.json
    print "========================================="
    print (data)
    print "========================================="
    res = {'code': 400, 'message': ''}
    if data is None or data['comment'] is None or data['messageId'] is None or data['receiverId'] is None:
        res['message'] = 'Data lost. Please submit again'
        return jsonify(res)
    # verify the browser token
    user_token = request.cookies.get('token')
    today = time.mktime(date.today().timetuple())
    user_log = g.mongo.db.log.find_one({'token': user_token})
    if not user_log or today > user_log['expireDateSecond']:
        res['code'] = 300
        return jsonify(res)
    # the unique id of the comment
    count = g.mongo.db.comment.count()
    global id
    if (count == 0):
        id = 0
    else:
        id = count
    # insert comment
    receiver = g.mongo.db.users.find_one({'userId': data['receiverId']})
    now = time.time()
    res['item'] = {'commentId': id, 'messageId': data['messageId'],
                             'content': data['comment'], 'createTime': now,
                             'sender': {'userId': user_log['userId'], 'name': user_log['userName']},
                             'receiver': {'userId': data['receiverId'], 'name': receiver['name']}}
    g.mongo.db.comment.insert({'commentId': id, 'messageId': data['messageId'],
                             'content': data['comment'], 'createTime': now,
                             'sender': {'userId': user_log['userId'], 'name': user_log['userName']},
                             'receiver': {'userId': data['receiverId'], 'name': receiver['name']}})
    # update message
    g.mongo.db.message.update({'messageId': data['messageId']}, {'$push': {'comment': id}})
    # update user
    g.mongo.db.users.update({'userId': user_log['userId']}, {'$push': {'comment': id}})
    res['code'] = 200
    return jsonify(res)


@comment_page.route('/comment/delete/', methods=['GET'])
def delete_message():
    """delete comment
    It achieves the delete comment function.
    ---
    tags:
      - Comment
    responses:
      200:
        description: delete comment successfully.
    """
    comment_id = int(request.args.get('commentId'))
    print "========================================="
    print (comment_id)
    print "========================================="
    res = {'code': 400, 'message': ''}
    if comment_id is None:
        res['message'] = 'Data lost. Please submit again'
        return jsonify(res)
    # verify the browser token
    user_token = request.cookies.get('token')
    today = time.mktime(date.today().timetuple())
    user_log = g.mongo.db.log.find_one({'token': user_token})
    if not user_log or today > user_log['expireDateSecond']:
        res['code'] = 300
        return jsonify(res)
    comment = g.mongo.db.comment.find_one({'commentId': comment_id})
    message_id = comment['messageId']
    # remove comment
    g.mongo.db.comment.remove({'commentId': comment_id})
    # update message
    g.mongo.db.message.update({'messageId': message_id}, {'$pull': {'comment': comment_id}})
    # update user
    g.mongo.db.users.update({'userId': user_log['userId']}, {'$pull': {'comment': comment_id}})
    res['code'] = 200
    return jsonify(res)