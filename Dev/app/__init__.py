from flask import Flask
import requests
import os

from views import index, test, data


app = Flask(__name__)
app.secret_key = os.urandom(12).hex()

with app.app_context():   
    app.register_blueprint(index.v)
    app.register_blueprint(test.v)
    app.register_blueprint(data.v)

if __name__ == "__main__":
    
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
        )

