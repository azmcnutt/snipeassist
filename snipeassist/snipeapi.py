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
            if response.status_code == 200:
                return response.json()['total']
            else:
                logger.critical('Error connecting to SnipeIT.  Error returned: %s',
                               response.status_code
                )
                return None
        except Exception as e:
            logger.warning(e)
            return None
    
    def create_asset(self, asset):
        logger.debug('Creating Asset:')
        logger.debug(asset)
        headers = self._headers
        headers['content-type'] = 'application/json'
        response = requests.post(self._snipe_url + self._endpoint, json=asset, headers=headers)
        logger.debug(f'Request Response Status Code: {response.status_code}')
        data = json.loads(response.text)
        if data['status'] == 'success':
            logger.debug('Snipe API Reports status success')
            if data['messages'] == 'Asset created successfully. :)':
                logger.debug('Snipe API Reports Asset created')
            else:
                logger.debug(f'Snipe API Reports: {data["messages"]}')
        else:
            logger.warn(f'Snipe API reports status: {data["status"]}')
        return data
    
    def checkout_asset(self, asset_id, checkout_type, assigned_to_id):
        checkout_type = checkout_type.lower()
        if checkout_type not in ['user', 'asset', 'location']:
            logger.warning(f'Check out type not valid: {checkout_type}.  Expected user, asset, or location')
            return {'status': 'error'}
        if checkout_type == 'user':
            assigned_type = 'assigned_user'
        elif checkout_type == 'asset':
            assigned_type = 'assigned_asset'
        elif checkout_type == 'location':
            assigned_type = 'assigned_location'
        else:
            logger.critical('Critical error occurred while assigning Check out type.')
            return {'status': 'error'}
        logger.debug('Checking out Asset:')
        logger.debug(asset_id)
        headers = self._headers
        headers['content-type'] = 'application/json'
        checkout_url = self._snipe_url + self._endpoint + '/' + str(asset_id) + '/checkout'
        payload = {
            'checkout_to_type': checkout_type,
            assigned_type: assigned_to_id,
        }
        response = requests.post(checkout_url, json=payload, headers=headers)
        logger.debug(f'Request Response Status Code: {response.status_code}')
        data = json.loads(response.text)
        if data['status'] == 'success':
            logger.debug('Snipe API Reports status success')
            if data['messages'] == 'Asset checked out successfully.':
                logger.debug('Snipe API Reports Asset Checked Out')
            else:
                logger.debug(f'Snipe API Reports: {data["messages"]}')
        else:
            logger.warn(f'Snipe API reports status: {data["status"]}')
        return data

    def get_snipe_url(self):
        return self._snipe_url
