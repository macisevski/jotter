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


class ListView(MethodView):
    def __init__(self):
        self.di = {'scenario': '', 'environment': '', 'branch': '',
                   'build': '', 'suite': ''}

    def get(self, *args, **kwargs):
        print request.args.keys()
        for key, value in request.args.iteritems():
            self.di[key] = value
        # posts = Post.objects(__raw__=di)
        print Post.objects.count()
        posts = Post.objects.filter(scenario__icontains=self.di["scenario"])
        posts = Post.objects.filter(environment__icontains=self.di["environment"])
        posts = Post.objects.filter(branch__icontains=self.di["branch"])
        posts = Post.objects.filter(build__icontains=self.di["build"])
        posts = Post.objects.filter(suite__icontains=self.di["suite"])
        print posts.count()
        return render_template('posts/list.html', posts=posts)


@app.route("/jot", methods=["GET", "POST"])
def add_post():
    try:
        data = json.loads(request.get_data())
        post = Post()
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
	r = post
    except Exception, e:
        print e
        r = {"Error": str(e)}
    finally:
        return jsonify({"posted":r})


@app.route("/upload", methods=["POST", "GET"])
def upload():
	import urllib
        fname = request.headers['name']
        data = request.get_data()
        f = open(os.path.join(app.config["UPLOAD_FOLDER"], fname), 'w')
        f.write(data)
        f.close()
        return jsonify({'uploaded_file': fname})

@app.route("/update", methods=["PUT"])
def update_post():
	data = json.loads(request.get_data())
	post = Post.objects.filter(created_at=data['created_at'])[0]
	post.message = data['message']
	post.save()
	return jsonify({'message': data['message']})

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

posts.add_url_rule('/', view_func=ListView.as_view('ListView'))
