"""Generate a view as well as handle POST requests
"""

from flask import Blueprint, request, render_template, jsonify, redirect
from flask import send_from_directory, url_for
from flask.views import MethodView
from jotter.models import Post
from jotter import app

import datetime
import os
import json
import base64

posts = Blueprint('posts', __name__, template_folder='templates')
di = {'scenario': '', 'environment': '', 'branch': '', 'build': '', 'suite': ''}


class ListView(MethodView):
    def get(self, *args, **kwargs):
        print request.args.keys()
        for key, value in request.args.iteritems():
            di[key] = value
        # posts = Post.objects(__raw__=di)
        posts = Post.objects.filter(scenario__icontains=di["scenario"])
        posts = Post.objects.filter(environment__icontains=di["environment"])
        posts = Post.objects.filter(branch__icontains=di["branch"])
        posts = Post.objects.filter(build__icontains=di["build"])
        posts = Post.objects.filter(suite__icontains=di["suite"])
        return render_template('posts/list.html', posts=posts)


@app.route("/jot", methods=["GET", "POST"])
def add_post():
    try:
        data = json.loads(request.get_data())
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
        post.report = data['report']
        post.save()
        r = post.report
    except Exception, e:
        print e
        r = {"Error": str(e)}
    finally:
        return jsonify({"r":r})


@app.route("/upload", methods=["POST", "GET"])
def upload():
        fname = request.headers['name']
        print fname
        data = request.get_data()
        print 1
        fdata = base64.b64decode(data)
        f = open(os.path.join(app.config["UPLOAD_FOLDER"], fname), 'w')
        f.write(fdata)
        f.close()
        ret = redirect(url_for('uploaded_file', filename=fname))
        return ret


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

posts.add_url_rule('/', view_func=ListView.as_view('ListView'))
