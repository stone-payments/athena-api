from flask import jsonify
from app.common.client import *
from app.common.module import *
from app.common.db import BaseDb
from app.common.config import since_hour_delta


class OrgNames(BaseDb):

    def get(self):
        projection = {'_id': 0, 'org': 1}
        result = query_find_to_dictionary(self.db, 'Org', {}, projection)
        return jsonify(result)


class OrgLanguages(BaseDb):

    def get(self):
        name = request.args.get("name")
        query = [{'$match': {'org': name}},
                 {'$unwind': "$languages"},
                 {'$group': {
                     '_id': {
                         'language': "$languages.language",
                     },
                     'count': {'$sum': '$languages.size'}
                 }},
                 {'$sort': {'count': -1}},
                 {'$project': {'_id': 0, "languages": "$_id.language", 'count': 1}}]
        result = query_aggregate_to_dictionary(self.db, 'Repo', query)
        result_sum = sum([language['count'] for language in result])
        for x in result:
            x['count'] = round((x['count'] / result_sum * 100), 2)
        return jsonify(result[:12])


class OrgOpenSource(BaseDb):

    def get(self):
        name = request.args.get("name")
        query = [{'$match': {'org': name}},
                 {'$group': {
                     '_id': {
                         'openSource': {'$slice': ["$open_source.status", -1]},
                     },
                     'count': {'$sum': 1}
                 }},
                 {'$sort': {'_id.openSource': 1}},
                 {'$unwind': "$_id.openSource"},
                 {'$project': {'_id': 0, "name": "$_id.openSource", 'value': '$count'}}
                 ]
        open_source_type_list = query_aggregate_to_dictionary(self.db, 'Repo', query)
        result_sum = sum([license_type['value'] for license_type in open_source_type_list])
        for open_source_status in open_source_type_list:
            if open_source_status['name'] is None:
                open_source_status['name'] = 'None'
            open_source_status['value'] = round(int(open_source_status['value']) / result_sum * 100, 1)
        if len(open_source_type_list) < 2:
            find_key(open_source_type_list, [True, False])
        open_source_type_list = sorted(open_source_type_list, key=itemgetter('name'), reverse=False)
        return jsonify(open_source_type_list)


class OrgCommits(BaseDb):

    def get(self):
        name = request.args.get("name")
        start_date = dt.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
        end_date = dt.datetime.strptime(request.args.get("endDate"), '%Y-%m-%d') + dt.timedelta(seconds=86399)
        query = [{'$match': {'org': name, 'committed_date': {'$gte': start_date, '$lt': end_date}}},
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


class OrgReadme(BaseDb):

    def get(self):
        name = request.args.get("name")
        query = [{'$match': {'org': name}},
                 {'$group': {
                     '_id': {
                         'status': "$readme",
                     },
                     'count': {'$sum': 1}
                 }},
                 {'$sort': {'_id.status': -1}},
                 {'$project': {'_id': 0, "name": "$_id.status", 'value': '$count'}}
                 ]
        readme_status_list = query_aggregate_to_dictionary(self.db, 'Repo', query)
        result_sum = sum([readme_status['value'] for readme_status in readme_status_list])
        for readme_status in readme_status_list:
            if readme_status['name'] is None:
                readme_status['name'] = 'None'
            readme_status['value'] = round(int(readme_status['value']) / result_sum * 100, 1)
        if len(readme_status_list) < 3:
            find_key(readme_status_list, ['None', 'Poor', 'OK'])
        readme_status_list = sorted(readme_status_list, key=itemgetter('name'), reverse=True)
        return jsonify(readme_status_list)


class OrgOpenSourceReadme(BaseDb):

    def get(self):
        name = request.args.get("name")
        query = [
            {'$project': {id: 1, 'openSource': {'$slice': ["$open_source.status", -1]}}},
            {'$match': {'org': name, 'openSource': True}},
            {'$group': {
                '_id': {
                    'status': "$readme",
                },
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id.status': -1}},
            {'$project': {'_id': 0, "status": "$_id.status",  'count': 1}}
            ]
        readme_status_list = query_aggregate_to_dictionary(self.db, 'Repo', query)
        result_sum = sum([readme_status['count'] for readme_status in readme_status_list])
        for readme_status in readme_status_list:
            if readme_status['status'] is None:
                readme_status['status'] = 'None'
            readme_status['count'] = round(int(readme_status['count']) / result_sum * 100, 1)
        if len(readme_status_list) < 3:
            find_key(readme_status_list, ['None', 'Poor', 'OK'])
        readme_status_list = sorted(readme_status_list, key=itemgetter('status'), reverse=True)
        return jsonify(readme_status_list)


class OrgLicense(BaseDb):

    def get(self):
        name = request.args.get("name")
        query = [{'$match': {'org': name, 'openSource': True,
                             'db_last_updated': {'$gte': utc_time_datetime_format(since_hour_delta)}}},
                 {'$group': {
                     '_id': {
                         'license': "$licenseType",
                     },
                     'count': {'$sum': 1}
                 }},
                 {'$project': {'_id': 0, "license": {'$ifNull': ["$_id.license", "None"]}, 'count': 1}}
                 ]
        license_type_list = query_aggregate_to_dictionary(self.db, 'Repo', query)
        if not license_type_list:
            return jsonify([{'status': 'None', 'count': 100.0}])
        result_sum = sum([license_type['count'] for license_type in license_type_list])
        for license_type in license_type_list:
            license_type['count'] = round(int(license_type['count']) / result_sum * 100, 1)
        license_type_list = sorted(license_type_list, key=itemgetter('count'), reverse=True)
        return jsonify(license_type_list)


class OrgIssues(BaseDb):

    def get(self):
        name = request.args.get("name")
        start_date = dt.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
        end_date = dt.datetime.strptime(request.args.get("endDate"), '%Y-%m-%d') + dt.timedelta(seconds=86399)
        delta = end_date - start_date
        query_created = [{'$match': {'org': name, 'created_at': {'$gte': start_date, '$lte': end_date}}},
                         {'$group': {
                             '_id': {
                                 'year': {'$year': "$created_at"},
                                 'month': {'$month': "$created_at"},
                                 'day': {'$dayOfMonth': "$created_at"},
                             },
                             'count': {'$sum': 1}
                         }},
                         {'$project': {'_id': 0, "year": "$_id.year", "month": "$_id.month", "day": "$_id.day",
                                       'count': 1}}
                         ]
        query_closed = [{'$match': {'org': name, 'closed_at': {'$gte': start_date, '$lte': end_date}}},
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


class OrgInfo(BaseDb):

    def get(self):
        name = request.args.get("name")
        query = {'org': name}
        projection = {'_id': 0, 'collection_name': 0}
        org_info_list = query_find_to_dictionary(self.db, 'Org', query, projection)
        org_info_list[0]['db_last_updated'] = round((dt.datetime.utcnow() -
                                                     org_info_list[0]['db_last_updated']).total_seconds() / 60)
        return jsonify(org_info_list)


class OrgLastCommits(BaseDb):

    def get(self):
        name = request.args.get("name")
        projection = {"_id": 0, "repo_name": 1, "author": 1,"committed_date": 1, 'message_head_line': 1,
                      'branch_name':  {"$slice": -1}}
        org_last_commit_list = query_last_document_limit_(self.db, name, "Commit", projection, "committed_date", 7)
        for org_last_commit in org_last_commit_list:
            if org_last_commit["branch_name"]:
                org_last_commit['branch_name'] = org_last_commit["branch_name"][0]
        return jsonify(org_last_commit_list)


class OrgReadmeLanguage(BaseDb):

    def get(self):
        name = request.args.get("name")
        query = [{'$match': {'org': name,
                             'db_last_updated': {'$gte': utc_time_datetime_format(since_hour_delta)}}},
                 {'$group': {
                     '_id': {
                         "readmeLanguage": "$readmeLanguage",
                     },
                     'count': {'$sum': 1}
                 }},
                 {'$project': {'_id': 0, "readmeLanguage": {'$ifNull': ["$_id.readmeLanguage", "None"]}, 'count': 1}}
                 ]
        license_type_list = query_aggregate_to_dictionary(self.db, 'Repo', query)
        if not license_type_list:
            return jsonify([{'status': 'None', 'count': 100.0}])
        result_sum = sum([license_type['count'] for license_type in license_type_list])
        for license_type in license_type_list:
            license_type['count'] = round(int(license_type['count']) / result_sum * 100, 1)
        license_type_list = sorted(license_type_list, key=itemgetter('count'), reverse=True)
        return jsonify(license_type_list)


class OrgOpenSourceReadmeLanguage(BaseDb):

    def get(self):
        name = request.args.get("name")
        query = [
            {'$project': {'id': 1, 'org': 1, 'readme_language': 1, 'openSource': {'$slice': ["$open_source.status", -1]}}},
            {'$unwind': "$openSource"},
            {'$match': {'org': name, 'openSource': True}},
            {'$group': {
                '_id': {
                    'status': "$readme_language",
                },
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id.status': -1}},
            {'$project': {'_id': 0, "name": "$_id.status", "value": '$count'}}
            ]
        license_type_list = query_aggregate_to_dictionary(self.db, 'Repo', query)

        if not license_type_list:
            return jsonify([{'name': 'None', 'value': 100.0}])
        result_sum = sum([license_type['value'] for license_type in license_type_list])
        for license_type in license_type_list:
            license_type['value'] = round(int(license_type['value']) / result_sum * 100, 1)
        license_type_list = sorted(license_type_list, key=itemgetter('value'), reverse=True)
        return jsonify(license_type_list)


class OrgHeaderInfo(BaseDb):

    def get(self):
        name = request.args.get("name")
        start_date = dt.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
        end_date = dt.datetime.strptime(request.args.get("endDate"), '%Y-%m-%d') + dt.timedelta(seconds=86399)
        query_repository_count = {'$or': [{'org': name, 'deleted_at': {'$gte': start_date, '$lt': end_date}},
                                          {'org': name,'deleted_at': None}]}
        query_teams_count = {'$or': [{'org': name, 'deleted_at': {'$gte': start_date, '$lt': end_date}},
                                          {'org': name,'deleted_at': None}]}
        query_users_count = {'$or': [{'org': name, 'deleted_at': {'$gte': start_date, '$lt': end_date}},
                                          {'org': name,'deleted_at': None}]}
        query_commits_count = {'$or': [{'org': name, 'deleted_at': {'$gte': start_date, '$lt': end_date}},
                                          {'org': name,'deleted_at': None}]}
        repository_count = query_count(self.db, 'Repo', query_repository_count)
        teams_count = query_count(self.db, 'Teams', query_teams_count)
        user_count = query_count(self.db, 'Dev', query_users_count)
        commits_count = query_count(self.db, 'Commit', query_commits_count)
        print({'users': user_count, 'teams': teams_count, 'repositories': repository_count,
               'avgCommits': commits_count})
        if query_repository_count and query_teams_count and query_users_count and query_commits_count:
            return jsonify({'users': user_count, 'teams': teams_count, 'repositories': repository_count,
                            'avgCommits': commits_count})
        return jsonify({'users': 0, 'teams': 0, 'repositories': 0, 'avgCommits': 0})

