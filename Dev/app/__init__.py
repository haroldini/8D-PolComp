from flask import Flask
import requests

from views import index, test, data


app = Flask(__name__)

with app.app_context():   
    app.register_blueprint(index.v)
    app.register_blueprint(test.v)
    app.register_blueprint(data.v)

if __name__ == "__main__":
    
    app.run(debug=True)

