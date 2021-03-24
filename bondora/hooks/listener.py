# -*- coding: utf-8 -*-
"""The file contains functions for listening to Bondora webhooks."""

import os
import sys
import inspect
import json
import configparser
from flask import Flask, request, Response

currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from setup_logger import logger
from trading.bondora_trading import BondoraTrading


PATH_SETTINGS = '/var/www/flask/bondora/settings.cfg'
PATH_DATA = '/var/www/flask/bondora'

# read configuration
try:
    logger.info('Reading configuration from {}...'.format(PATH_SETTINGS))
    config = configparser.ConfigParser()
    config.read_file(open(PATH_SETTINGS))

    USER_NAME = config.get('BONDORA', 'USER2')

except Exception as e:
    logger.critical(e)
    sys.exit(-1)

trading = BondoraTrading(USER_NAME)

app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def responder():
    """
    Listen to webhooks.

    Returns
    -------
    response : flask.Response object
            Response object that is used by default in Flask.

    """
    response = Response(status=200)
    try:
        loan_data = request.get_json(force=True, silent=True)
        trading.buy_red_loan(loan_data)
        trading.buy_green_loan(loan_data)
        with open(PATH_DATA + '/data_{}.json'.format(USER_NAME[0:5]),
                  'w', encoding='utf-8') as outfile:
            json.dump(loan_data, outfile, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.critical(e)
        response = Response(status=400)

    return response
