# -*- coding: utf-8 -*-
"""The file contains the class definition of Bondora trading."""

import os
import sys
import inspect
import urllib3
import time
from datetime import date, datetime, timedelta
from setup_logger import logger

currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from setup_logger import logger
from api.bondora_api import BondoraApi

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PATH_DATA = '/var/www/flask/bondora'


class BondoraTrading(BondoraApi):
    """Class representation of trading on Bondora."""

    def __init__(self, user):
        self.user = user
        BondoraApi.__init__(self, self.user)

    def bid_loan(self, auction):
        """
        Make bid into specified auction.

        Parameters
        ----------
        hook : dict
            Loan related data with summary, collection process, and schedules.

        Returns
        -------
        None.

        """
        loan_selector = False
        try:
            # get payload
            if 'EventType' not in auction:
                return None
            else:
                if auction['EventType'] != 'auction.published':
                    return None
                else:
                    payload = auction['Payload']

            if loan_selector:
                self.bid_on_auction([payload['AuctionId']], 5)
                today = datetime.now()
                with open(PATH_DATA + '/bid_{}.log'.format(
                        self.user[0:5]), 'a') as outfile:
                    outfile.write(
                        (today + timedelta(seconds=0*60*60)
                         ).strftime(
                             '%d.%m.%Y %H:%M:%S') + ': Try to invest 5 EUR\n')

        except Exception as e:
            logger.error(e)

    def buy_green_loan(self, loan):
        """
        Buy green loan on secondary market, if buying conditions are satisfied.

        Parameters
        ----------
        loan : dict
            Loan related data with summary, collection process, and schedules.

        Returns
        -------
        None.
        """
        loan_selector = False
        today = datetime.now()
        try:
            # get payload
            if 'EventType' not in loan:
                return None
            else:
                if loan['EventType'] not in ['secondmarket.published',
                                             'secondmarket.updated']:
                    return None
                else:
                    payload = loan['Payload']

            # check buying conditions
            loan_selector = False # define trading conditions here

            if loan_selector:
                self.buy_on_secondarymarket([payload['Id']])
                with open(PATH_DATA + '/buy_green_{}.log'.format(
                        self.user[0:5]), 'a') as outfile:
                    outfile.write(
                        (today + timedelta(seconds=0*60*60)
                         ).strftime('%d.%m.%Y %H:%M:%S') + ': Try to invest ' +
                        str(payload['Price']) +
                        ' EUR in ' + payload['LoanPartId'] +
                        ' on the secondary market with discount ' +
                        str(payload['DesiredDiscountRate']) + '\n')

        except Exception as e:
            logger.error(e)

    def buy_red_loan(self, loan):
        """
        Buy red loan on secondary market, if buying conditions are satisfied.

        Parameters
        ----------
        loan : dict
            Loan related data with summary, collection process, and schedules.

        Returns
        -------
        None.

        """
        loan_selector = False
        today = datetime.now()
        try:
            # get payload
            if 'EventType' not in loan:
                return None
            else:
                if loan['EventType'] not in ['secondmarket.published',
                                             'secondmarket.updated']:
                    return None
                else:
                    payload = loan['Payload']

            # check buying conditions
            loan_selector = False # define trading conditions here

            if loan_selector:
                self.buy_on_secondarymarket([payload['Id']])
                with open(PATH_DATA + '/buy_red_{}.log'.format(
                        self.user[0:5]), 'a') as outfile:
                    outfile.write(
                        (today + timedelta(seconds=0*60*60)
                         ).strftime('%d.%m.%Y %H:%M:%S') + ': Try to invest ' +
                        str(payload['Price']) +
                        ' EUR in ' + payload['LoanPartId'] +
                        ' on the secondary market with discount ' +
                        str(payload['DesiredDiscountRate']) + '\n')

        except Exception as e:
            logger.error(e)
