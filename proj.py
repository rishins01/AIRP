from flask import Flask,render_template,redirect,url_for,request
from back.backend import *



def init_app():
    app=Flask(__name__)
    app.debug=True
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:<pwd>@localhost/AIRP"   #"sqlite:///users.db"

    app.secret_key = 'your_secret_key_here' 

    app.app_context().push()
    db.init_app(app)
    print("Application Started...")
    return app

app=init_app()

from back.controllers import *
if __name__ == "__main__":
    app.run(debug=True)