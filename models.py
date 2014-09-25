"""Define data modela
"""

import datetime
from jotter import db


class Post(db.Document):
    created_at = db.DateTimeField(
        default=datetime.datetime.now(),
        required=True)
    environment = db.StringField(max_length=255, required=True)
    branch = db.StringField(max_length=255, required=True)
    build = db.StringField(max_length=255, required=True)
    suite = db.StringField(max_length=255, required=True)
    scenario = db.StringField(max_length=255, required=True)
    result = db.StringField(max_length=255, required=True)
    message = db.StringField(max_length=255, required=True)
    run_time = db.StringField(max_length=255, required=True)
    used_memory_delta = db.DecimalField(required=True)
    user_cpu_delta = db.DecimalField(required=True)

    meta = {'allow_inheritance': True, 'indexes': ['-created_at'],
            'ordering': ['-created_at']}
