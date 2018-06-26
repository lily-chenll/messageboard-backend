from flask import Flask, g
from flask.ext.pymongo import PyMongo
from flask_cors import CORS
from flasgger import Swagger

from comment import comment_page
from message import message_page
from user import user_page

app = Flask(__name__)
CORS(app, supports_credentials=True)
swagger = Swagger(app)

# set database
app.config['MONGO_DBNAME'] = 'messageboard'
pymongo = PyMongo(app)

app.register_blueprint(comment_page)
app.register_blueprint(message_page)
app.register_blueprint(user_page)

@app.before_request
def before_request():
    g.mongo = pymongo

app.run(debug=True)