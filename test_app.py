import re
import unittest

import dateutil
from app import create_app
from datetime import datetime, timedelta
from dateutil import parser

class TestNotifications(unittest.TestCase):
    @classmethod
    def setUp(cls):
        # Initialize a temporary db for testing
        cls.app = create_app('sqlite:///:memory:').app
        cls.client = cls.app.test_client()

    def create_notification(self, noti):
        return self.client.post('/notifications', json = noti)

    def get_notifications(self, params):
        return self.client.get('/notifications', query_string = params)

    def edit_notification(self, url, noti):
        return self.client.patch(url, json = noti)

    def test_no_notifications(self):
        request = self.client.get('/notifications')
        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.json, [])

    def test_create_notification(self):
        date = datetime.now()
        noti = {
                'user_id': 1,
                'sent_on': date.isoformat(),
                'content': 'Test1'
            }

        request = self.create_notification(noti)
        self.assertEqual(request.status_code, 201)
        self.assertIn('url', request.json)
        obj = request.json

        request = self.client.get('/notifications')
        self.assertEqual(request.status_code, 200)
        self.assertEqual(len(request.json), 1)
        self.assertEqual(request.json[0]['user_id'], noti['user_id'])
        self.assertEqual(request.json[0]['content'], noti['content'])

        request = self.client.get(obj['url'])
        self.assertEqual(request.status_code, 200)
        self.assertIn('url', request.json)
        self.assertIn('user_id', request.json)
        self.assertIn('sent_on', request.json)
        self.assertIn('content', request.json)
        self.assertIn('read_on', request.json)
        
        date = datetime.now()
        noti = {
                'user_id': 1,
                'sent_on': "2020-11-16T20:08:39.128358",
                'read_on': date.isoformat(),
                'content': 'Test1'
            }

        request = self.create_notification(noti)
        self.assertEqual(request.status_code, 201)
        self.assertIn('url', request.json)

    def test_user_notifications(self):
        date = datetime.now()
        noti1 = {
                'user_id': 1,
                'sent_on': date.isoformat(),
                'content': 'Test1'
            }
        noti2 = {
                'user_id': 2,
                'sent_on': date.isoformat(),
                'content': 'Test2'
            }

        request = self.create_notification(noti1)
        self.assertEqual(request.status_code, 201)
        self.assertIn('url', request.json)

        request = self.create_notification(noti2)
        self.assertEqual(request.status_code, 201)

        request = self.get_notifications({'user_id': 1})
        
        self.assertEqual(request.status_code, 200)
        self.assertEqual(len(request.json), 1)
        self.assertEqual(request.json[0]['user_id'], noti1['user_id'])
        self.assertEqual(request.json[0]['content'], noti1['content'])

    def test_read_notification(self):
        date_sent = datetime(2020, 10, 10, 10, 0)
        date_read = datetime(2020, 10, 10, 11, 0)
        noti1 = {
                'user_id': 1,
                'sent_on': date_sent.isoformat(),
                'content': 'Test1'
            }
        noti2 = {
                'user_id': 1,
                'sent_on': date_sent.isoformat(),
                'content': 'Test2'
            }

        request = self.create_notification(noti1)
        self.assertEqual(request.status_code, 201)
        self.assertIn('url', request.json)
        obj1 = request.json

        request = self.create_notification(noti2)
        self.assertEqual(request.status_code, 201)

        request = self.get_notifications({'user_id': 1, 'read': True})
        
        self.assertEqual(request.status_code, 200)
        self.assertEqual(len(request.json), 0)

        request = self.edit_notification(obj1['url'], { 'read_on': date_read.isoformat()})
        self.assertEqual(request.status_code, 200)

        request = self.get_notifications({'user_id': 1, 'read': True})
        
        self.assertEqual(request.status_code, 200)
        self.assertEqual(len(request.json), 1)
        self.assertEqual(request.json[0]['content'], 'Test1')

        request = self.get_notifications({'user_id': 1, 'read': False})
        
        self.assertEqual(request.status_code, 200)
        self.assertEqual(len(request.json), 1)
        self.assertEqual(request.json[0]['content'], 'Test2')

    def test_new_malformed_dates(self):
        noti = {
            "user_id": 1,
            "sent_on": "foo",
            "content": "Test"
        }
        request = self.create_notification(noti)
        self.assertEqual(request.status_code, 400)

        noti = {
            "user_id": 1,
            "sent_on": "2020-11-16T20:08:39.128358",
            "read_on": "foo",
            "content": "Test"
        }
        request = self.create_notification(noti)
        self.assertEqual(request.status_code, 400)

    def test_new_future_dates(self):
        tomorrow = datetime.today() + timedelta(1)
        noti = {
            "user_id": 1,
            "sent_on": tomorrow.isoformat(),
            "content": "Test"
        }
        request = self.create_notification(noti)
        self.assertEqual(request.status_code, 400)

        noti = {
            "user_id": 1,
            "sent_on": "2020-11-16T20:08:39.128358",
            "read_on": tomorrow.isoformat(),
            "content": "Test"
        }
        request = self.create_notification(noti)
        self.assertEqual(request.status_code, 400)

    def test_read_before_sent(self):
        noti = {
            "user_id": 1,
            "sent_on": "2020-11-16T20:08:39.128358",
            "read_on": "2020-11-15T20:08:39.128358",
            "content": "Test"
        }
        request = self.create_notification(noti)
        self.assertEqual(request.status_code, 400)

    def test_edit_malformed_dates(self):
        noti = {
            "user_id": 1,
            "sent_on": "2020-11-16T20:08:39.128358",
            "content": "Test"
        }
        obj = self.create_notification(noti).json

        patch = {
            "read_on": "foo"
        }
        request = self.edit_notification(obj['url'], patch)
        self.assertEqual(request.status_code, 400)

    def test_edit_future_dates(self):
        noti = {
            "user_id": 1,
            "sent_on": "2020-11-16T20:08:39.128358",
            "content": "Test"
        }
        obj = self.create_notification(noti).json

        tomorrow = datetime.today() + timedelta(1)
        patch = {
            "read_on": tomorrow.isoformat()
        }
        request = self.edit_notification(obj['url'], patch)
        self.assertEqual(request.status_code, 400)

    def test_edit_read_before_sent(self):
        noti = {
            "user_id": 1,
            "sent_on": "2020-11-16T20:08:39.128358",
            "content": "Test"
        }
        obj = self.create_notification(noti).json

        patch = {
            "read_on": "2020-11-15T20:08:39.128358",
        }
        request = self.edit_notification(obj['url'], patch)
        self.assertEqual(request.status_code, 400)

    def test_get_nonexistant_notification(self):
        request = self.client.get('/notifications/1')
        self.assertEqual(request.status_code, 404)

    def test_edit_nonexistant_notification(self):
        request = self.edit_notification('/notifications/1', {
            'read_on': "2020-11-15T20:08:39.128358"
        })
        self.assertEqual(request.status_code, 404)

    def test_edit_complete_notification(self):
        obj = self.create_notification({
            'user_id': 1,
            'content': 'Test',
            'sent_on': '2020-11-15T20:08:39.128358',
            'read_on': '2020-11-16T20:08:39.128358'
        }).json

        request = self.edit_notification(obj['url'], {
            'read_on': "2020-11-17T20:08:39.128358"
        })
        self.assertEqual(request.status_code, 400)
