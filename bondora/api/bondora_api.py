# -*- coding: utf-8 -*-
"""The file contains the class definition of Bondora API."""

import json
import requests
import urllib3
import inspect
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
                 url_investments=api.urls.URL_BONDORA_INVESTMENTS,
                 url_eventlog=api.urls.URL_BONDORA_EVENTLOG,
                 url_auctions=api.urls.URL_BONDORA_AUCTIONS,
                 url_bid_auction=api.urls.URL_BONDORA_BID_AUCTION,
                 url_sm=api.urls.URL_BONDORA_SM,
                 url_loan_parts=api.urls.URL_LOAN_PARTS,
                 url_buy_sm=api.urls.URL_BONDORA_BUY_SM,
                 url_sell_sm=api.urls.URL_BONDORA_SELL_SM,
                 url_cancel_sm=api.urls.URL_BONDORA_CANCEL_SM):
        self.user = user
        self.url_api = url_api
        self.url_balance = url_balance
        self.url_investments = url_investments
        self.url_eventlog = url_eventlog
        self.url_auctions = url_auctions
        self.url_bid_auction = url_bid_auction
        self.url_sm = url_sm
        self.url_loan_parts = url_loan_parts
        self.url_buy_sm = url_buy_sm
        self.url_sell_sm = url_sell_sm
        self.url_cancel_sm = url_cancel_sm
        self.balance = None
        self.investments = None
        self.eventlog = None
        self.sm = None
        self.loan_parts = None
        self.retry = {}
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

    def get(self, url, params=None, data=None):
        """
        Make a GET request to the specified url.

        Parameters
        ----------
        url : str
            URL of the request.
        params : dict
            Parameters to pass in URL.

        Returns
        -------
        response : requests.Response object
            Response of server to the request.

        """
        response_json = None
        try:
            response = requests.get(self.url_api + '/{}'.format(url),
                                    headers=self.headers,
                                    params=params)

            # check if response ok
            if response.status_code == requests.codes.ok:
                response_json = json.loads(response.content)

            # response is not ok
            else:
                logger.error('Response status code: {}'
                             .format(response.status_code))
                # if too many requests
                if response.status_code == requests.codes.too_many_requests:
                    # get wait time
                    response_json = json.loads(response.content)
                    wait_time = int(
                        response_json['Errors'][0]['Details'].split()[2])
                    # get caller name
                    caller = inspect.stack()[1][3]
                    self.retry[caller] = wait_time

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
            balance = self.get(self.url_balance)
            if 'Payload' not in balance:
                return None
            self.balance = float(balance['Payload']['TotalAvailable'])
        except Exception as e:
            logger.error(e)

    def get_investments(self, **kwargs):
        """
        Get list of investments.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments:
                Request information (see
                https://api.bondora.com/doc/Api/GET-api-v1-account-investments?v=1).

        Returns
        -------
        None.

        """
        try:
            investments = self.get(self.url_investments, params=kwargs)
            if 'Payload' not in investments:
                return None
            self.investments = investments['Payload']
        except Exception as e:
            logger.error(e)

    def get_eventlog(self, **kwargs):
        """
        Get events that have been made with this application.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments:
                Request information (see
                https://api.bondora.com/doc/Api/GET-api-v1-eventlog?v=1).

        Returns
        -------
        None.

        """
        try:
            eventlog = self.get(self.url_eventlog, params=kwargs)
            if 'Payload' not in eventlog:
                return None
            self.eventlog = eventlog['Payload']
        except Exception as e:
            logger.error(e)

    def get_auctions(self, **kwargs):
        """
        Get list of active auctions.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments:
                Request information (see
                https://api.bondora.com/doc/Api/GET-api-v1-auctions?v=1).

        Returns
        -------
        None.

        """
        try:
            auctions = self.get(self.url_auctions, params=kwargs)
            if 'Payload' not in auctions:
                return None
            self.auctions = auctions['Payload']
        except Exception as e:
            logger.error(e)

    def bid_on_auction(self, ids, amount):
        """
        Make bid into auctions by auction IDs.

        Parameters
        ----------
        ids : list
            List of auction IDs to bid.
        amount : int
            Amount to bid.

        Returns
        -------
        response : requests.Response object
            Response of server to the request.

        """
        auctions_ids_list = []
        try:
            # create list of dicts
            for auction_id in ids:
                auctions_ids_list.append({'AuctionId': auction_id,
                                          'Amount': amount,
                                          'MinAmount': 1})
            response = self.post(self.url_bid_auction, {'Bids':
                                                        auctions_ids_list})
            return response

        except Exception as e:
            logger.error(e)

    def get_secondarymarket(self, **kwargs):
        """
        Get list of active secondary market items.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments:
                Request information (see
                https://api.bondora.com/doc/Api/GET-api-v1-secondarymarket?v=1).

        Returns
        -------
        None.

        """
        try:
            sm = self.get(self.url_sm, params=kwargs)
            if 'Payload' not in sm:
                return None
            self.sm = sm['Payload']
        except Exception as e:
            logger.error(e)

    def get_loanparts(self, ids):
        """
        Get loan part info.

        Parameters
        ----------
        ids : list
            List of loan part IDs.

        Returns
        -------
        None.

        """
        try:
            json_ids = json.dumps({'ItemIds': ids})
            loan_parts = self.post(self.url_loan_parts, content=json_ids)
            if 'Payload' not in loan_parts:
                return None
            self.loan_parts = loan_parts['Payload']
        except Exception as e:
            logger.error(e)

    def buy_on_secondarymarket(self, ids):
        """
        Buy loans from secondary market by loans IDs.

        Parameters
        ----------
        ids : list
            List of secondary market item IDs to buy.

        Returns
        -------
        response : requests.Response object
            Response of server to the request.

        """
        try:
            response = self.post(self.url_buy_sm, {'ItemIds': ids})
            return response

        except Exception as e:
            logger.error(e)

    def sell_on_secondarymarket(self, loans,
                                cancel_on_payment=False,
                                cancel_on_reschedule=False):
        """
        Sell loans on secondary market.

        Parameters
        ----------
        loans : list
            List of tuples (LoanPartId, DesiredDiscountRate) to sell.
        cancel_on_payment : bool, optional
            Allow to auto cancel the selling of loans
            if they receive new repayments. The default is False.
        cancel_on_reschedule : bool, optional
            Allow to auto cancel the selling of loans
            if they are rescheduled. The default is False.

        Returns
        -------
        response : requests.Response object
            Response of server to the request.

        """
        loans_ids_list = []
        try:
            # create list of dicts
            for loan in loans:
                loans_ids_list.append({'LoanPartId': loan[0],
                                       'DesiredDiscountRate': loan[1]})
            loans_dict = {'Items': loans_ids_list,
                          'CancelItemOnPaymentReceived': cancel_on_payment,
                          'CancelItemOnReschedule': cancel_on_reschedule}
            response = self.post(self.url_sell_sm, loans_dict)
            return response

        except Exception as e:
            logger.error(e)

    def cancel_on_secondarymarket(self, ids):
        """
        Sell loans on secondary market.

        Parameters
        ----------
        ids : list
            List of secondary market item IDs to cancel.

        Returns
        -------
        response : requests.Response object
            Response of server to the request.

        """
        try:
            response = self.post(self.url_cancel_sm, {'ItemIds': ids})
            return response

        except Exception as e:
            logger.error(e)
