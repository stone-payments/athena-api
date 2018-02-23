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