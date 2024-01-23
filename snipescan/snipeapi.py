"""A small API Interface for the things I'll need from Snipe"""
import logging
import logging.config
import json

import requests

import settings
from project import all_snipe_endpoints

MAX_LIMIT = 500


class SnipeGet:

    def __init__(self, snipe_url, api_key, endpoint='hardware', limit=500):
        logging.config.dictConfig(settings.LOGGING_CONFIG)
        self.logger = logging.getLogger(__name__)
        
        self._api_key = api_key
        self._snipe_url = snipe_url
        if endpoint in all_snipe_endpoints:
            self._endpoint = endpoint
        else:
            self.logger.error('Endpoint %s not defined, defaulting to hardware', endpoint)
            self._endpoint = 'hardware'
        if limit > MAX_LIMIT:
            self.logger.warn('Limit %s is higher than %s, setting to %s',
                             limit, MAX_LIMIT, MAX_LIMIT)
            limit = MAX_LIMIT
        elif    limit <= 0:
            self.logger.warn('Limit %s is lower than 1, setting to %s',
                             limit, MAX_LIMIT)
            limit = MAX_LIMIT
        self._limit = limit
        self._url = self._snipe_url + self._endpoint + '?limit=' + str(limit)
        self._headers = {
                "accept": "application/json",
                "Authorization": "Bearer " + self._api_key
            }
    
    def get_all(self):
        ret = []
        offset = 0
        try:
            response = requests.get(self._url, headers=self._headers)
            for r in response.json()['rows']:
                ret.append(r)
            while response.json()['total'] > len(ret):
                offset += self._limit
                temp_url = self._url + '&offset=' + str(offset)
                response = requests.get(temp_url,
                                        headers=self._headers)
                for r in response.json()['rows']:
                    ret.append(r)
            return ret
        except:
            return None
    
    def count(self):
        try:
            response = requests.get(
                self._snipe_url + self._endpoint, 
                headers=self._headers
            )
            return response.json()['total']
        except:
            return None
        

    
    def get_snipe_url(self):
        return self._snipe_url

