import datetime as dt

from flask import jsonify, request

from app.common.client import query_find_to_dictionary, query_aggregate_to_dictionary, query_last_document_limit_2, \
    query_find_to_dictionary_distinct
from app.common.config import since_hour_delta
from app.common.db import BaseDb
from app.common.module import last_updated_at, start_day_string_time, end_date_string_time, fill_all_dates, \
    process_data, \
    utc_time_datetime_format, name_regex_search


class UserAvatar(BaseDb):

    def get(self):
        name = request.args.get("login")
        query = {'login': name}
        projection = {'_id': 0, 'collection_name': 0}
        query_result = query_find_to_dictionary(self.db, 'Dev', query, projection)
        if not query_result:
            return jsonify([{'response': 404}])
        query_result[0]['db_last_updated'] = last_updated_at(query_result[0]['db_last_updated'])
        query_result[0]['response'] = 200
        return jsonify(query_result)


class UserCommit(BaseDb):

    def get(self):
        name = request.args.get("name")
        start_date = start_day_string_time()
        end_date = end_date_string_time()
        query = [{'$match': {'author': name, 'committed_date': {'$gte': start_date, '$lt': end_date}}},
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
        commits_count_list = self.db.Commit.aggregate(query)
        commits_count_list = [dict(i) for i in commits_count_list]
        for commit_count in commits_count_list:
            commit_count['date'] = dt.datetime(commit_count['year'], commit_count['month'], commit_count['day'], 0, 0)
        days = [start_date + dt.timedelta(days=i) for i in range(delta.days + 1)]
        lst = [fill_all_dates(day, commits_count_list) for day in days]
        return jsonify(lst)


class UserContributedRepo(BaseDb):

    def get(self):
        name = request.args.get("name")
        start_date = start_day_string_time()
        end_date = end_date_string_time()
        query = [
            {'$match': {'author': name, 'committedDate': {'$gte': start_date, '$lte': end_date}}},
            {
                '$group':
                    {
                        '_id': {'repoName': "$repoName",
                                'org': "$org",

                                }
                    }
            },
            {'$project': {'_id': 0, "org": "$_id.org", 'repoName': '$_id.repoName'}}
        ]
        query_result = query_aggregate_to_dictionary(self.db, 'Commit', query)
        query_result = sorted(query_result, key=lambda x: x['repoName'].lower(), reverse=False)
        return jsonify(query_result)


class UserStats(BaseDb):

    def get(self):
        name = request.args.get("name")
        start_date = start_day_string_time()
        end_date = end_date_string_time()
        delta = end_date - start_date
        query_addttions = [
            {'$match': {'author': name, 'committedDate': {'$gte': start_date, '$lte': end_date}}},
            {
                '$group':
                    {
                        '_id': {'author': "$author",
                                'year': {'$year': "$committedDate"},
                                'month': {'$month': "$committedDate"},
                                'day': {'$dayOfMonth': "$committedDate"},
                                },
                        'totalAmount': {'$sum': '$additions'}
                    }
            },
            {'$project': {'_id': 0, "year": "$_id.year", "month": "$_id.month", "day": "$_id.day",
                          'author': '$_id.author',
                          'count': '$totalAmount'}}
        ]
        query_deletions = [
            {'$match': {'author': name, 'committedDate': {'$gte': start_date, '$lte': end_date}}},
            {
                '$group':
                    {
                        '_id': {'author': "$author",
                                'year': {'$year': "$committedDate"},
                                'month': {'$month': "$committedDate"},
                                'day': {'$dayOfMonth': "$committedDate"},
                                },
                        'totalAmount': {'$sum': '$deletions'}
                    }
            },
            {'$project': {'_id': 0, "year": "$_id.year", "month": "$_id.month", "day": "$_id.day",
                          'author': '$_id.author',
                          'count': '$totalAmount'}}
        ]
        additions_list = process_data(self.db, 'Commit', query_addttions, delta, start_date)
        deletions_list = process_data(self.db, 'Commit', query_deletions, delta, start_date)
        response = [additions_list, deletions_list]
        return jsonify(response)


class UserTeam(BaseDb):

    def get(self):
        name = request.args.get("name")
        query = [{'$lookup': {
            'from': 'Teams', 'localField': 'to', 'foreignField': '_id', 'as': 'Team'}}
            , {'$lookup': {
                'from': 'Dev', 'localField': 'from', 'foreignField': '_id', 'as': 'Dev'}},
            {
                '$match':
                    {"Dev.0.login": name, 'type': 'dev_to_team', 'data.db_last_updated':
                        {'$gte': utc_time_datetime_format(since_hour_delta)}}
            },
            {'$sort': {'Team.teamName': 1}},
            {'$project': {'_id': 0, "Team.teamName": 1, 'Team.org': 1, 'Team.slug': 1}}
        ]
        query_result = query_aggregate_to_dictionary(self.db, 'edges', query)
        query_result = [x['Team'][0] for x in query_result]
        query_result = sorted(query_result, key=lambda x: x['teamName'].lower(), reverse=False)
        return jsonify(query_result)


class UserLogin(BaseDb):

    def get(self):
        return name_regex_search(self.db, 'Dev', 'login')


class UserNewWork(BaseDb):

    def get(self):
        name = request.args.get("name")
        start_date = start_day_string_time()
        end_date = end_date_string_time()
        query = [{'$match': {'author': name, 'committed_date': {'$gte': start_date, '$lt': end_date}}},
                 {'$group': {
                     '_id': {'author': "$author"
                             },
                     'additions': {'$sum': '$additions'},
                     'deletions': {'$sum': '$deletions'},
                     'commits': {'$sum': 1},
                 }},
                 {'$project': {'_id': 0, 'author': '$_id.author',
                               'additions': '$additions', 'deletions': '$deletions', 'commits': '$commits'}}
                 ]
        query2 = [{'$match': {'author': name, 'committed_date': {'$gte': start_date, '$lt': end_date}}},
                  {'$group': {
                      '_id': {
                          'year': {'$year': "$committed_date"},
                          'month': {'$month': "$committed_date"},
                          'day': {'$dayOfMonth': "$committed_date"},
                      }
                  }}
                  ]

        commits_count_list = query_aggregate_to_dictionary(self.db, 'Commit', query)
        total_days_count = len(query_aggregate_to_dictionary(self.db, 'Commit', query2))
        all_days = [start_date + dt.timedelta(days=x) for x in range((end_date - start_date).days + 1)]
        working_days = sum(1 for d in all_days if d.weekday() < 5)
        if not commits_count_list:
            return jsonify({'data': [-100, 0, 0, name]})
        commits_ratio = int((total_days_count / working_days - 0.5) * 2 * 100)
        if commits_ratio >= 100:
            commits_ratio = 100
        value_result = commits_count_list[0]['additions'] - commits_count_list[0]['deletions']
        if value_result >= 0:
            addittions_deletions_ratio = int((value_result / commits_count_list[0]['additions'] - 0.5) * 200)
        else:
            addittions_deletions_ratio = -100
        return jsonify({'data': [commits_ratio, addittions_deletions_ratio, commits_count_list[0]['commits'], name]})


class UserLastCommits(BaseDb):

    def get(self):
        name = request.args.get("name")
        query = {"author": name}
        projection = {"_id": 0, "repo_name": 1, "author": 1, "committed_date": 1, 'message_head_line': 1,
                      'branch_name':  {"$slice": -1}}
        org_last_commit_list = query_last_document_limit_2(self.db, query, "Commit", projection, "committed_date", 6)
        for org_last_commit in org_last_commit_list:
            try:
                org_last_commit['branch_name'] = org_last_commit["branch_name"][0]
            except IndexError:
                org_last_commit['branch_name'] = None
            org_last_commit['day'] = org_last_commit['committed_date'].strftime('%d')
            org_last_commit['month'] = org_last_commit['committed_date'].strftime('%b')
        return jsonify(org_last_commit_list)


class UserWorkedRepository(BaseDb):

    def get(self):
        name = request.args.get("name")
        start_date = start_day_string_time()
        end_date = end_date_string_time()
        repo_id = query_find_to_dictionary_distinct(self.db, 'Commit', 'repository_id',
                                                    {'committed_date': {'$gte': start_date, '$lt': end_date},
                                                     'author': name})
        total_commits = [{'$match': {'committed_date': {'$gte': start_date, '$lt': end_date},
                                     'repository_id': {'$in': repo_id}}},
                 {'$group': {
                     '_id': {
                         'repo_name': "$repo_name",
                     },
                     'total': {'$sum': 1}
                 }},
                 {'$sort': {'_id.repo_name': -1}},
                 {'$project': {'_id': 0,  "repo_name": "$_id.repo_name", 'total': 1}},
                 ]
        total_commits_count = query_aggregate_to_dictionary(self.db, 'Commit', total_commits)
        user_commits = [{'$match': {'committed_date': {'$gte': start_date, '$lt': end_date}, 'author': name,
                                    'repository_id': {'$in': repo_id}}},
                 {'$group': {
                     '_id': {
                         'repo_name': "$repo_name",
                         'author':'$author'
                     },
                     'user_total': {'$sum': 1}
                 }},
                 {'$sort': {'_id.repo_name': -1}},
                 {'$project': {'_id': 0, "author": "$_id.author", "repo_name": "$_id.repo_name", 'user_total': 1}},
                 ]
        user_commits_count = query_aggregate_to_dictionary(self.db, 'Commit', user_commits)
        response = [{'name': k1['repo_name'], 'value': int(k2['user_total']/k1['total']*100)} for k1, k2 in zip(total_commits_count, user_commits_count)]
        response = sorted(response, key=lambda x: x['value'], reverse=True)
        return jsonify(response)
