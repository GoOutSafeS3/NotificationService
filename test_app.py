import unittest

import dateutil
from app import create_app
from datetime import datetime
from dateutil import parser

class TestNotifications(unittest.TestCase):
    @classmethod
    def setUp(cls):
        # Initialize a temporary db for testing
        cls.app = create_app('sqlite:///:memory:').app
        cls.client = cls.app.test_client()

    def test_no_notifications(self):
        request = self.client.get('/notifications')
        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.json, [])

        request = self.client.get('/notifications',
            query_string = {
                "read": True
            })
        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.json, [])

        request = self.client.get('/notifications',
            query_string = {
                "read": False
            })
        self.assertEqual(request.status_code, 200)
        self.assertEqual(request.json, [])

    def test_create_notification(self):
        date = datetime.now()
        noti = {
                'user_id': 1,
                'sent_on': date.isoformat(),
                'content': 'Test1'
            }

        request = self.client.post('/notifications', 
            json = noti)
        self.assertEqual(request.status_code, 201)
        self.assertIn('url', request.json)

        request = self.client.get('/notifications')
        self.assertEqual(request.status_code, 200)
        self.assertEqual(len(request.json), 1)
        self.assertEqual(request.json[0]['user_id'], noti['user_id'])
        self.assertEqual(request.json[0]['content'], noti['content'])
