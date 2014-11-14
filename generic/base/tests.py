'''
Created on Sep 5, 2014

@author: morteza
'''
import json

from django.test.client import Client

from CAuth.tests import create_user
from vigor.generic.utils.colorify import Colorify


class CRUDTestCase():
    # an instant of Client class
    client = None
    # name of Test e.g. Person TestCase
    test_name = ''
    # login url e.g. /auth/login/
    login_url = ''
    # url of the class the we want to test e.g. /got/Box/
    main_url = ''
    # data entry that is needed to add in setup function
    setup_data_entry = {}
    # data entry that is needed to add in post function
    post_data = {}
    # name of a filed that we use in change test functio to change and save it should be a string
    put_field_name = ''
    # if you have a file field and you want to except it to update
    put_excepted_filed = ''
    
    def setUp( self ):
        create_user()
        self.client = Client()
        self.client.post(self.login_url, data = {'username': 'test_user@local.com', 'password': '123456'})
        if self.setup_data_entry:
            response = self.client.post(self.main_url, data=self.setup_data_entry)
    
    def test_adding(self):
        if not self.post_data:
            self.assertFalse(False, "POST data is not set")
            return
        response = self.client.post(self.main_url, data=self.post_data)
        result = json.loads(response.content)
        self.assertFalse(result['hasError'], Colorify.fail('Adding failed in %s - Ex: %s # %s' % (self.test_name, result['message'], result['extraMessage'])))
        
    def test_reading_list(self):
        response = self.client.get(self.main_url + '?page=-1')
        result = json.loads(response.content)
        self.assertGreater(len(result['data']), 0, Colorify.fail('Reading Box failed in  %s - Ex: %s # %s' % (self.test_name, result['message'], result['extraMessage'])))
    
    def test_reading(self):
        response = self.client.get(self.main_url)
        
        result = json.loads(response.content)
        self.assertGreater(len(result['data']), 0, Colorify.fail('Reading failed in %s - doesn\'t exist any entry - Ex: %s # %s' % (self.test_name, result['message'], result['extraMessage'])))
        
        response = self.client.get(self.main_url + '%s/' % (result['data'][0]['id']))
        result = json.loads(response.content)
        self.assertFalse(result['hasError'], Colorify.fail('Failed to read in %s - Ex: %s # %s' % (self.test_name, result['message'], result['extraMessage'])))
    
    def test_delete(self):
        response = self.client.get(self.main_url)
        result = json.loads(response.content)
        self.assertGreater(len(result['data']), 0, Colorify.fail('Deleting failed in %s - doesn\'t exist any entry - Ex: %s # %s' % (self.test_name, result['message'], result['extraMessage'])))
        response = self.client.delete(self.main_url + '%s/' % (result['data'][0]['id']))
        result = json.loads(response.content)
        self.assertFalse(result['hasError'], Colorify.fail('Failed to delete in %s - Ex: %s # %s' % (self.test_name, result['message'], result['extraMessage'])))
    
    def test_update(self):
        if not self.put_field_name:
            self.assertFalse(False, "POST data is not set")
            return
        response = self.client.get(self.main_url)
        result = json.loads(response.content)
        self.assertGreater(len(result['data']), 0, Colorify.fail('Updating failed in %s - doesn\'t exist any entry - Ex: %s # %s' % (self.test_name, result['message'], result['extraMessage'])))
        obj = result['data'][0]
        if self.put_field_name:
            obj[self.put_field_name] = (obj[self.put_field_name] if obj[self.put_field_name] else "field is ") + ' - updated'
        if self.put_excepted_filed:
            obj.pop(self.put_excepted_filed)
        response = self.client.put(self.main_url + '%s/' % (obj['id']), data = obj)
        result = json.loads(response.content)
        self.assertFalse(result['hasError'], Colorify.fail('Failed to update in  %s - Ex: %s # %s' % (self.test_name, result['message'], result['extraMessage'])))
