from pymongo import MongoClient
import urllib.parse


class Mongraph(object):
    def __init__(self, db_name, db_url, username, password, auth_mechanism):
        self.auth_mechanism = auth_mechanism
        self.password = password
        self.username = username
        self.db_name = db_name
        self.db_url = db_url

    def connect(self):
        if self.db_url is None:
            raise NameError("DB URL is not Defined")
        if self.username and self.password:
            password = urllib.parse.quote_plus(self.password)
            username = urllib.parse.quote_plus(self.username)
            client = MongoClient('mongodb://%s:%s@%s/%s?authSource=%s' %
                                 (username, password, self.db_url, self.db_name, self.db_name))
        else:
            client = MongoClient('mongodb://%s' % self.db_url)
        _db = client[self.db_name]
        return _db
