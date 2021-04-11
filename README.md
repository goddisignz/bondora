# Bondora
Trading on [Bondora](https://www.bondora.com/en) marketplace including API, webhooks listener, and analytics.

Bondora as a leading Estonian marketplace for peer-to-peer consumer lending has a well-established secondary market and provides historical data on all secondary market transactions in a transparent way.

## Usage
### Installation
TO DO

### Project structure
The project is organized as follows:
```
.
├── api
│   ├── bondora_api.py
│   └── urls.py
├── examples
│   ├── offer_green_loans.py
│   ├── offer_red_loans.py
│   └── reset_webhooks.py
├── hooks
│   ├── application.py
│   ├── hooks.wsgi
│   └── listener.py
├── trading
│   └── bondora_trading.py
├── settings.cfg
└── setup_logger.py
```
* The folder `api` contains a low-level Python wrapper of the official Bondora API:
  * `bondora_api.py` - Python wrapper class
  * `urls.py` - collection of API endpoints
* The folder `examples` contains a few examples of using this project:
  * `offer_green_loans.py` - how to offer current (green) loans for selling on the secondary market
  * `offer_red_loans.py` - how to offer defaulted (red) loans for selling on the secondary market
  * `reset_webhooks.py` - how to unblock a webhook endpoint, if it has been blocked by Bondora. Bondora blocs a webhook endpoint after generating 25 errors as a response to the POST request.
* The folder `hooks` contains functionality required for receiving and proceeding webhook notifications from Bondora:
  * `application.py` - TO DO
  * `hooks.wsgi` - TO DO
  * `listener.py` - TO DO
*  The folder `trading` contains high-level Python class for communication with the official Bondora API:
  * `bondora_trading.py` - TO DO
* `settings.cfg` - project settings file
* `setup_logger.py` - logger class

### Functionality
#### API
TO DO

#### Trading
TO DO

#### Hooks
TO DO

#### Examples
TO DO

## Important Risk Disclosure
Any investment carries the risk of a total loss of the invested amount or even to additional payments. Therefore, it is not suitable for everyone. Any decision for a particular investment should be based solely on your own trading objectives. The usage of this trading system is at your own risk!

## License
MIT License
