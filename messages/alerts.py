import os
import admin.config as cfg
from twilio.rest import Client
import logging

logger = logging.getLogger('__name__')

def send_sms_message(message, phone_number):
    try:
        client = Client(cfg.get_config_value('twilio', 'smsAccountSID'), cfg.get_config_value('twilio', 'smsAuthToken'))
        client.messages.create(from_=cfg.get_config_value('twilio', 'smsSenderNumber'),
                            to=phone_number,
                            body=message)
    except Exception as e:
        logger.error(e)
