#!/opt/miniconda3/envs/flask/bin/python
# -*- coding: utf-8 -*-
"""Example how to offer current (green) loans on bondora's secondary market."""

import os
import sys
import time
import inspect
import configparser

currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from setup_logger import logger
from trading.bondora_trading import BondoraTrading

PATH_SETTINGS = '/var/www/flask/bondora/settings.cfg'

max_price = 5  # maximal selling price (5%)
min_price = 0  # minimal selling price (0%)

# read configuration
try:
    logger.info('Reading configuration from {}...'.format(PATH_SETTINGS))
    config = configparser.ConfigParser()
    config.read_file(open(PATH_SETTINGS))

    TOKEN = config.get('BONDORA', 'TOKEN')

except Exception as e:
    logger.critical(e)
    sys.exit(-1)


def offer_green_loans(token, max_price, min_price=None, retry=True):
    """
    Offer current (green) loans on bondora's secondary market for selling.

    Parameters
    ----------
    token : str
        Access token.
    max_price : int
        Maximal price to sell loan.
    min_price : int, optional
        Minimal price to sell loan. The default is None.
    retry : bool, optional
            Retry to execute the underlying methods, if too many requests.
            The default is True.

    Returns
    -------
    None.

    """
    # initialize trading object
    bt = BondoraTrading(token)

    # calcel loans with current loans status offered on secondary market
    bt.cancel_sm_offers(retry=retry,
                        LoanStatusCode=2)

    # place loans with current loans status on  secondary market for selling
    bt.place_sm_offers(max_price=max_price,
                       min_price=min_price,
                       retry=retry,
                       LoanStatusCode=2)


if __name__ == "__main__":
    offer_green_loans(TOKEN, max_price, min_price)
