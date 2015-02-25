"""Generate a view as well as handle POST requests
"""

import jotter
import jotter.models
import flask
import flask.views
import datetime
import os
import json
import io
import lxml.etree
import zipfile
import zlib

posts = flask.Blueprint('posts', __name__, template_folder='templates')
details = flask.Blueprint('details', __name__, template_folder='templates')


class ListView(flask.views.MethodView):
    """Pluggable (class based) view
        good in cases when new views need to be inherited from a base view to
        avoid code duplication
    """

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


class DetailsView(flask.views.MethodView):

    def __init__(self):
        self.di = {}
        self.tags = ['TestCase', 'BasicSequence', 'TestStep', 'AbstractStepLog',
                     'ProcedureLog']

    def get(self, filename):
        zfname = filename + '.zip'
        with zipfile.ZipFile('uploads/'+ zfname) as book:
            a = self.get_text(book.read(filename))

        return flask.render_template('details/table.html', details=a)

    def get_text(self, xml):
        r = []
        a = lxml.etree.parse(io.BytesIO(xml))
        t = a.xpath("BaseTestLog/BaseTestLog/AbstractStepLog/BaseTestLog[@name] |" +
                    "BaseTestLog/BaseTestLog/AbstractStepLog/BaseTestLog/BasicSequenceLog/*[@name] |" +
                    "BaseTestLog/BaseTestLog/AbstractStepLog/BaseTestLog/BasicSequenceLog[not(@name)]/AbstractStepLog[not(@name)]/ProcedureLog[@name]/AbstractStepLog[@name] |" +
                    "BaseTestLog/BaseTestLog/AbstractStepLog/BaseTestLog/BasicSequenceLog[TestStep]/AbstractStepLog[not(@name)]/*[@name]")
        for i in t:
            r.append({'name': i.attrib.get('name', ''), 'tag': i.tag})
        #for ac, elem in lxml.etree.iterparse(io.BytesIO(xml)):
        #    di = {}
        #    tag = elem.tag
        #    if not tag in self.tags:
        #        continue
        #    name = elem.attrib.get('name', None)
        #    if not name:
        #        continue
        #    parent = elem.getparent()
        #    if parent:
        #        parent_tag = parent.tag
        #        testtype = parent.attrib.get('testtype', None)
        #    if testtype == 'teststep':
        #        r.append({'name': name, 'tag': tag})
        #    if parent_tag == 'AbstractStepLog':
        #        r.append({'name': name, 'tag': tag})
        return r


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
        post.customstream = data.get('customstream', '')
        post.fixhub = data.get('fixhub', '')
        post.tradelog = data.get('tradelog', '')
        post.pulse = data.get('pulse', '')
        post.omflexnew = data.get('omflexnew', '')
        post.fixflex = data.get('fixflex', '')
        post.fixbrk = data.get('fixbrk', '')
        print post
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
    fpath = os.path.join(jotter.app.config["UPLOAD_FOLDER"]. fname)
    zfpath = fpath + '.zip'
    data = flask.request.get_data()
    with open(fpath, 'w') as f:
        f.write(data)
    with zipfile.ZipFile(zfpath, 'w') as zf:
        zf.write(fpath)
    os.remove(fpath)

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
    zfname = filename + '.zip'

    return flask.send_from_directory(jotter.app.config["UPLOAD_FOLDER"], zfname)


# Class base views cannot be decorated, so map ListView to url this way
posts.add_url_rule('/', view_func=ListView.as_view('posts'))
details.add_url_rule('/details/<filename>', view_func=DetailsView.as_view('details'))
