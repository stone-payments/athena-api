import unittest
from app import create_app


class AthenaRouterTestCase(unittest.TestCase):
    """This class represents the athena-router test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client

    # org
    def test_api_org_names(self):
        res = self.client().get('/org_names')
        self.assertEqual(res.status_code, 200)

    def test_api_org_languages(self):
        res = self.client().get('/org_languages?name=stone-payments')
        self.assertEqual(res.status_code, 200)

    def test_api_org_commits(self):
        res = self.client().get('/org_commits?name=stone-payments&startDate=2018-02-01&endDate=2018-02-16')
        self.assertEqual(res.status_code, 200)

    def test_api_org_open_source(self):
        res = self.client().get('/org_open_source?name=stone-payments')
        self.assertEqual(res.status_code, 200)

    def test_api_org_readme(self):
        res = self.client().get('/org_readme?name=stone-payments')
        self.assertEqual(res.status_code, 200)

    def test_api_org_open_source_readme(self):
        res = self.client().get('/org_open_source_readme?name=stone-payments')
        self.assertEqual(res.status_code, 200)

    def test_api_org_license(self):
        res = self.client().get('/org_license?name=stone-payments')
        self.assertEqual(res.status_code, 200)

    def test_api_org_issues(self):
        res = self.client().get('/org_issues?name=stone-payments&startDate=2018-02-01&endDate=2018-02-16')
        self.assertEqual(res.status_code, 200)

    def test_api_org_info(self):
        res = self.client().get('/org_info?name=stone-payments')
        self.assertEqual(res.status_code, 200)

    # team
    def test_api_team_name(self):
        res = self.client().get('/team_name?name=po&org=stone-payments')
        self.assertEqual(res.status_code, 200)

    def test_api_team_check_with_exist(self):
        res = self.client().get('/team_check_with_exist?org=stone-payments&name=pos')
        self.assertEqual(res.status_code, 200)

    def test_api_team_open_source(self):
        res = self.client().get('/team_open_source?org=stone-payments&name=pos')
        self.assertEqual(res.status_code, 200)

    def test_api_team_new_work(self):
        res = self.client().get('/team_new_work?name=pos&startDate=2018-02-01&endDate=2018-02-16&org=stone-payments')
        self.assertEqual(res.status_code, 200)

    def test_api_team_readme(self):
        res = self.client().get('/team_readme?org=stone-payments&name=pos')
        self.assertEqual(res.status_code, 200)

    def test_api_team_license(self):
        res = self.client().get('/team_license?org=stone-payments&name=pos')
        self.assertEqual(res.status_code, 200)

    def test_api_team_languages(self):
        res = self.client().get('/team_languages?org=stone-payments&name=pos')
        self.assertEqual(res.status_code, 200)

    def test_api_team_repo_members(self):
        res = self.client().get('/team_repo_members?org=stone-payments&name=pos')
        self.assertEqual(res.status_code, 200)

    def test_api_team_commits(self):
        res = self.client().get('/team_commits?name=pos&startDate=2018-02-01&endDate=2018-02-16&org=stone-payments')
        self.assertEqual(res.status_code, 200)

    def test_api_team_issues(self):
        res = self.client().get('/team_issues?name=pos&startDate=2018-02-01&endDate=2018-02-16&org=stone-payments')
        self.assertEqual(res.status_code, 200)

    # repo
    def test_api_repo_name(self):
        res = self.client().get('/repo_name?name=po&org=stone-payments')
        self.assertEqual(res.status_code, 200)

    def test_api_repo_commits(self):
        res = self.client()\
            .get('/repo_commits?name=pombo-correio-api&startDate=2018-02-01&endDate=2018-02-16&org=stone-payments')
        self.assertEqual(res.status_code, 200)

    def test_api_repo_members(self):
        res = self.client().get('/repo_members?name=pombo-correio-api&org=stone-payments')
        self.assertEqual(res.status_code, 200)

    def test_api_repo_best_practices(self):
        res = self.client().get('/repo_best_practices?name=pombo-correio-api&org=stone-payments')
        self.assertEqual(res.status_code, 200)

    def test_api_repo_issues(self):
        res = self.client()\
            .get('/repo_issues?name=pombo-correio-api&startDate=2018-02-01&endDate=2018-02-16&org=stone-payments')
        self.assertEqual(res.status_code, 200)

    # user
    def test_api_user_avatar(self):
        res = self.client().get('/user_avatar?login=MSDandrea')
        self.assertEqual(res.status_code, 200)

    def test_api_user_commit(self):
        res = self.client().get('/user_commit?name=MSDandrea&startDate=2018-02-01&endDate=2018-02-16')
        self.assertEqual(res.status_code, 200)

    def test_api_user_contributed_repo(self):
        res = self.client().get('/user_contributed_repo?name=MSDandrea&startDate=2018-02-01&endDate=2018-02-16')
        self.assertEqual(res.status_code, 200)

    def test_api_user_team(self):
        res = self.client().get('/user_team?name=MSDandrea')
        self.assertEqual(res.status_code, 200)

    def test_api_user_stats(self):
        res = self.client().get('/user_stats?name=MSDandrea&startDate=2018-02-01&endDate=2018-02-16')
        self.assertEqual(res.status_code, 200)

    def test_api_user_new_work(self):
        res = self.client().get('/user_new_work?name=MSDandrea&startDate=2018-02-01&endDate=2018-02-16')
        self.assertEqual(res.status_code, 200)


if __name__ == "__main__":
    unittest.main()

