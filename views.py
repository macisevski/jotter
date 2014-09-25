"""Generate a view as well as handle POST requests
"""

from flask import Blueprint, request, render_template, jsonify
from flask.views import MethodView
from jotter.models import Post
from jotter import app

import datetime

posts = Blueprint('posts', __name__, template_folder='templates')


class ListView(MethodView):
    def get(self):
        posts = Post.objects.limit(10)
        return render_template('posts/list.html', posts=posts)


@app.route("/jot", methods=["GET", "POST"])
def add_post():
    try:
        data = request.get_json()
        post = Post()
        post.created_at = datetime.datetime.now()
        post.environment = data['environment']
        post.branch = data['branch']
        post.build = data['build']
        post.suite = data['suite']
        post.scenario = data['scenario']
        post.result = data['result']
        post.message = data['message']
        post.run_time = data['run_time']
        post.used_memory_delta = data['used_memory_delta']
        post.user_cpu_delta = data['user_cpu_delta']
        post.save()
        ret = request.get_json(force=True)
    except Exception, e:
        ret = {"Error": str(e)}
    finally:
        return jsonify(ret)

posts.add_url_rule('/', view_func=ListView.as_view('list'))
