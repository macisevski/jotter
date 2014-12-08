from flask import Flask
from flask.ext.mongoengine import MongoEngine

import datetime

app = Flask(__name__)
app.config["MONGODB_SETTINGS"] = {'DB': "jotter"}
app.config["SECRET_KEY"] = "backtoussr"
app.config["UPLOAD_FOLDER"] = "uploads/"

db = MongoEngine(app)

if __name__ == '__main__':
    app.run()


@app.context_processor
def utility_processor():
    def format_runtime(runtime):
        if runtime:
            runtime = str(datetime.timedelta(seconds=int(float(runtime))))
        return runtime

    def format_result(result):
        if result:
            result = 'Passed' if result == '1' else 'Failed'
        return result
    return dict(format_runtime=format_runtime, format_result=format_result)


def register_blueprints(app):
    # Prevent circular imports
    from jotter.views import posts
    app.register_blueprint(posts)

register_blueprints(app)
