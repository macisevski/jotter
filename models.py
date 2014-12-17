"""Define data modela
"""

import datetime
from jotter import db


class Post(db.Document):
    created_at = db.DateTimeField(default=datetime.datetime.now(),
                                  required=True
                                  )
    environment = db.StringField(max_length=255, required=False)
    branch = db.StringField(max_length=255, required=False)
    build = db.StringField(max_length=255, required=False)
    suite = db.StringField(max_length=255, required=False)
    scenario = db.StringField(max_length=255, required=False)
    result = db.StringField(max_length=255, required=False)
    message = db.StringField(max_length=255, required=False)
    run_time = db.StringField(max_length=255, required=False)
    used_memory_delta = db.DecimalField(required=False)
    user_cpu_delta = db.DecimalField(required=False)
    report = db.StringField(required=False)

    meta = {'allow_inheritance': True, 'indexes': ['-created_at'],
            'ordering': ['-created_at']
            }

    def find(self, report):
	print type(db)
	post = self.objects.filter(report=report)[0]
	return post

