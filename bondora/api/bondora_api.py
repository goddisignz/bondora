# -*- coding: utf-8 -*-
"""The file contains the class definition of Bondora API."""

import json
import requests
import urllib3
import api.urls
from datetime import date, datetime, timedelta
from setup_logger import logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BondoraApi:
    """Class representation of Bondora API."""

    def __init__(self,
                 user,
                 url_api=api.urls.URL_BONDORA_API,
                 url_balance=api.urls.URL_BONDORA_BALANCE,
                 url_buy_sm=api.urls.URL_BONDORA_BUY_SM):
        self.user = user
        self.url_api = url_api
        self.url_balance = url_balance
        self.url_buy_sm = url_buy_sm
        self.balance = None
        self.headers = {'User-Agent':
                        ('Mozilla/5.0 (X11; Linux x86_64) '
                         'AppleWebKit/537.11 (KHTML, like Gecko) '
                         'Chrome/23.0.1271.64 Safari/537.11'),
                        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                        'Accept-Encoding': 'none',
                        'Accept-Language': 'en-US,en;q=0.8',
                        'Connection': 'keep-alive',
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer {}'.format(self.user)}

    def post(self, url, content):
        """
        Make a POST request to the specified url.

        Parameters
        ----------
        url : str
            URL of the request.
        content : dict
            Content to send as a query string.

        Returns
        -------
        response : requests.Response object
            Response of server to the request.

        """
        response = None
        try:
            response = requests.post(self.url_api + '/{}'.format(url),
                                     headers=self.headers,
                                     data=json.dumps(content))
        except Exception as e:
            logger.error(e)

        return response

    def get(self, url, content=None):
        """
        Make a GET request to the specified url.

        Parameters
        ----------
        url : str
            URL of the request.
        content : dict
            Content to send to the specified URL.

        Returns
        -------
        response : requests.Response object
            Response of server to the request.

        """
        response_json = None
        try:
            response = requests.get(self.url_api + '/{}'.format(url),
                                    headers=self.headers,
                                    data=json.dumps(content))
            # check if response ok
            if response.status_code == requests.codes.ok:
                response_json = json.loads(response.content)

            # response is not ok
            else:
                logger.error('Response status code: {}'
                             .format(response.status_code))

        except Exception as e:
            logger.error(e)

        return response_json

    def get_balance(self):
        """
        Get balance of the account.

        Returns
        -------
        None.

        """
        try:
            balance = self.get(self.url_balance)['Payload']['TotalAvailable']
            self.balance = float(balance)
        except Exception as e:
            logger.error(e)

    def buy_on_secondarymarket(self, ids):
        """
        Buy loans from secondary market by loans IDs.

        Parameters
        ----------
        ids : list
            List of loans IDs to buy.

        Returns
        -------
        response : requests.Response object
            Response of server to the request.

        """
        json_ids = json.dumps({'ItemIds': ids})
        response = self.post(self.url_buy_sm, json_ids)
        return response
