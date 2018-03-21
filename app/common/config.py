import os

db_url = os.getenv("MONGODB_URL")
username = os.getenv("MONGODB_USER", False)
password = os.getenv("MONGODB_PASS", False)
db_name = os.getenv("DB_NAME")
auth_mechanism = os.getenv("AUTH_MECHANISM")
since_hour_delta = os.getenv("SINCE_HOUR_DELTA", -2)
