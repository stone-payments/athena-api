from flask.views import MethodView
from app.common.mongo import Mongraph
from app.common.config import *

db = Mongraph(db_name=db_name, db_url=db_url, username=username,
              password=password, auth_mechanism=auth_mechanism).connect()


class BaseDb(MethodView):

    def __init__(self, db=db):
        self.db = db
