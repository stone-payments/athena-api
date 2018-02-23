from collections import defaultdict
from flask import jsonify
from app.common.client import *
from app.common.module import *
from threading import Thread
import queue
from app.common.db import BaseDb


class CheckWithExist(BaseDb):

    def get(self):
        org = request.args.get("org")
        name = request.args.get("name")
        query = {'org': org, 'slug': name}
        projection = {'_id': 1}
        query_result = query_find_to_dictionary(self.db, 'Teams', query, projection)
        if not query_result:
            return jsonify({'response': 404})
        return jsonify({'response': 200})


class TeamLanguages(BaseDb):

    def get(self):
        org = request.args.get("org")
        name = request.args.get("name")
        query = [
            {'$lookup': {'from': 'Teams', 'localField': 'to', 'foreignField': '_id', 'as': 'Teams'}},
            {'$lookup': {'from': 'Repo', 'localField': 'from', 'foreignField': '_id', 'as': 'Repo'}},
            {
                '$match':
                    {'Teams.0.slug': name, 'type': 'repo_to_team', 'Teams.0.org': org}},
            {"$unwind": "$Repo"},
            {'$project': {'_id': 0, "languages": "$Repo.languages", 'count': 1}},
            {"$unwind": "$languages"},
            {'$project': {'_id': 0, "languages": "$languages", 'count': 1}},
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
        query_result = self.db.edges.aggregate(query)
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
        query = [
            {'$lookup': {'from': 'Teams', 'localField': 'to', 'foreignField': '_id', 'as': 'Teams'}},
            {'$lookup': {'from': 'Repo', 'localField': 'from', 'foreignField': '_id', 'as': 'Repo'}},
            {
                '$match':
                    {'Teams.0.slug': name, 'type': 'repo_to_team', 'Teams.0.org': org}},
            {'$group': {
                '_id': {
                    'status': "$Repo.openSource",
                },
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id.status': -1}},
            {'$project': {"status": "$_id.status", "_id": 0, 'count': 1}}
        ]
        query_result = self.db.edges.aggregate(query)
        if not query_result:
            return json.dumps([{'response': 404}])
        readme_status_list = [dict(i) for i in query_result]
        soma = sum([readme_status['count'] for readme_status in readme_status_list])
        for readme_status in readme_status_list:
            readme_status['status'] = readme_status['status'][0]
            readme_status['count'] = round(int(readme_status['count']) / soma * 100, 1)
        if len(readme_status_list) < 2:
            find_key(readme_status_list, [True, False])
        readme_status_list = sorted(readme_status_list, key=itemgetter('status'), reverse=False)
        return jsonify(readme_status_list)


class TeamReadme(BaseDb):

    def get(self):
        org = request.args.get("org")
        name = request.args.get("name")
        query = [
            {'$lookup': {'from': 'Teams', 'localField': 'to', 'foreignField': '_id', 'as': 'Teams'}},
            {'$lookup': {'from': 'Repo', 'localField': 'from', 'foreignField': '_id', 'as': 'Repo'}},
            {
                '$match':
                    {'Teams.0.slug': name, 'type': 'repo_to_team', 'Teams.0.org': org}},
            {'$group': {
                '_id': {
                    'status': "$Repo.readme",
                },
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id.status': -1}},
            {'$project': {"status": "$_id.status", "_id": 0, 'count': 1}}
        ]
        query_result = self.db.edges.aggregate(query)
        readme_status_list = [dict(i) for i in query_result]
        soma = sum([readme_status['count'] for readme_status in readme_status_list])
        for readme_status in readme_status_list:
            if readme_status['status'][0] is None:
                readme_status['status'] = 'None'
            else:
                readme_status['status'] = readme_status['status'][0]
            readme_status['count'] = round(int(readme_status['count']) / soma * 100, 1)
        if len(readme_status_list) < 3:
            find_key(readme_status_list, ['None', 'Poor', 'OK'])
        readme_status_list = sorted(readme_status_list, key=itemgetter('status'), reverse=True)
        return jsonify(readme_status_list)


class TeamLicense(BaseDb):

    def get(self):
        org = request.args.get("org")
        name = request.args.get("name")
        query = [
            {'$lookup': {'from': 'Teams', 'localField': 'to', 'foreignField': '_id', 'as': 'Teams'}},
            {'$lookup': {'from': 'Repo', 'localField': 'from', 'foreignField': '_id', 'as': 'Repo'}},
            {
                '$match':
                    {'Teams.0.slug': name, 'type': 'repo_to_team', 'Teams.0.org': org}},
            {'$group': {
                '_id': {
                    'status': "$Repo.licenseType",
                },
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id.count': -1}},
            {'$project': {"status": "$_id.status", "_id": 0, 'count': 1}}
        ]
        query_result = self.db.edges.aggregate(query)
        readme_status_list = [dict(i) for i in query_result]
        soma = sum([readme_status['count'] for readme_status in readme_status_list])
        for readme_status in readme_status_list:
            if readme_status['status'][0] is None:
                readme_status['status'] = 'None'
            else:
                readme_status['status'] = readme_status['status'][0]
            readme_status['count'] = round(int(readme_status['count']) / soma * 100, 1)
        return jsonify(readme_status_list)


class TeamRepoMembers(BaseDb):

    def get(self):
        org = request.args.get("org")
        name = request.args.get("name")
        query = [
            {'$lookup': {'from': 'Teams', 'localField': 'to', 'foreignField': '_id', 'as': 'Teams'}},
            {'$lookup': {'from': 'Dev', 'localField': 'from', 'foreignField': '_id', 'as': 'Dev'}},
            {
                '$match':
                    {'Teams.0.slug': name, 'type': 'dev_to_team', 'Teams.0.org': org}},
            {'$group': {
                '_id': {
                    'member': "$Dev.login",
                }
            }},
            {'$sort': {'_id.member': 1}},
            {'$project': {"member": "$_id.member", "_id": 0}}
        ]
        query_result = query_aggregate_to_dictionary(self.db, 'edges', query)
        return jsonify(query_result)


class TeamName(BaseDb):

    def get(self):
        name = "^" + str(request.args.get("name"))
        org = request.args.get("org")
        compiled_name = re.compile(r'%s' % name, re.I)
        query_result = self.db['Teams'].find({'slug': {'$regex': compiled_name}, 'org': org},
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

        def issue_response(list):
            c = defaultdict(int)
            list = [x for xs in list for x in xs]
            range_days = [start_date + dt.timedelta(days=i) for i in range(delta.days + 1)]
            list = sorted(list, key=itemgetter('date'), reverse=False)
            for y in list:
                y['day'] = str(y.get('date').strftime('%a %d-%b-%y'))
            for d in list:
                c[d['date']] += d['count']
            list = [{'date': day, 'count': count} for day, count in c.items()]
            list = [fill_all_dates(day, list) for day in range_days]
            return list

        def query_created(input, output):
            while True:
                try:
                    dev_id = input.get_nowait()
                    query_1_2 = [{'$match': {'devId': dev_id,
                                             'committedDate': {'$gte': start_date, '$lt': end_date}}},
                                 {'$group': {
                                     '_id': {
                                         'year': {'$year': "$committedDate"},
                                         'month': {'$month': "$committedDate"},
                                         'day': {'$dayOfMonth': "$committedDate"},
                                     },
                                     'count': {'$sum': 1}
                                 }},
                                 {'$project': {"_id": 0, "year": "$_id.year", "month": "$_id.month", "day": "$_id.day",
                                               'count': 1}}]
                    count_list = query_aggregate_to_dictionary(self.db, 'Commit', query_1_2)
                    if count_list:
                        for count in count_list:
                            count['date'] = dt.datetime(count['year'], count['month'], count['day'], 0, 0)
                        output.put(count_list)
                except queue.Empty:
                    break

        id_team = query_find_to_dictionary(self.db, 'Teams', {'slug': name, 'org': org}, {'_id': '_id'})
        repo_id_list = query_find_to_dictionary_distinct(self.db, 'edges', 'from',
                                                         {'to': id_team[0]['_id'], "type": 'dev_to_team'})
        created = Queue()
        output_created = Queue()
        [created.put(id) for id in repo_id_list]
        workers_commit = [Thread(target=query_created, args=(created, output_created,)) for _ in range(200)]
        [t.start() for t in workers_commit]
        [t.join() for t in workers_commit]
        lista_created = [output_created.get_nowait() for _ in range(output_created.qsize())]
        lista_created = issue_response(lista_created)
        return jsonify(lista_created)


class TeamIssues(BaseDb):

    def get(self):
        name = request.args.get("name")
        org = request.args.get("org")
        start_date = dt.datetime.strptime(request.args.get("startDate"), '%Y-%m-%d')
        end_date = dt.datetime.strptime(request.args.get("endDate"), '%Y-%m-%d') + dt.timedelta(seconds=86399)
        delta = end_date - start_date

        def issue_response(list):
            c = defaultdict(int)
            list = [x for xs in list for x in xs]
            range_days = [start_date + dt.timedelta(days=i) for i in range(delta.days + 1)]
            list = sorted(list, key=itemgetter('date'), reverse=False)
            for y in list:
                y['day'] = str(y.get('date').strftime('%a %d-%b-%y'))
            for d in list:
                c[d['date']] += d['count']
            list = [{'date': day, 'count': count} for day, count in c.items()]
            list = [fill_all_dates(day, list) for day in range_days]
            list = accumulator(list)
            return list

        def query_created(input, output):
            while True:
                try:
                    id_name = input.get_nowait()
                    query_1_2 = [
                        {'$match': {'repositoryId': id_name,
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
                    count_list = query_aggregate_to_dictionary(self.db, 'Issue', query_1_2)
                    if count_list:
                        for count in count_list:
                            count['date'] = dt.datetime(count['year'], count['month'], count['day'], 0, 0)
                        output.put(count_list)
                except queue.Empty:
                    break

        def query_closed(input, output):
            while True:
                try:
                    id_name = input.get_nowait()
                    query_1_2 = [
                        {'$match': {'repositoryId': id_name,
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
                    count_list = query_aggregate_to_dictionary(self.db, 'Issue', query_1_2)
                    if count_list:
                        for count in count_list:
                            count['date'] = dt.datetime(count['year'], count['month'], count['day'], 0, 0)
                        output.put(count_list)
                except queue.Empty:
                    break

        id_team = query_find_to_dictionary(self.db, 'Teams', {'slug': name, 'org': org}, {'_id': '_id'})
        repo_id_list = query_find_to_dictionary_distinct(self.db, 'edges', 'from',
                                                         {'to': id_team[0]['_id'], "type": 'repo_to_team'})
        created = Queue()
        closed = Queue()
        output_created = Queue()
        output_closed = Queue()
        [created.put(id) for id in repo_id_list]
        [closed.put(id) for id in repo_id_list]
        workers_commit = [Thread(target=query_created, args=(created, output_created,)) for _ in range(200)]
        workers_days = [Thread(target=query_closed, args=(closed, output_closed,)) for _ in range(200)]
        [t.start() for t in workers_commit]
        [t.start() for t in workers_days]
        [t.join() for t in workers_commit]
        [t.join() for t in workers_days]
        lista_closed = [output_closed.get_nowait() for _ in range(output_closed.qsize())]
        lista_created = [output_created.get_nowait() for _ in range(output_created.qsize())]
        lista_closed = issue_response(lista_closed)
        lista_created = issue_response(lista_created)
        return jsonify([lista_closed, lista_created])


class TeamNewWork(BaseDb):

    def get(self):
        org = request.args.get("org")
        name = request.args.get("name")
        start_date = start_day_string_time()
        end_date = end_date_string_time()

        def query_id_name(input, output):
            while True:
                try:
                    id_name = input.get_nowait()
                    query_1_2 = [
                        {'$match': {'devId': id_name,
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
                    response = query_aggregate_to_dictionary(self.db, 'Commit', query_1_2)
                    output.put(response)
                except queue.Empty:
                    break

        def query_id_name2(input, output):
            while True:
                try:
                    id_name = input.get_nowait()
                    query_1_2 = [
                        {'$match': {'devId': id_name,
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
                    response = query_aggregate_to_dictionary(self.db, 'Commit', query_1_2)
                    output.put(response)
                except queue.Empty:
                    break

        id_team = query_find_to_dictionary(self.db, 'Teams', {'slug': name, 'org': org}, {'_id': '_id'})
        id_list = query_find_to_dictionary_distinct(self.db, 'edges', 'from',
                                                    {'to': id_team[0]['_id'], "type": 'dev_to_team'})
        input_commits = Queue()
        input_days = Queue()
        output_commits = Queue()
        output_days = Queue()
        [input_commits.put(id) for id in id_list]
        [input_days.put(id) for id in id_list]
        workers_commit = [Thread(target=query_id_name, args=(input_commits, output_commits,)) for _ in range(200)]
        workers_days = [Thread(target=query_id_name2, args=(input_days, output_days,)) for _ in range(200)]
        [t.start() for t in workers_commit]
        [t.start() for t in workers_days]
        [t.join() for t in workers_commit]
        [t.join() for t in workers_days]
        commits_count_list = [output_commits.get_nowait() for _ in id_list]
        total_days_count = [output_days.get_nowait() for _ in id_list]
        commits_count_list = [x[0] for x in commits_count_list if x]
        total_days_count = [x[0] for x in total_days_count if x]
        lista = merge_lists(commits_count_list, total_days_count, 'author')
        all_days = [start_date + dt.timedelta(days=x) for x in range((end_date - start_date).days + 1)]
        working_days = sum(1 for d in all_days if d.weekday() < 5)
        response = []
        for user in lista:
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
