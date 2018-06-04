import datetime as dt
import json
from operator import itemgetter

from flask import request, jsonify

from app.common.client import query_aggregate_to_dictionary, query_last_document_limit_2
from app.common.db import BaseDb
from app.common.module import name_and_org_regex_search, start_day_string_time, end_date_string_time, fill_all_dates, \
    process_data, accumulator


class RepoName(BaseDb):

    def get(self):
        return name_and_org_regex_search(self.db, 'Repo', 'repo_name')


class RepoLanguages(BaseDb):

    def get(self):
        name = request.args.get("name")
        org = str(request.args.get("org"))
        query = [{'$match': {'org': org, 'repo_name': name}},
                 {'$project': {'_id': 0,  "languages":1, "size": 1}},{'$unwind': "$languages"},
                 {'$project': {'_id': 0,  "name": "$languages.language", "value":"$languages.size"}}
                 ]
        result = query_aggregate_to_dictionary(self.db, 'Repo', query)
        if not result:
            return jsonify([{"name": "None", "value": 100}])
        result = sorted(result, key=itemgetter('value'), reverse=True)
        if len(result) > 4:
            new_result = result[:4]
            new_result.append({"name": "Others", "value": round(sum(item['value'] for item in result[4:]), 2)})
            return jsonify(new_result)
        return jsonify(result[:4])


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
        for commit_count in commits_count_list:
            commit_count['date'] = dt.datetime(commit_count['year'], commit_count['month'], commit_count['day'], 0, 0)
        days = [start_date + dt.timedelta(days=i) for i in range(delta.days + 1)]
        lst = [fill_all_dates(day, commits_count_list) for day in days]
        return jsonify(lst)


class RepoMembers(BaseDb):

    def get(self):
        name = request.args.get("name")
        org = request.args.get("org")
        start_date = start_day_string_time()
        end_date = end_date_string_time()
        user_commits = [{'$match': {'committed_date': {'$gte': start_date, '$lt': end_date}, 'repo_name': name,
                                    'org': org}},
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
        total = sum(x["user_total"] for x in user_commits_count)
        response = [{'name': k1['author'], 'value': int(k1['user_total']/total*100)} for k1 in user_commits_count]
        response = sorted(response, key=lambda x: x['value'], reverse=True)
        return jsonify(response)


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
        if query_result:
            return jsonify(query_result[0])
        return jsonify({'_id': '-', 'contributing': '-', 'readme': '-', 'readme_language': '-', 'license_type': '-',
                       'opensource': '-'})


class RepoIssues(BaseDb):

    def get(self):
        name = request.args.get("name")
        org = request.args.get("org")
        start_date = dt.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
        end_date = dt.datetime.strptime(request.args.get("endDate"), '%Y-%m-%d') + dt.timedelta(seconds=86399)
        delta = end_date - start_date
        query_created = [
            {'$match': {'org': org, 'repo_name': name, 'created_at': {'$gte': start_date, '$lte': end_date}}},
            {'$group': {
                '_id': {
                    'year': {'$year': "$created_at"},
                    'month': {'$month': "$created_at"},
                    'day': {'$dayOfMonth': "$created_at"},
                },
                'count': {'$sum': 1}
            }},
            {'$project': {'_id': 0, "year": "$_id.year", "month": "$_id.month", "day": "$_id.day", 'count': 1}}
            ]
        query_closed = [{'$match': {'org': org, 'repo_name': name, 'closed_at': {'$gte': start_date, '$lte': end_date}}},
                        {'$group': {
                            '_id': {
                                'year': {'$year': "$closed_at"},
                                'month': {'$month': "$closed_at"},
                                'day': {'$dayOfMonth': "$closed_at"},
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


class RepoLastCommits(BaseDb):

    def get(self):
        name = request.args.get("name")
        org = request.args.get("org")
        query = {"repo_name": name, "org": org}
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
