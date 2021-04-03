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
            today = datetime.now()
            next_pm_date = date.fromisoformat(payload['NextPaymentDate'][:10])
            pm_date_min = (today + timedelta(days=10)).date()
            loan_selector = (
                payload['NextPaymentNr'] == 1
                and
                payload['DesiredDiscountRate'] <= 1.0
                and
                payload['LoanStatusCode'] == 2
                and
                not payload['ReScheduledOn']
                and
                not payload['DebtOccuredOn']
                and
                not payload['DebtOccuredOnForSecondary']
                and
                payload['LateAmountTotal'] == 0.0
                and
                payload['Amount'] <= 5.0
                and
                payload['Interest'] > 12.0
                and
                payload['NrOfScheduledPayments'] > 36
                and
                next_pm_date > pm_date_min
                )

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
            #logger.error(e)
            pass

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
            loan_selector = (
                payload['DesiredDiscountRate'] <= -94.0
                and
                payload['Price'] <= 5.0
                )

            if loan_selector:
                self.buy_on_secondarymarket([payload['Id']])
                today = datetime.now()
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
            #logger.error(e)
            pass

    def cancel_sm_offers(self, retry=False, **kwargs):
        """
        Cancel selling of own loans offered on secondary market.

        Loans for canceling can be specified by the conditions defined
        in `kwargs`. See the full list of possible conditions at:
        https://api.bondora.com/doc/Api/GET-api-v1-secondarymarket?v=1

        Parameters
        ----------
        retry : bool, optional
            Retry to execute the method, if too many requests.
            The default is False.
        **kwargs : dict
            Keyword arguments:
                Loans conditions to cancel.

        Returns
        -------
        None.

        """
        # wait 1 second before proceed
        time.sleep(1)

        # select only own loans offered on secondary market
        if isinstance(kwargs, dict):
            kwargs['ShowMyItems'] = True
        else:
            kwargs = {'ShowMyItems': True}
        self.get_secondarymarket(retry, **kwargs)

        # get list of secondary market item IDs
        ids = []
        if self.sm:
            for loan_on_sm in self.sm:
                try:
                    ids.append(loan_on_sm['Id'])
                except Exception as e:
                    logger.error(e)
        else:
            if self.retry:
                if 'get_secondarymarket' in self.retry:
                    logger.warning('Too many requests. Retry after {} s.'
                                   .format(self.retry['get_secondarymarket']))
                    return None
            logger.warning('No loans satisfying provided conditions '
                           'and offered for selling were found.')
            return None

        # cancel loans offered on secondary market
        if ids:
            response = self.cancel_on_secondarymarket(ids)
            if response.status_code == 202:
                if len(ids) == 1:
                    logger.info('1 loan was successfully canceled on '
                                'secondary market.')
                else:
                    logger.info(' {} loans were successfully canceled on '
                                'secondary market.'.format(len(ids)))
            else:
                logger.error('Error by canceling loans on secondary market. '
                             'Error code: {}'.format(response.status_code))

    def place_sm_offers(self, max_price, min_price=None,
                        days_before_payment=2, retry=False, **kwargs):
        """
        Place loans for selling on secondary market.

        Loans for selling can be specified by the conditions defined
        in `kwargs`. See the full list of possible conditions at:
        https://api.bondora.com/doc/Api/GET-api-v1-account-investments?v=1
        If `min_price` is not specified, the selling price will be `max_price`.
        Otherwise, the selling price will be reduced depending on how many
        days remain between today and the next payment day.

        Parameters
        ----------
        max_price : int
            Maximal price to sell loan.
        min_price : int, optional
            Minimal price to sell loan. The default is None.
        days_before_payment : int, optional
            Latest selling date of loans before the next payment.
            The default is 2.
        retry : bool, optional
            Retry to execute the method, if too many requests.
            The default is False.
        **kwargs : dict
            Keyword arguments:
                Loans conditions to select for selling.

        Returns
        -------
        None.

        """
        # wait 1 second before proceed
        time.sleep(1)

        price = max_price
        self.get_investments(retry, **kwargs)

        # calculate latest selling date of loans before the next payment
        if min_price:
            latest_sell_date = date.today() + timedelta(
                days=days_before_payment)

        # get list of loan parts IDs and selling prices
        part_ids_prices = []
        if self.investments:
            for investment in self.investments:
                try:
                    # calculate selling price
                    if min_price:
                        next_payment_date = datetime.strptime(
                            investment['NextPaymentDate'],
                            '%Y-%m-%dT00:00:00').date()
                        price = min_price + (next_payment_date -
                                             latest_sell_date).days
                        if price > max_price:
                            price = max_price
                        elif price < min_price:
                            price = min_price
                    part_ids_prices.append((investment['LoanPartId'], price))
                except Exception as e:
                    logger.error(e)
        else:
            if self.retry:
                if 'get_investments' in self.retry:
                    logger.warning('Too many requests. Retry after {} s.'
                                   .format(self.retry['get_investments']))
                    return None
            logger.warning('No loans satisfying provided conditions '
                           'were found.')
            return None

        # sell loans on secondary market
        if part_ids_prices:
            response = self.sell_on_secondarymarket(part_ids_prices)
            if response.status_code == 202:
                if len(part_ids_prices) == 1:
                    logger.info('1 loan was successfully put on '
                                'secondary market for selling.')
                else:
                    logger.info(' {} loans were successfully put on '
                                'secondary market for selling.'
                                .format(len(part_ids_prices)))

            else:
                logger.error('Error by putting loans on secondary market. '
                             'Error code: {}'.format(response.status_code))
