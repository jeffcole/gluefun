"""
This module exposes functionality for working with the GetGlue API.
"""


import logging
import pprint
import random
import requests
import string
import sys
import time
import urllib
import xmltodict

from requests.auth import OAuth1
from urlparse import urljoin

import settings


API_URL = u'http://api.getglue.com'
PUBLIC_URL = u'http://getglue.com'


logger = logging.getLogger('gluefun.custom')
pp = pprint.PrettyPrinter(indent=4)


class GlueClient(object):
    """
    This class encapsulates all the details of authorizing with and making
    requests for data to the GetGlue API.
    """

    ### Authorization methods

    def get_request_token(self):
        """
        Get the initial request token from GetGlue.

        Returns a dictionary.
        """
        url = urljoin(API_URL, '/oauth/request_token')
        oauth = OAuth1(settings.CONSUMER_KEY, settings.SECRET_KEY)
        response = requests.get(url, auth=oauth)
        return self._parse_query_string(response.text)

    def get_authorization_url(self, request_token, callback_url):
        """
        Get the encoded GetGlue authorization URL, given a request token and
        callback url.

        Returns a string.
        """
        url = urljoin(PUBLIC_URL, '/oauth/authorize')
        request_token.update({'oauth_callback': callback_url})
        return '{0}?{1}'.format(url, urllib.urlencode(request_token))

    def retrieve_access_token(self, request_token):
        """
        Retrieve and set the access token on this client object, given a request
        token.

        After this method has executed, the following attributes are available
        on the client object:
          1. user_id
          2. oauth
        """
        url = urljoin(API_URL, '/oauth/access_token')
        oauth = OAuth1(settings.CONSUMER_KEY, settings.SECRET_KEY,
                       request_token['oauth_token'],
                       request_token['oauth_token_secret'])
        response = requests.get(url, auth=oauth)
        response_dict = self._parse_query_string(response.text)
        self.user_id = response_dict.get('glue_userId', None)
        if self.user_id:
            self.oauth = OAuth1(settings.CONSUMER_KEY, settings.SECRET_KEY,
                                response_dict['oauth_token'],
                                response_dict['oauth_token_secret'])
        else:
            self.oauth = None

    ### Entity retrieval methods
    """
    These methods work by setting the 'url' and 'params' attributes on self,
    and deferring the API call and response parsing to the _get_response()
    method.
    """

    def get_friends(self):
        """
        Get the current client user's friends from the GetGlue API.

        Returns a list of strings.
        """
        self.url = urljoin(API_URL, '/v2/user/friends')
        self.params = {'userId': self.user_id}
        response = self._get_response()
        try:
            friends = response['adaptiveblue']['response']['friends']['userId']
        except KeyError:
            friends = []
        return friends

    def get_objects(self, category):
        """
        Get the current client user's object interactions from the GetGlue API.

        Returns a list of OrderedDict's.
        """
        all_objects, objects = [], []
        num_items, page = 20, 0
        next_token = None
        self.url = urljoin(API_URL, '/v2/user/objects')
        self.params = {'userId': self.user_id, 'category': category,
                       'numItems': num_items}
        """
        Handle paging. Checking response[...]['pagingInfo']['total'] is not
        reliable; instead, when response[...]['pagingInfo']['nextToken'] is
        absent, there are no more pages to fetch.
        """
        while page == 0 or next_token:
            page += 1
            self.params['page'] = page
            self.params['nextToken'] = next_token
            response = self._get_response()
            try:
                objects = (response['adaptiveblue']['response']['interactions']
                                   ['interaction'])
            except KeyError:
                objects = []
            try:
                next_token = response['adaptiveblue']['pagingInfo']['nextToken']
            except KeyError:
                next_token = None
            all_objects.extend(objects)
        return all_objects
             
    def get_user_object_action(self, user_id, object_key):
        """
        Get the interaction for the given user and object combination.

        Returns a string.
        """
        self.url = urljoin(API_URL, '/v2/user/object')
        self.params = {'userId': user_id, 'objectId': object_key}
        response = self._get_response()
        try:
            action = (response['adaptiveblue']['response']['interactions']
                              ['interaction']['action'])
        except KeyError:
            action = None
        return action

    ### Internal methods

    def _parse_query_string(self, qs):
        """
        Parse key=value pairs in a &-delimited query string into a dictionary.

        Returns a dictionary.
        """
        items = [item.split('=') for item in qs.split('&')]
        return {key: val for key, val in items}

    def _get_response(self):
        """
        Make an API call and return the parsed response. This method relies on
        the presence of the following attributes on self:
          1. url
          2. oauth
          3. params

        This method makes use of the requests and xmltodict modules for making
        requests and parsing xml into python dictionaries, respectively.

        Returns an OrderedDict.
        """
        response = requests.get(self.url, auth=self.oauth, params=self.params)
        return xmltodict.parse(response.text)
