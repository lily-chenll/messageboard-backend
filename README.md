# messageboard-backend
the backend codes of my messageboard

steps:
  1. install the python virtual environment and mongodb first
  2. pip install datetime, flask, flask.ext.pymongo, flask_cors and flagger
  3. git pull the codes
  4. modify the database connection code in blueprint.py:
  
    # set database
    app.config['MONGO_DBNAME'] = 'messageboard'
    pymongo = PyMongo(app)
  
  5. run the project in the virtual environment
  
  ￼
