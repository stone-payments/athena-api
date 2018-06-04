import datetime as dt
import json
from operator import itemgetter

from flask import jsonify, request

from app.common.client import *
from app.common.config import since_hour_delta
from app.common.db import BaseDb
from app.common.module import utc_time_datetime_format, find_key, name_and_org_regex_search, fill_all_dates, \
    merge_lists, process_data, accumulator, start_day_string_time, end_date_string_time


class CheckWithExist(BaseDb):

    def get(self):
        org = request.args.get("org")
        name = request.args.get("name")
        query = {'org': org, 'slug': name, 'db_last_updated': {'$gte': utc_time_datetime_format(since_hour_delta)}}
        projection = {'_id': 0, 'db_last_updated': 1}
        query_result = query_find_to_dictionary(self.db, 'Teams', query, projection)
        if not query_result:
            return jsonify({'response': 404})
        query_result[0]['db_last_updated'] = round((dt.datetime.utcnow() -
                                                    query_result[0]['db_last_updated']).total_seconds() / 60)
        return jsonify(query_result)


class TeamLanguages(BaseDb):

    def get(self):
        org = request.args.get("org")
        name = request.args.get("name")
        id_team = query_find_to_dictionary(self.db, 'Teams',
                                           {'slug': name, 'org': org},
                                           {'_id': '_id'})
        repo_id_list = query_find_to_dictionary_distinct(self.db, 'edges', 'from',
                                                         {'to': id_team[0]['_id'], "type": 'repo_to_team'})
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
            {'$project': {"name": "$_id.language", "_id": 0, 'value': '$count'}}
        ]
        query_result = self.db.Repo.aggregate(query)
        result = [dict(i) for i in query_result]
        if not result:
            return jsonify([{"name": "None", "value": 100}])
        soma = sum([readme_status['value'] for readme_status in result])
        for readme_status in result:
            if readme_status['name'] is None:
                readme_status['name'] = 'None'
            readme_status['value'] = round(int(readme_status['value']) / soma * 100, 1)
        result = sorted(result, key=itemgetter('value'), reverse=True)
        if len(result) > 4:
            new_result = result[:4]
            new_result.append({"name": "Others", "value": round(sum(item['value'] for item in result[4:]), 2)})
            return jsonify(new_result)
        return jsonify(result[:4])


class TeamOpenSource(BaseDb):

    def get(self):
        org = request.args.get("org")
        name = request.args.get("name")
        id_team = query_find_to_dictionary(self.db, 'Teams',
                                           {'slug': name, 'org': org,
                                            'db_last_updated': {'$gte': utc_time_datetime_format(since_hour_delta)}},
                                           {'_id': '_id'})
        repo_id_list = query_find_to_dictionary_distinct(self.db, 'edges', 'from',
                                                         {'to': id_team[0]['_id'], "type": 'repo_to_team',
                                                          'data.db_last_updated': {
                                                              '$gte': utc_time_datetime_format(since_hour_delta)}})
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
                                            'db_last_updated': {'$gte': utc_time_datetime_format(since_hour_delta)}},
                                           {'_id': '_id'})
        repo_id_list = query_find_to_dictionary_distinct(self.db, 'edges', 'from',
                                                         {'to': id_team[0]['_id'], "type": 'repo_to_team',
                                                          'data.db_last_updated': {
                                                              '$gte': utc_time_datetime_format(since_hour_delta)}})
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
                                            'db_last_updated': {'$gte': utc_time_datetime_format(since_hour_delta)}},
                                           {'_id': '_id'})
        repo_id_list = query_find_to_dictionary_distinct(self.db, 'edges', 'from',
                                                         {'to': id_team[0]['_id'], "type": 'repo_to_team',
                                                          'data.db_last_updated': {
                                                              '$gte': utc_time_datetime_format(since_hour_delta)}})
        query = [
            {
                '$match':
                    {'_id': {'$in': repo_id_list}, 'openSource': True}},
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
            return jsonify([{'status': 'Only private repositories', 'count': 100.0}])
        soma = sum([readme_status['count'] for readme_status in readme_status_list])
        for readme_status in readme_status_list:
            if readme_status['status'] is None:
                readme_status['status'] = 'None'
            readme_status['count'] = round(int(readme_status['count']) / soma * 100, 1)
        readme_status_list = sorted(readme_status_list, key=itemgetter('count'), reverse=True)
        return jsonify(readme_status_list)


class TeamReadmeLanguages(BaseDb):

    def get(self):
        org = request.args.get("org")
        name = request.args.get("name")
        id_team = query_find_to_dictionary(self.db, 'Teams',
                                           {'slug': name, 'org': org,
                                            'db_last_updated': {'$gte': utc_time_datetime_format(since_hour_delta)}},
                                           {'_id': '_id'})
        repo_id_list = query_find_to_dictionary_distinct(self.db, 'edges', 'from',
                                                         {'to': id_team[0]['_id'], "type": 'repo_to_team',
                                                          'data.db_last_updated': {
                                                              '$gte': utc_time_datetime_format(since_hour_delta)}})
        query = [
            {
                '$match':
                    {'_id': {'$in': repo_id_list}}},
            {'$group': {
                '_id': {
                    'language': "$readmeLanguage",
                },
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id.count': -1}},
            {'$project': {"language": {'$ifNull': ["$_id.language", "None"]}, "_id": 0, 'count': 1}}
        ]
        query_result = self.db.Repo.aggregate(query)
        readme_status_list = [dict(i) for i in query_result]
        if not readme_status_list:
            return jsonify([{'language': 'None', 'count': 100.0}])
        soma = sum([readme_status['count'] for readme_status in readme_status_list])
        for readme_status in readme_status_list:
            readme_status['count'] = round(int(readme_status['count']) / soma * 100, 1)
        readme_status_list = sorted(readme_status_list, key=itemgetter('count'), reverse=True)
        return jsonify(readme_status_list)


class TeamRepoMembers(BaseDb):

    def get(self):
        org = request.args.get("org")
        name = request.args.get("name")
        id_team = query_find_to_dictionary(self.db, 'Teams',
                                           {'slug': name, 'org': org},
                                           {'_id': '_id'})
        print(id_team)
        dev_id_list = query_find_to_dictionary_distinct(self.db, 'edges', 'from',
                                                        {'to': id_team[0]['_id'], "type": 'dev_to_team'})
        print(dev_id_list)
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
            {'$project': {"name": "$_id.member", "_id": 0}}
        ]
        query_result = query_aggregate_to_dictionary(self.db, 'Dev', query)
        query_result = sorted(query_result, key=lambda x: x['name'].lower(), reverse=False)
        print(query_result)
        return jsonify(query_result)


class TeamName(BaseDb):

    def get(self):
        return name_and_org_regex_search(self.db, 'Teams', 'slug')


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
        query = [{'$match': {'dev_id': {'$in': dev_id_list},
                             'committed_date': {'$gte': start_date, '$lt': end_date}}},
                 {'$group': {
                     '_id': {
                         'year': {'$year': "$committed_date"},
                         'month': {'$month': "$committed_date"},
                         'day': {'$dayOfMonth': "$committed_date"},
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
            {'$match': {'repository_id': {'$in': repo_id_list},
                        'created_at': {'$gte': start_date,
                                      '$lt': end_date}}},
            {'$group': {
                '_id': {
                    'year': {'$year': "$created_at"},
                    'month': {'$month': "$created_at"},
                    'day': {'$dayOfMonth': "$created_at"},
                },
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}},
            {'$project': {"_id": 0, "year": "$_id.year", "month": "$_id.month", "day": "$_id.day",
                          'count': 1}}
        ]

        query_closed = [
            {'$match': {'repository_id': {'$in': repo_id_list},
                        'closed_at': {'$gte': start_date,
                                     '$lt': end_date}}},
            {'$group': {
                '_id': {
                    'year': {'$year': "$closed_at"},
                    'month': {'$month': "$closed_at"},
                    'day': {'$dayOfMonth': "$closed_at"},
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
                {'$match': {'dev_id': {'$in': id_name},
                            'committed_date': {'$gte': start_date,
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
                {'$match': {'dev_id': {'$in': id_name},
                            'committed_date': {'$gte': start_date,
                                              '$lt': end_date}}},
                {'$group': {
                    '_id': {
                        'author': "$author",
                        'year': {'$year': "$committed_date"},
                        'month': {'$month': "$committed_date"},
                        'day': {'$dayOfMonth': "$committed_date"},
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
                                                    {'to': id_team[0]['_id'], "type": 'dev_to_team'})

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
            response.append([commits_ratio, additions_deletions_ratio, user['commits'], user['author']])
        if response:
            return jsonify({'data': response})
        else:
            return jsonify([response, {'x': 0, 'y': 0}])


class ReportConsolidateReadme(BaseDb):

    def get(self):
        org = request.args.get("org")
        teams_id = query_find_to_dictionary(self.db, 'Teams', {'org': org,
                                                               'db_last_updated': {
                                                                   '$gte': utc_time_datetime_format(since_hour_delta)}},
                                            {'_id': '_id'})
        teams_id = [x['_id'] for x in teams_id]
        query = [
            {
                '$match':
                    {'to': {'$in': teams_id}, "type": 'repo_to_team',
                     'data.db_last_updated': {'$gte': utc_time_datetime_format(since_hour_delta)}}},
            {'$group': {'_id': "$to", 'repositories': {'$push': "$from"}}},
            {'$project': {"repositories": "$repositories"}},
            {
                '$lookup':
                    {
                        'from': "Repo",
                        'localField': "repositories",
                        'foreignField': "_id",
                        'as': "repositories"
                    }
            },
            {
                '$lookup':
                    {
                        'from': "Teams",
                        'localField': "_id",
                        'foreignField': "_id",
                        'as': "teams"
                    }
            },
            {'$project': {"teams": "$teams.slug", "repositories": "$repositories", "_id": 1}},
            {"$unwind": "$repositories"},
            {'$group': {
                '_id': {
                    'team': '$_id',
                    'readme': '$repositories.readme',
                    'team_name': '$teams'
                },
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id.team': -1}},
            {"$unwind": "$_id.team_name"},
            {'$project': {"team": "$_id.team_name", "readme": "$_id.readme", "count": "$count",
                          "_id": 0}},
            {'$group': {'_id': "$team", 'team': {'$push': "$$ROOT"}}},
            {'$project': {"team": 1, "_id": 0}},
        ]
        query_result = self.db.edges.aggregate(query)
        readme_status_list2 = [dict(i) for i in query_result]
        lista = []
        for readme_status_list in readme_status_list2:
            readme_status_list = readme_status_list['team']
            lista.append(readme_status_list)
        flat_list = [item for sublist in lista for item in sublist]
        return jsonify(flat_list)


class ReportReadme(BaseDb):

    def get(self):
        org = request.args.get("org")
        teams_id = query_find_to_dictionary(self.db, 'Teams', {'org': org,
                                                               'db_last_updated': {
                                                                   '$gte': utc_time_datetime_format(since_hour_delta)}},
                                            {'_id': '_id'})
        teams_id = [x['_id'] for x in teams_id]
        query = [
            {
                '$match':
                    {'to': {'$in': teams_id}, "type": 'repo_to_team',
                     'data.db_last_updated': {'$gte': utc_time_datetime_format(since_hour_delta)}}},
            {'$group': {'_id': "$to", 'repositories': {'$push': "$from"}}},
            {'$project': {"repositories": "$repositories"}},
            {
                '$lookup':
                    {
                        'from': "Repo",
                        'localField': "repositories",
                        'foreignField': "_id",
                        'as': "repositories"
                    }
            },
            {
                '$lookup':
                    {
                        'from': "Teams",
                        'localField': "_id",
                        'foreignField': "_id",
                        'as': "teams"
                    }
            },
            {'$project': {"teams": "$teams.slug", "repositories": "$repositories", "_id": 1}},
            {"$unwind": "$repositories"},
            {'$project': {"team": "$teams", "status": "$repositories.readme", "repo_name": "$repositories.repoName",
                          "_id": 0}},
            {"$unwind": "$team"},
        ]
        query_result = self.db.edges.aggregate(query)
        query_result = [dict(i) for i in query_result]
        return jsonify(query_result)


class ReportRepositoryInfo(BaseDb):

    def get(self):
        org = request.args.get("org")
        teams_id = query_find_to_dictionary(self.db, 'Teams', {'org': org,
                                                               'db_last_updated': {
                                                                   '$gte': utc_time_datetime_format(since_hour_delta)}},
                                            {'_id': '_id'})
        teams_id = [x['_id'] for x in teams_id]
        query = [
            {
                '$match':
                    {'to': {'$in': teams_id}, "type": 'repo_to_team',
                     'data.db_last_updated': {'$gte': utc_time_datetime_format(since_hour_delta)}}},
            {'$group': {'_id': "$to", 'repositories': {'$push': "$from"}}},
            {'$project': {"repositories": "$repositories"}},
            {
                '$lookup':
                    {
                        'from': "Repo",
                        'localField': "repositories",
                        'foreignField': "_id",
                        'as': "repositories"
                    }
            },
            {
                '$lookup':
                    {
                        'from': "Teams",
                        'localField': "_id",
                        'foreignField': "_id",
                        'as': "teams"
                    }
            },
            {'$project': {"teams": "$teams.slug", "repositories": "$repositories", "_id": 1}},
            {"$unwind": "$repositories"},
            {'$project': {"readmeLanguage": "$repositories.readmeLanguage", "team": "$teams",
                          "readme": "$repositories.readme", "repo_name": "$repositories.repoName",
                          "openSource": "$repositories.openSource", "license": "$repositories.licenseType",
                          "contributing": "$repositories.contributing", "_id": 0}},
            {"$unwind": "$team"},
        ]
        query_result = self.db.edges.aggregate(query)
        query_result = [dict(i) for i in query_result]
        return jsonify(query_result)


class TeamRepositoriesReadme(BaseDb):

    def get(self):
        org = request.args.get("org")
        name = request.args.get("name")
        id_team = query_find_to_dictionary(self.db, 'Teams',
                                           {'slug': name, 'org': org,
                                            'db_last_updated': {'$gte': utc_time_datetime_format(since_hour_delta)}},
                                           {'_id': '_id'})
        repo_id_list = query_find_to_dictionary_distinct(self.db, 'edges', 'from',
                                                         {'to': id_team[0]['_id'], "type": 'repo_to_team',
                                                          'data.db_last_updated': {
                                                              '$gte': utc_time_datetime_format(since_hour_delta)}})
        query = [
            {
                '$match':
                    {'_id': {'$in': repo_id_list}}},
            {'$sort': {'repoName': 1}},
            {'$project': {"repoName": "$repoName", "status": {'$ifNull': ["$readme", "None"]}, "_id": 0}},
        ]
        query_result = query_aggregate_to_dictionary(self.db, "Repo", query)
        query_result = sorted(query_result, key=lambda x: x['repoName'].lower(), reverse=False)
        return jsonify(query_result)


class TeamLastCommits(BaseDb):

    def get(self):
        name = request.args.get("name")
        org = request.args.get("org")

        id_team = query_find_to_dictionary(self.db, 'Teams', {'slug': name, 'org': org}, {'_id': '_id'})
        dev_id_list = query_find_to_dictionary_distinct(self.db, 'edges', 'from',
                                                        {'to': id_team[0]['_id'], "type": 'dev_to_team'})

        query = {'dev_id': {'$in': dev_id_list}}
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
