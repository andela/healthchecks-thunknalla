from datetime import timedelta as td
from django.utils.timezone import now


from hc.api.models import Check
from hc.test import BaseTestCase


class ListChecksTestCase(BaseTestCase):
    def setUp(self):
        super(ListChecksTestCase, self).setUp()

        self.now = now().replace(microsecond=0)

        self.a1 = Check(user=self.alice, name="Alice 1")
        self.a1.timeout = td(seconds=3600)
        self.a1.grace = td(seconds=900)
        self.a1.last_ping = self.now
        self.a1.n_pings = 1
        self.a1.status = "new"
        self.a1.save()

        self.a2 = Check(user=self.alice, name="Alice 2")
        self.a2.timeout = td(seconds=86400)
        self.a2.grace = td(seconds=3600)
        self.a2.last_ping = self.now
        self.a2.status = "up"
        self.a2.save()

    def get(self):
        return self.client.get("/api/v1/checks/", HTTP_X_API_KEY="abc")

    def test_it_works(self):
        r = self.get()

        ### Assert the response status code
        self.assertTrue(r.status_code == 200)

        doc = r.json()
        self.assertTrue("checks" in doc)

        checks = {check["name"]: check for check in doc["checks"]}
        ### Assert the expected length of checks

        self.assertEqual(len(doc["checks"]), 2)

        ### Assert the checks Alice 1 and Alice 2's timeout, grace, ping_url, status,
        ### last_ping, n_pings and pause_url
        self.assertEqual(checks['Alice 1']['timeout'], 3600)
        self.assertEqual(checks['Alice 1']['grace'], 900)
        self.assertEqual(checks['Alice 1']['ping_url'], self.a1.to_dict()['ping_url'])
        self.assertEqual(checks['Alice 1']['status'], "new")
        self.assertEqual(checks['Alice 1']['last_ping'], self.now.isoformat())
        self.assertEqual(checks['Alice 1']['n_pings'], self.a1.to_dict()['n_pings'])
        self.assertEqual(checks['Alice 1']['pause_url'], self.a1.to_dict()['pause_url'])

        self.assertEqual(checks['Alice 2']['timeout'], 86400)
        self.assertEqual(checks['Alice 2']['grace'], 3600)
        self.assertEqual(checks['Alice 2']['ping_url'], self.a2.to_dict()['ping_url'])
        self.assertEqual(checks['Alice 2']['status'], "up")
        self.assertEqual(checks['Alice 2']['last_ping'], self.a2.to_dict()['last_ping'])
        self.assertEqual(checks['Alice 2']['n_pings'], self.a2.to_dict()['n_pings'])
        self.assertEqual(checks['Alice 2']['pause_url'], self.a2.to_dict()['pause_url'])

    def test_it_shows_only_users_checks(self):
        bobs_check = Check(user=self.bob, name="Bob 1")
        bobs_check.save()

        r = self.get()
        data = r.json()
        self.assertEqual(len(data["checks"]), 2)
        for check in data["checks"]:
            self.assertNotEqual(check["name"], "Bob 1")

    ### Test that it accepts an api_key in the request

    def test_it_accepts_an_api_key_in_request(self):
        r = self.get()
        self.assertTrue('HTTP_X_API_KEY' in r.request)
