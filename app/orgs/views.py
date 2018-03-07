from flask import jsonify
from app.common.client import *
from app.common.module import *
from app.common.db import BaseDb


class OrgNames(BaseDb):

    def get(self):
        projection = {'_id': 0, 'org': 1}
        result = query_find_to_dictionary(self.db, 'Org', {}, projection)
        return jsonify(result)


class OrgLanguages(BaseDb):

    def get(self):
        name = request.args.get("name")
        query = [{'$match': {'org': name, 'db_last_updated': {'$gte': utc_time_datetime_format(-1)}}},
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
        query = [{'$match': {'org': name, 'db_last_updated': {'$gte': utc_time_datetime_format(-1)}}},
                 {'$group': {
                     '_id': {
                         'openSource': "$openSource",
                     },
                     'count': {'$sum': 1}
                 }},
                 {'$sort': {'_id.openSource': 1}},
                 {'$project': {'_id': 0, "status": "$_id.openSource", 'count': 1}}
                 ]
        open_source_type_list = query_aggregate_to_dictionary(self.db, 'Repo', query)
        result_sum = sum([license_type['count'] for license_type in open_source_type_list])
        for open_source_status in open_source_type_list:
            if open_source_status['status'] is None:
                open_source_status['status'] = 'None'
            open_source_status['count'] = round(int(open_source_status['count']) / result_sum * 100, 1)
        if len(open_source_type_list) < 2:
            find_key(open_source_type_list, [True, False])
        open_source_type_list = sorted(open_source_type_list, key=itemgetter('status'), reverse=False)
        return jsonify(open_source_type_list)


class OrgCommits(BaseDb):

    def get(self):
        name = request.args.get("name")
        start_date = dt.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
        end_date = dt.datetime.strptime(request.args.get("endDate"), '%Y-%m-%d') + dt.timedelta(seconds=86399)
        query = [{'$match': {'org': name, 'committedDate': {'$gte': start_date, '$lt': end_date}}},
                 {'$group': {
                     '_id': {
                         'year': {'$year': "$committedDate"},
                         'month': {'$month': "$committedDate"},
                         'day': {'$dayOfMonth': "$committedDate"},
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
        query = [{'$match': {'org': name, 'db_last_updated': {'$gte': utc_time_datetime_format(-1)}}},
                 {'$group': {
                     '_id': {
                         'status': "$readme",
                     },
                     'count': {'$sum': 1}
                 }},
                 {'$sort': {'_id.status': -1}},
                 {'$project': {'_id': 0, "status": "$_id.status", 'count': 1}}
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


class OrgOpenSourceReadme(BaseDb):

    def get(self):
        name = request.args.get("name")
        query = [
            {'$match': {'org': name, 'openSource': True, 'db_last_updated': {'$gte': utc_time_datetime_format(-1)}}},
            {'$group': {
                '_id': {
                    'status': "$readme",
                },
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id.status': -1}},
            {'$project': {'_id': 0, "status": "$_id.status", 'count': 1}}
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
                             'db_last_updated': {'$gte': utc_time_datetime_format(-1)}}},
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
        print(license_type_list)
        return jsonify(license_type_list)


class OrgIssues(BaseDb):

    def get(self):
        name = request.args.get("name")
        start_date = dt.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
        end_date = dt.datetime.strptime(request.args.get("endDate"), '%Y-%m-%d') + dt.timedelta(seconds=86399)
        delta = end_date - start_date
        query_created = [{'$match': {'org': name, 'createdAt': {'$gte': start_date, '$lte': end_date}}},
                         {'$group': {
                             '_id': {
                                 'year': {'$year': "$createdAt"},
                                 'month': {'$month': "$createdAt"},
                                 'day': {'$dayOfMonth': "$createdAt"},
                             },
                             'count': {'$sum': 1}
                         }},
                         {'$project': {'_id': 0, "year": "$_id.year", "month": "$_id.month", "day": "$_id.day",
                                       'count': 1}}
                         ]
        query_closed = [{'$match': {'org': name, 'closedAt': {'$gte': start_date, '$lte': end_date}}},
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


class OrgInfo(BaseDb):

    def get(self):
        name = request.args.get("name")
        query = {'org': name}
        projection = {'_id': 0, 'collection_name': 0}
        org_info_list = query_find_to_dictionary(self.db, 'Org', query, projection)
        org_info_list[0]['db_last_updated'] = round((dt.datetime.utcnow() -
                                                     org_info_list[0]['db_last_updated']).total_seconds() / 60)
        return jsonify(org_info_list)

