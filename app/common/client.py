from pymongo import DESCENDING

def query_find_to_dictionary(db, collection, query, projection):
    query_result = db[collection].find(query, projection)
    return [dict(i) for i in query_result]


def query_find(db, collection, query, projection):
    return db[collection].find(query, projection)


def query_aggregate_to_dictionary(db, collection, query):
    query_result = db[collection].aggregate(query)
    return [dict(i) for i in query_result]


def query_find_to_dictionary_distinct(db, collection, distinct_key, query):
    return db[collection].distinct(distinct_key, query)


def query_count(db, collection, query):
    return db[collection].count(query)


def query_last_document_limit_(db, org, collection, projection, sort_document, limit):
    query_result = db[collection].find({"org": org}, projection).sort([(sort_document, DESCENDING)]).limit(limit)
    return [dict(i) for i in query_result]
