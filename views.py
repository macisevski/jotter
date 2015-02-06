"""Generate a view as well as handle POST requests
"""

import jotter
import jotter.models
import flask
import flask.views
import datetime
import os
import json

posts = flask.Blueprint('posts', __name__, template_folder='templates')


class ListView(flask.views.MethodView):
    def __init__(self):
        self.di = {'scenario': '', 'environment': '', 'branch': '',
                   'build': '', 'suite': ''}

    def get(self, *args, **kwargs):
        print flask.request.args.keys()
        for key, value in flask.request.args.iteritems():
            self.di[key] = value
        # posts = Post.objects(__raw__=di)
        print jotter.models.Post.objects.count()
        posts = jotter.models.Post.objects.filter(scenario__icontains=self.di["scenario"])
        posts = jotter.models.Post.objects.filter(environment__icontains=self.di["environment"])
        posts = jotter.models.Post.objects.filter(branch__icontains=self.di["branch"])
        posts = jotter.models.Post.objects.filter(build__icontains=self.di["build"])
        posts = jotter.models.Post.objects.filter(suite__icontains=self.di["suite"])
        print posts.count()
        return flask.render_template('posts/list.html', posts=posts)


@jotter.app.route("/jot", methods=["GET", "POST"])
def add_post():
    try:
        data = json.loads(flask.request.get_data())
        post = jotter.models.Post()
        post.created_at = datetime.datetime.now()
        post.environment = data.get('environment', '')
        post.branch = data.get('branch', '')
        post.build = data.get('build', '')
        post.suite = data.get('suite', '')
        post.scenario = data.get('scenario', '')
        post.result = data.get('result', '')
        post.message = data.get('message', '')
        post.run_time = data.get('run_time', '')
        post.used_memory_delta = data.get('used_memory_delta', -1)
        post.user_cpu_delta = data.get('user_cpu_delta', -1)
        post.report = data.get('report', '')
        post.save()
        ret = post
    except Exception, error:
        print error
        ret = {"Error": str(error)}
    finally:
        return flask.jsonify({"posted": ret})


@jotter.app.route("/upload", methods=["POST", "GET"])
def upload():
    fname = flask.request.headers['name']
    data = flask.request.get_data()
    f = open(os.path.join(jotter.app.config["UPLOAD_FOLDER"], fname), 'w')
    f.write(data)
    f.close()
    return flask.jsonify({'uploaded_file': fname})


@jotter.app.route("/update", methods=["PUT"])
def update_post():
    data = json.loads(flask.request.get_data())
    post = jotter.models.Post.objects.filter(created_at=data['created_at'])[0]
    post.message = data['message']
    post.save()
    return flask.jsonify({'message': data['message']})


@jotter.app.route("/uploads/<filename>")
def uploaded_file(filename):
    return flask.send_from_directory(jotter.app.config["UPLOAD_FOLDER"], filename)

posts.add_url_rule('/', view_func=ListView.as_view('ListView'))
