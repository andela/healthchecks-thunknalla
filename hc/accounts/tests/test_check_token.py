from django.contrib.auth.hashers import make_password
from hc.test import BaseTestCase


class CheckTokenTestCase(BaseTestCase):

    def setUp(self):
        super(CheckTokenTestCase, self).setUp()
        self.profile.token = make_password("secret-token")
        self.profile.save()

    def test_it_shows_form(self):
        response = self.client.get("/accounts/check_token/alice/secret-token/")
        self.assertContains(response, "You are about to log in")

    def test_it_redirects(self):
        response = self.client.post("/accounts/check_token/alice/secret-token/")
        self.assertRedirects(response, "/checks/")

        # After login, token should be blank
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.token, "")

    # Login and test it redirects already logged in
    def test_it_redirects_already_logged_in(self):
        self.client.login(username="alice@example.org", password="password")
        response = self.client.post("/accounts/check_token/alice/secret-token/")
        self.assertEqual(response.status_code, 302)

    # Login with a bad token and check that it redirects
    #login  with bad token
    def test_redirects_bad_token(self):
        self.client.login(username="alice@example.org", password="password")
        response = self.client.post("/accounts/check_token/alice/bad-token/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/checks/")



    ### Any other tests?
