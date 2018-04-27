from flask import Flask
from instance.config import app_config
from app.common.mongo import Mongraph
from app.common.config import *


def create_app(config_name):

    from app.orgs.views import OrgNames, OrgLanguages, \
        OrgOpenSource, OrgCommits, OrgReadme, OrgOpenSourceReadme, OrgLicense, OrgIssues, OrgInfo, OrgReadmeLanguage,\
        OrgOpenSourceReadmeLanguage, OrgHeaderInfo
    from app.repo.views import RepoName, RepoLanguages, RepoCommits, RepoMembers,\
        RepoBestPratices, RepoIssues
    from app.user.views import UserAvatar, UserCommit, UserContributedRepo,\
        UserStats, UserLogin, UserTeam, UserNewWork
    from app.team.views import CheckWithExist, TeamCommits, TeamIssues, TeamLanguages, TeamLicense,\
        TeamName, TeamNewWork, TeamOpenSource, TeamReadme, TeamRepoMembers, ReportConsolidateReadme, ReportReadme,\
        ReportRepositoryInfo, TeamReadmeLanguages, TeamRepositoriesReadme

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')

    # org
    app.add_url_rule('/org_names', view_func=OrgNames.as_view('org_names'), methods=['GET'])
    app.add_url_rule('/org_languages', view_func=OrgLanguages.as_view('org_languages'), methods=['GET'])
    app.add_url_rule('/org_open_source', view_func=OrgOpenSource.as_view('org_open_source'), methods=['GET'])
    app.add_url_rule('/org_commits', view_func=OrgCommits.as_view('org_commits'), methods=['GET'])
    app.add_url_rule('/org_readme', view_func=OrgReadme.as_view('org_readme'), methods=['GET'])
    app.add_url_rule('/org_open_source_readme', view_func=OrgOpenSourceReadme.as_view('org_open_source_readme'),
                     methods=['GET'])
    app.add_url_rule('/org_license', view_func=OrgLicense.as_view('org_license'), methods=['GET'])
    app.add_url_rule('/org_issues', view_func=OrgIssues.as_view('org_issues'), methods=['GET'])
    app.add_url_rule('/org_info', view_func=OrgInfo.as_view('org_info'), methods=['GET'])
    app.add_url_rule('/org_readme_languages', view_func=OrgReadmeLanguage.as_view('org_readme_languages'),
                     methods=['GET'])
    app.add_url_rule('/org_open_source_readme_languages',
                     view_func=OrgOpenSourceReadmeLanguage.as_view('org_open_source_readme_languages'), methods=['GET'])
    app.add_url_rule('/org_header_info', view_func=OrgHeaderInfo.as_view('org_header_info'), methods=['GET'])

    # repo
    app.add_url_rule('/repo_name', view_func=RepoName.as_view('repo_name'), methods=['GET'])
    app.add_url_rule('/repo_languages', view_func=RepoLanguages.as_view('repo_languages'), methods=['GET'])
    app.add_url_rule('/repo_commits', view_func=RepoCommits.as_view('repo_commits'), methods=['GET'])
    app.add_url_rule('/repo_members', view_func=RepoMembers.as_view('repo_members'), methods=['GET'])
    app.add_url_rule('/repo_best_practices', view_func=RepoBestPratices.as_view('repo_best_practices'),
                     methods=['GET'])
    app.add_url_rule('/repo_issues', view_func=RepoIssues.as_view('repo_issues'), methods=['GET'])
    # user
    app.add_url_rule('/user_avatar', view_func=UserAvatar.as_view('user_avatar'), methods=['GET'])
    app.add_url_rule('/user_commit', view_func=UserCommit.as_view('user_commit'), methods=['GET'])
    app.add_url_rule('/user_contributed_repo', view_func=UserContributedRepo.as_view('user_contributed_repo'),
                     methods=['GET'])
    app.add_url_rule('/user_stats', view_func=UserStats.as_view('user_stats'), methods=['GET'])
    app.add_url_rule('/user_login', view_func=UserLogin.as_view('user_login'), methods=['GET'])
    app.add_url_rule('/user_team', view_func=UserTeam.as_view('user_team'), methods=['GET'])
    app.add_url_rule('/user_new_work', view_func=UserNewWork.as_view('user_new_work'), methods=['GET'])
    # team
    app.add_url_rule('/team_check_with_exist', view_func=CheckWithExist.as_view('team_check_with_exist'),
                     methods=['GET'])
    app.add_url_rule('/team_languages', view_func=TeamLanguages.as_view('team_languages'), methods=['GET'])
    app.add_url_rule('/team_open_source', view_func=TeamOpenSource.as_view('team_open_source'), methods=['GET'])
    app.add_url_rule('/team_readme', view_func=TeamReadme.as_view('team_readme'), methods=['GET'])
    app.add_url_rule('/team_license', view_func=TeamLicense.as_view('team_license'), methods=['GET'])
    app.add_url_rule('/team_repo_members', view_func=TeamRepoMembers.as_view('team_repo_members'), methods=['GET'])
    app.add_url_rule('/team_name', view_func=TeamName.as_view('team_name'), methods=['GET'])
    app.add_url_rule('/team_commits', view_func=TeamCommits.as_view('team_commits'), methods=['GET'])
    app.add_url_rule('/team_issues', view_func=TeamIssues.as_view('team_issues'), methods=['GET'])
    app.add_url_rule('/team_new_work', view_func=TeamNewWork.as_view('team_new_work'), methods=['GET'])
    app.add_url_rule('/team_readme_languages', view_func=TeamReadmeLanguages.as_view('team_readme_languages'),
                     methods=['GET'])
    app.add_url_rule('/report_consolidate_readme',
                     view_func=ReportConsolidateReadme.as_view('report_consolidate_readme'), methods=['GET'])
    app.add_url_rule('/report_readme', view_func=ReportReadme.as_view('report_readme'), methods=['GET'])
    app.add_url_rule('/report_team_repository_info',
                     view_func=ReportRepositoryInfo.as_view('report_team_repository_info'), methods=['GET'])
    app.add_url_rule('/team_repositories_readme',
                     view_func=TeamRepositoriesReadme.as_view('team_repositories_readme'), methods=['GET'])

    return app

