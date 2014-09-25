from flask import Flask
from flask.ext.mongoengine import MongoEngine

app = Flask(__name__)
app.config["MONGODB_SETTINGS"] = {'DB': "jotter"}
app.config["SECRET_KEY"] = "backtoussr"

db = MongoEngine(app)

if __name__ == '__main__':
    app.run()


def register_blueprints(app):
    # Prevent circular imports
    from jotter.views import posts
    app.register_blueprint(posts)

register_blueprints(app)
