# load the logging configuration
import logging
from logging.config import fileConfig
fileConfig('config/logging.ini')

import os
from flask import Flask, request, make_response, Response
import json
import traceback
import threading
import time
import urllib

from api.woocommerce import WoocommerceInstance
from api.slack import SlackInstance
from api.slack import message_builder

_SLACK_BOT_USER_OATH = os.environ["SLACK_BOT_USER_OATH"]
_SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
_WOO_SITE_URL = os.environ["WOO_SITE_URL"]
_WOO_USERNAME = os.environ["WOO_USERNAME"]
_WOO_PASSWORD = os.environ["WOO_PASSWORD"]

app = Flask(__name__)

woo = None
slack = None

def check_products(response_channel):
    global woo, slack
    logging.info("Checking products")

    products = woo.call_api("products")
    
    message =  "\n{} products found.\n".format(str(len(products)))
    message += "------------------------\n"
    
    errors = woo.verify_products(products)

    if len(errors) <= 0:
        message += "No products had errors in them."
    else:
        message += "{} product(s) had errors in them.\n".format(str(len(errors)))
        for error in errors:
            message += "{}: {}\n".format(error['id'], ", ".join(error['errors']))

    logging.info("Checking products completed")
    
    slack.post_message(response_channel, message)

    

@app.route("/get", methods=['POST'])
def get_request():
    try:
        if request.form['token'] != _SLACK_VERIFICATION_TOKEN:
            logging.warning("Invalid token given with request: {}".format(request.form['token']))
            return "invalid token"
        logging.info(request.form)
        #threading.Thread(target=check_products, args=(request.form['channel_id'],)).start()
        return "RETURNING TEST"

    except Exception as e:
        traceback.print_exc()
        logging.error("Unexpected error occured: {}:{}".format(type(e).__name__, e))
        return "Error checking products."
    
@app.route("/check", methods=['POST'])
def check_request():
    try:
        if request.form['token'] != _SLACK_VERIFICATION_TOKEN:
            logging.warning("Invalid token given with request: {}".format(request.form['token']))
            return "invalid token"
        logging.info(request.form)
        threading.Thread(target=check_products, args=(request.form['channel_id'],)).start()
        return "Checking products!"

    except Exception as e:
        traceback.print_exc()
        logging.error("Unexpected error occured: {}:{}".format(type(e).__name__, e))
        return "Error checking products."

if __name__ == '__main__':
    global woo, slack
    app.run(host='0.0.0.0')
    woo = WoocommerceInstance(url=_WOO_SITE_URL,username=_WOO_USERNAME,password=_WOO_PASSWORD)
    slack = SlackInstance(bearer=_SLACK_BOT_USER_OATH)
