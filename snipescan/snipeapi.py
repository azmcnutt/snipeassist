"""A small API Interface for the things I'll need from Snipe"""
import logging
import logging.config
import json

import requests

import settings
from project import all_snipe_endpoints

MAX_LIMIT = 500

logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger(__name__)

class SnipeGet:

    def __init__(self, snipe_url, api_key, endpoint='hardware', limit=500):


        self._api_key = api_key
        self._snipe_url = snipe_url
        if endpoint in all_snipe_endpoints:
            logger.debug('New Snipe Instance for endpoint: %s', endpoint)
            self._endpoint = endpoint
        else:
            logger.error('Endpoint %s not defined, defaulting to hardware', endpoint)
            self._endpoint = 'hardware'
        if limit > MAX_LIMIT:
            logger.warning('Limit %s is higher than %s, setting to %s',
                                limit, MAX_LIMIT, MAX_LIMIT)
            limit = MAX_LIMIT
        elif limit <= 0:
            logger.warning('Limit %s is lower than 1, setting to %s',
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
        logger.debug('Getting all records for endpoint %s', self._endpoint)
        try:
            response = requests.get(self._url, headers=self._headers)
            for r in response.json()['rows']:
                ret.append(r)
            logger.debug('Received %s rows out of %s from endpoint: %s',
                         len(ret),
                         response.json()['total'],
                         self._endpoint
                         )
            while response.json()['total'] > len(ret):
                offset += self._limit
                temp_url = self._url + '&offset=' + str(offset)
                response = requests.get(temp_url,
                                        headers=self._headers)
                for r in response.json()['rows']:
                    ret.append(r)
                logger.debug('Received %s rows out of %s from endpoint: %s',
                             len(ret),
                             response.json()['total'],
                             self._endpoint
                             )
            return ret
        except:
            return None

    def get_by_id(self, snipe_id):
        try:
            response = requests.get(self._snipe_url + self._endpoint + '/' + str(snipe_id), headers=self._headers)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            logger.warning(e)
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
