# Bondora
Trading on [Bondora](https://www.bondora.com/en) marketplace including API, webhooks listener, and analytics.

Bondora as a leading Estonian marketplace for peer-to-peer consumer lending has a well-established secondary market and provides historical data on all secondary market transactions in a transparent way.

## Usage
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

## Important Risk Disclosure
Any investment carries the risk of a total loss of the invested amount or even to additional payments. Therefore, it is not suitable for everyone. Any decision for a particular investment should be based solely on your own trading objectives. The usage of this trading system is at your own risk!

## License
MIT License
