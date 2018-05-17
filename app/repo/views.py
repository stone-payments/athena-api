from flask import jsonify
from app.common.client import *
from app.common.module import *
from app.common.db import BaseDb


class RepoName(BaseDb):

    def get(self):
        return name_and_org_regex_search(self.db, 'Repo', 'repoName')


class RepoLanguages(BaseDb):

    def get(self):
        name = request.args.get("name")
        org = str(request.args.get("org"))
        query = {'org': org, 'repoName': name}
        projection = {"languages": 1, "_id": 0}
        result = query_find_to_dictionary(self.db, 'Repo', query, projection)
        if not result:
            return json.dumps([{'response': 404}])
        result = (result[0]['languages'])
        result = sorted(result, key=itemgetter('size'), reverse=True)
        return jsonify(result)


class RepoCommits(BaseDb):

    def get(self):
        name = request.args.get("name")
        org = request.args.get("org")
        start_date = start_day_string_time()
        end_date = end_date_string_time()
        query = [{'$match': {'org': org, 'repo_name': name, 'committed_date': {'$gte': start_date, '$lt': end_date}}},
                 {'$group': {
                     '_id': {
                         'year': {'$year': "$committed_date"},
                         'month': {'$month': "$committed_date"},
                         'day': {'$dayOfMonth': "$committed_date"},
                     },
                     'count': {'$sum': 1}
                 }},
                 {'$project': {'_id': 0, "year": "$_id.year", "month": "$_id.month", "day": "$_id.day", 'count': 1}}
                 ]
        delta = end_date - start_date
        commits_count_list = query_aggregate_to_dictionary(self.db, 'Commit', query)
        print(commits_count_list)
        for commit_count in commits_count_list:
            commit_count['date'] = dt.datetime(commit_count['year'], commit_count['month'], commit_count['day'], 0, 0)
        days = [start_date + dt.timedelta(days=i) for i in range(delta.days + 1)]
        lst = [fill_all_dates(day, commits_count_list) for day in days]
        return jsonify(lst)


class RepoMembers(BaseDb):

    def get(self):
        name = request.args.get("name")
        org = str(request.args.get("org"))
        query = {'org': org, 'repoName': name, 'author': {'$ne': None}}
        projection = {'_id': 0, 'author': 1}
        query_result = query_find(self.db, 'Commit', query, projection).distinct("author")
        query_result = sorted(query_result, key=lambda x: x.lower(), reverse=False)
        return jsonify(query_result)


class RepoBestPratices(BaseDb):

    def get(self):
        name = request.args.get("name")
        org = str(request.args.get("org"))
        query = [{'$match': {'org': org, 'repo_name': name}},
                 {'$project': {'_id': 0, 'contributing': 1, 'readme': 1, 'readme_language': 1, 'license_type': 1,
                               'opensource': {'$slice': ["$open_source.status", -1]}}},
                 {'$unwind': "$opensource"},
                 ]
        query_result = query_aggregate_to_dictionary(self.db, 'Repo', query)
        if not query_result:
            return jsonify({'_id': '-', 'contributing': '-', 'readme': '-', 'readme_language': '-', 'license_type': '-',
                           'opensource': '-'})
        return jsonify(query_result[0])


class RepoIssues(BaseDb):

    def get(self):
        name = request.args.get("name")
        org = request.args.get("org")
        start_date = dt.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
        end_date = dt.datetime.strptime(request.args.get("endDate"), '%Y-%m-%d') + dt.timedelta(seconds=86399)
        delta = end_date - start_date
        query_created = [
            {'$match': {'org': org, 'repoName': name, 'createdAt': {'$gte': start_date, '$lte': end_date}}},
            {'$group': {
                '_id': {
                    'year': {'$year': "$createdAt"},
                    'month': {'$month': "$createdAt"},
                    'day': {'$dayOfMonth': "$createdAt"},
                },
                'count': {'$sum': 1}
            }},
            {'$project': {'_id': 0, "year": "$_id.year", "month": "$_id.month", "day": "$_id.day", 'count': 1}}
            ]
        query_closed = [{'$match': {'org': org, 'repoName': name, 'closedAt': {'$gte': start_date, '$lte': end_date}}},
                        {'$group': {
                            '_id': {
                                'year': {'$year': "$closedAt"},
                                'month': {'$month': "$closedAt"},
                                'day': {'$dayOfMonth': "$closedAt"},
                            },
                            'count': {'$sum': 1}
                        }},
                        {'$project': {'_id': 0, "year": "$_id.year", "month": "$_id.month", "day": "$_id.day",
                                      'count': 1}}
                        ]
        created_issues_list = process_data(self.db, 'Issue', query_created, delta, start_date)
        created_issues_list = accumulator(created_issues_list)
        closed_issues_list = process_data(self.db, 'Issue', query_closed, delta, start_date)
        closed_issues_list = accumulator(closed_issues_list)
        response = [closed_issues_list, created_issues_list]
        return jsonify(response)
