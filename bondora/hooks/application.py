# -*- coding: utf-8 -*-
"""The file contains the class definition of Bondora application."""
import sys
import requests
import urllib3
import api.urls
from bs4 import BeautifulSoup
from setup_logger import logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BondoraApplication:
    """Class representation of Bondora application."""

    def __init__(self,
                 user,
                 password,
                 application_id,
                 url_auth=api.urls.URL_BONDORA_AUTH,
                 url_button=api.urls.URL_BONDORA_BUTTON):
        self.user = user
        self.password = password
        self.application_id = application_id
        self.url_auth = url_auth
        self.url_button = url_button
        self.signedup = False
        self.webhooks = None
        self.headers = {'User-Agent':
                        ('Mozilla/5.0 (X11; Linux x86_64) '
                         'AppleWebKit/537.11 (KHTML, like Gecko) '
                         'Chrome/23.0.1271.64 Safari/537.11'),
                        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                        'Accept-Encoding': 'none',
                        'Accept-Language': 'en-US,en;q=0.8',
                        'Connection': 'keep-alive'}
        try:
            # create session
            logger.info('Creating new session...')
            self.session = requests.Session()
        except Exception as e:
            logger.critical(e)
            sys.exit(-1)

    def get_webhooks(self):
        """
        Log into Bondora's API web interface and get list of webhooks.

        Parameters
        ----------
        None.

        Returns
        -------
        None.

        """
        # check if signed up
        if self.signedup:
            logger.warning('Already signed up.')
            return None

        payload = {'userName': self.user,
                   'password': self.password,
                   'returnUrl': '/Application/Webhooks?applicationId={}'
                   .format(self.application_id)}

        try:
            auth = self.session.post(self.url_auth,
                                     headers=self.headers,
                                     data=payload)

            # check if response ok
            if auth.status_code == requests.codes.ok:
                self.signedup = True
                auth_html = BeautifulSoup(auth.content, 'html.parser')
                # get table
                table = auth_html.find('table',
                                       attrs={'class': 'table table-striped'})
                # get all rows
                trs = table.find_all('tr')
                # find positions of columns 'Name' and `Failures` in the table
                ths = trs[0].find_all('th')
                for index, th in enumerate(ths):
                    if th.text.strip() == 'Name':
                        # get column index with `Name`
                        index_name = index
                    elif th.text.strip() == 'Failures':
                        # get column index with `Failures`
                        index_failures = index
                    elif th.text.strip() == 'Info':
                        # get column index with `send test` button
                        index_button = index + 1
                # get number of failures for all webhooks
                webhooks_list = []
                for tr in trs[1:]:
                    webhook_dict = {}
                    # get all columns in the current row
                    columns = tr.find_all('td')
                    # get name of webhook
                    webhook_dict['name'] = columns[index_name].text.strip()
                    # get numbers of failures
                    webhook_dict['n_failures'] = int(
                        columns[index_failures].text.strip())
                    # get button id
                    webhook_dict['button_id'] = columns[index_button].find(
                        'form')['data-id']
                    # append dictionary to list
                    webhooks_list.append(webhook_dict)

                if webhooks_list:
                    self.webhooks = webhooks_list

            # response is not ok
            else:
                logger.critical('Login failed. Response status code: {}'
                                .format(auth.status_code))

        except Exception as e:
            logger.error(e)

    def reset_webhooks(self, threshold=10):
        """
        Reset webhooks, if the number of failures are above threshold.

        Parameters
        ----------
        threshold : int, optional
            Threshold for maximal number of failures. The default is 10.

        Returns
        -------
        None.

        """
        if self.webhooks:
            try:
                for webhook in self.webhooks:
                    # number of failures is above threshold
                    if webhook['n_failures'] > threshold:
                        # reset webhook
                        reset_response = self.session.post(
                            self.url_button + '/' + webhook['button_id'],
                            headers=self.headers)
                        # check if response ok
                        if reset_response.status_code == requests.codes.ok:
                            logger.info('Reset webhook for {}.'
                                        .format(webhook['name']))
                        # response is not ok
                        else:
                            logger.error('Response status code: {}'
                                         .format(reset_response.status_code))

            except Exception as e:
                logger.error(e)
