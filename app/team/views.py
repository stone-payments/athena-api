from flask import jsonify
from app.common.client import *
from app.common.module import *
from app.common.db import BaseDb


class CheckWithExist(BaseDb):

    def get(self):
        org = request.args.get("org")
        name = request.args.get("name")
        query = {'org': org, 'slug': name, 'db_last_updated': {'$gte': utc_time_datetime_format(-1)}}
        projection = {'_id': 1}
        query_result = query_find_to_dictionary(self.db, 'Teams', query, projection)
        if not query_result:
            return jsonify({'response': 404})
        return jsonify({'response': 200})


class TeamLanguages(BaseDb):

    def get(self):
        org = request.args.get("org")
        name = request.args.get("name")
        id_team = query_find_to_dictionary(self.db, 'Teams',
                                           {'slug': name, 'org': org,
                                            'db_last_updated': {'$gte': utc_time_datetime_format(-1)}}, {'_id': '_id'})
        repo_id_list = query_find_to_dictionary_distinct(self.db, 'edges', 'from',
                                                         {'to': id_team[0]['_id'], "type": 'repo_to_team',
                                                          'data.db_last_updated': {'$gte': utc_time_datetime_format(-1)}})
        query = [
            {
                '$match':
                    {'_id': {'$in': repo_id_list}}},

            {"$unwind": "$languages"},

            {'$group': {
                '_id': {
                    'language': "$languages.language",
                },
                'count': {'$sum': '$languages.size'}
            }},
            {'$sort': {'count': -1}},
            {'$limit': 12},
            {'$project': {"language": "$_id.language", "_id": 0, 'count': 1}}
        ]
        query_result = self.db.Repo.aggregate(query)
        readme_status_list = [dict(i) for i in query_result]
        soma = sum([readme_status['count'] for readme_status in readme_status_list])
        for readme_status in readme_status_list:
            if readme_status['language'] is None:
                readme_status['language'] = 'None'
            readme_status['count'] = round(int(readme_status['count']) / soma * 100, 1)
        return jsonify(readme_status_list)


class TeamOpenSource(BaseDb):

    def get(self):
        org = request.args.get("org")
        name = request.args.get("name")
        id_team = query_find_to_dictionary(self.db, 'Teams',
                                           {'slug': name, 'org': org,
                                            'db_last_updated': {'$gte': utc_time_datetime_format(-1)}}, {'_id': '_id'})
        repo_id_list = query_find_to_dictionary_distinct(self.db, 'edges', 'from',
                                                         {'to': id_team[0]['_id'], "type": 'repo_to_team',
                                                          'data.db_last_updated': {'$gte': utc_time_datetime_format(-1)}})
        query = [
            {
                '$match':
                    {'_id': {'$in': repo_id_list}}},
            {'$group': {
                '_id': {
                    'status': "$openSource",
                },
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id.status': -1}},
            {'$project': {"status": "$_id.status", "_id": 0, 'count': 1}}
        ]
        query_result = self.db.Repo.aggregate(query)
        if not query_result:
            return json.dumps([{'response': 404}])
        readme_status_list = [dict(i) for i in query_result]
        soma = sum([readme_status['count'] for readme_status in readme_status_list])
        for readme_status in readme_status_list:
            readme_status['count'] = round(int(readme_status['count']) / soma * 100, 1)
        if len(readme_status_list) < 2:
            find_key(readme_status_list, [True, False])
        readme_status_list = sorted(readme_status_list, key=itemgetter('status'), reverse=False)
        return jsonify(readme_status_list)


class TeamReadme(BaseDb):

    def get(self):
        org = request.args.get("org")
        name = request.args.get("name")
        id_team = query_find_to_dictionary(self.db, 'Teams',
                                           {'slug': name, 'org': org,
                                            'db_last_updated': {'$gte': utc_time_datetime_format(-1)}}, {'_id': '_id'})
        repo_id_list = query_find_to_dictionary_distinct(self.db, 'edges', 'from',
                                                         {'to': id_team[0]['_id'], "type": 'repo_to_team',
                                                          'data.db_last_updated': {'$gte': utc_time_datetime_format(-1)}})
        query = [
            {
                '$match':
                    {'_id': {'$in': repo_id_list}}},
            {'$group': {
                '_id': {
                    'status': "$readme",
                },
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id.status': -1}},
            {'$project': {"status": "$_id.status", "_id": 0, 'count': 1}}
        ]
        query_result = self.db.Repo.aggregate(query)
        readme_status_list = [dict(i) for i in query_result]
        soma = sum([readme_status['count'] for readme_status in readme_status_list])
        for readme_status in readme_status_list:
            if readme_status['status'] is None:
                readme_status['status'] = 'None'
            readme_status['count'] = round(int(readme_status['count']) / soma * 100, 1)
        if len(readme_status_list) < 3:
            find_key(readme_status_list, ['None', 'Poor', 'OK'])
        readme_status_list = sorted(readme_status_list, key=itemgetter('status'), reverse=True)
        return jsonify(readme_status_list)


class TeamLicense(BaseDb):

    def get(self):
        org = request.args.get("org")
        name = request.args.get("name")
        id_team = query_find_to_dictionary(self.db, 'Teams',
                                           {'slug': name, 'org': org,
                                            'db_last_updated': {'$gte': utc_time_datetime_format(-1)}}, {'_id': '_id'})
        repo_id_list = query_find_to_dictionary_distinct(self.db, 'edges', 'from',
                                                         {'to': id_team[0]['_id'], "type": 'repo_to_team',
                                                          'data.db_last_updated': {'$gte': utc_time_datetime_format(-1)}})
        query = [
            {
                '$match':
                    {'_id': {'$in': repo_id_list}}},
            {'$group': {
                '_id': {
                    'status': "$licenseType",
                },
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id.count': -1}},
            {'$project': {"status": "$_id.status", "_id": 0, 'count': 1}}
        ]
        query_result = self.db.Repo.aggregate(query)
        readme_status_list = [dict(i) for i in query_result]
        if not readme_status_list:
            return jsonify([{'status': 'None', 'count': 100.0}])
        soma = sum([readme_status['count'] for readme_status in readme_status_list])
        for readme_status in readme_status_list:
            if readme_status['status'] is None:
                readme_status['status'] = 'None'
            readme_status['count'] = round(int(readme_status['count']) / soma * 100, 1)
        readme_status_list = sorted(readme_status_list, key=itemgetter('count'), reverse=True)
        return jsonify(readme_status_list)


class TeamRepoMembers(BaseDb):

    def get(self):
        org = request.args.get("org")
        name = request.args.get("name")
        id_team = query_find_to_dictionary(self.db, 'Teams',
                                           {'slug': name, 'org': org,
                                            'db_last_updated': {'$gte': utc_time_datetime_format(-1)}}, {'_id': '_id'})
        dev_id_list = query_find_to_dictionary_distinct(self.db, 'edges', 'from',
                                                         {'to': id_team[0]['_id'], "type": 'dev_to_team',
                                                          'data.db_last_updated': {'$gte': utc_time_datetime_format(-1)}})
        query = [
            {
                '$match':
                    {'_id': {'$in': dev_id_list}}},
            {'$group': {
                '_id': {
                    'member': "$login",
                }
            }},
            {'$sort': {'_id.member': 1}},
            {'$project': {"member": "$_id.member", "_id": 0}}
        ]
        query_result = query_aggregate_to_dictionary(self.db, 'Dev', query)
        return jsonify(query_result)


class TeamName(BaseDb):

    def get(self):
        name = "^" + str(request.args.get("name"))
        org = request.args.get("org")
        compiled_name = re.compile(r'%s' % name, re.I)
        query_result = self.db['Teams'].find({'slug': {'$regex': compiled_name}, 'org': org,
                                              'db_last_updated': {'$gte': utc_time_datetime_format(-1)}},
                                             {'_id': 0, 'slug': 1}).limit(6)
        result = [dict(i) for i in query_result]
        if not query_result:
            return jsonify([{'response': 404}])
        return jsonify(result)


class TeamCommits(BaseDb):

    def get(self):
        name = request.args.get("name")
        org = request.args.get("org")
        start_date = dt.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
        end_date = dt.datetime.strptime(request.args.get("endDate"), '%Y-%m-%d') + dt.timedelta(seconds=86399)
        delta = end_date - start_date
        id_team = query_find_to_dictionary(self.db, 'Teams', {'slug': name, 'org': org}, {'_id': '_id'})
        dev_id_list = query_find_to_dictionary_distinct(self.db, 'edges', 'from',
                                                        {'to': id_team[0]['_id'], "type": 'dev_to_team'})
        query = [{'$match': {'devId': {'$in': dev_id_list},
                             'committedDate': {'$gte': start_date, '$lt': end_date}}},
                 {'$group': {
                     '_id': {
                         'year': {'$year': "$committedDate"},
                         'month': {'$month': "$committedDate"},
                         'day': {'$dayOfMonth': "$committedDate"},
                     },
                     'count': {'$sum': 1}
                 }},
                 {'$project': {"_id": 0, "year": "$_id.year", "month": "$_id.month",
                               "day": "$_id.day",
                               'count': 1}}]
        count_list = query_aggregate_to_dictionary(self.db, 'Commit', query)
        if count_list:
            for count in count_list:
                count['date'] = dt.datetime(count['year'], count['month'], count['day'], 0, 0)
        days = [start_date + dt.timedelta(days=i) for i in range(delta.days + 1)]
        lst = [fill_all_dates(day, count_list) for day in days]
        return jsonify(lst)


class TeamIssues(BaseDb):

    def get(self):
        name = request.args.get("name")
        org = request.args.get("org")
        start_date = dt.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
        end_date = dt.datetime.strptime(request.args.get("endDate"), '%Y-%m-%d') + dt.timedelta(seconds=86399)
        delta = end_date - start_date
        id_team = query_find_to_dictionary(self.db, 'Teams', {'slug': name, 'org': org}, {'_id': '_id'})
        repo_id_list = query_find_to_dictionary_distinct(self.db, 'edges', 'from',
                                                         {'to': id_team[0]['_id'], "type": 'repo_to_team'})
        query_created = [
            {'$match': {'repositoryId': {'$in': repo_id_list},
                        'createdAt': {'$gte': start_date,
                                      '$lt': end_date}}},
            {'$group': {
                '_id': {
                    'year': {'$year': "$createdAt"},
                    'month': {'$month': "$createdAt"},
                    'day': {'$dayOfMonth': "$createdAt"},
                },
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}},
            {'$project': {"_id": 0, "year": "$_id.year", "month": "$_id.month", "day": "$_id.day",
                          'count': 1}}
        ]

        query_closed = [
            {'$match': {'repositoryId': {'$in': repo_id_list},
                        'closedAt': {'$gte': start_date,
                                     '$lt': end_date}}},
            {'$group': {
                '_id': {
                    'year': {'$year': "$closedAt"},
                    'month': {'$month': "$closedAt"},
                    'day': {'$dayOfMonth': "$closedAt"},
                },
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}},
            {'$project': {"_id": 0, "year": "$_id.year", "month": "$_id.month", "day": "$_id.day",
                          'count': 1}}
        ]
        created_issues_list = process_data(self.db, 'Issue', query_created, delta, start_date)
        created_issues_list = accumulator(created_issues_list)
        closed_issues_list = process_data(self.db, 'Issue', query_closed, delta, start_date)
        closed_issues_list = accumulator(closed_issues_list)
        response = [closed_issues_list, created_issues_list]
        return jsonify(response)


class TeamNewWork(BaseDb):

    def get(self):
        org = request.args.get("org")
        name = request.args.get("name")
        start_date = start_day_string_time()
        end_date = end_date_string_time()

        def query_id_name(id_name):
            query_1_2 = [
                {'$match': {'devId': {'$in': id_name},
                            'committedDate': {'$gte': start_date,
                                              '$lt': end_date}}},
                {'$group': {
                    '_id': {'author': "$author"
                            },
                    'additions': {'$sum': '$additions'},
                    'deletions': {'$sum': '$deletions'},
                    'commits': {'$sum': 1},
                }},
                {'$project': {'_id': 0, 'author': '$_id.author',
                              'additions': '$additions', 'deletions': '$deletions', 'commits': '$commits'}},

            ]
            return query_aggregate_to_dictionary(self.db, 'Commit', query_1_2)

        def query_id_name2(id_name):
            query_1_2 = [
                {'$match': {'devId': {'$in': id_name},
                            'committedDate': {'$gte': start_date,
                                              '$lt': end_date}}},
                {'$group': {
                    '_id': {
                        'author': "$author",
                        'year': {'$year': "$committedDate"},
                        'month': {'$month': "$committedDate"},
                        'day': {'$dayOfMonth': "$committedDate"},
                    }
                }},
                {'$group': {
                    '_id': {
                        'author': "$_id.author"
                    },
                    'totalAmount': {'$sum': 1}
                }},
                {'$project': {"_id": 0, 'author': '$_id.author', 'totalAmount': '$totalAmount'}}
            ]
            return query_aggregate_to_dictionary(self.db, 'Commit', query_1_2)

        id_team = query_find_to_dictionary(self.db, 'Teams', {'slug': name, 'org': org}, {'_id': '_id'})
        id_list = query_find_to_dictionary_distinct(self.db, 'edges', 'from',
                                                    {'to': id_team[0]['_id'], "type": 'dev_to_team',
                                                     'data.db_last_updated': {'$gte': utc_time_datetime_format(-1)}})

        commits_count_list = query_id_name(id_list)
        total_days_count = query_id_name2(id_list)
        new_work_list = merge_lists(commits_count_list, total_days_count, 'author')
        all_days = [start_date + dt.timedelta(days=x) for x in range((end_date - start_date).days + 1)]
        working_days = sum(1 for d in all_days if d.weekday() < 5)
        response = []
        for user in new_work_list:
            commits_ratio = int((user['totalAmount'] / working_days - 0.5) * 2 * 100)
            if commits_ratio >= 100:
                commits_ratio = 100
            value_result = user['additions'] - user['deletions']
            if value_result >= 0 and user['additions'] > 0:
                additions_deletions_ratio = int((value_result / user['additions'] - 0.5) * 200)
            else:
                additions_deletions_ratio = -100
            response.append([{'author': user['author'], 'commits': user['commits'], 'additions': user['additions'],
                              'deletions': user['deletions']}, {'x': commits_ratio, 'y': additions_deletions_ratio}])
        if response:
            average_x = int(sum([x[1]['x'] for x in response]) / len(response))
            average_y = int(sum([x[1]['y'] for x in response]) / len(response))
            return jsonify([response, {'x': average_x, 'y': average_y}])
        else:
            return jsonify([response, {'x': 0, 'y': 0}])
