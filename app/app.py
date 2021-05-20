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

_SLACK_BOT_USER_OATH = os.environ["SLACK_BOT_USER_OATH"]
_SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
_WOO_SITE_URL = os.environ["SITE_URL"]
_WOO_USERNAME = os.environ["USERNAME"]
_WOO_PASSWORD = os.environ["PASSWORD"]

app = Flask(__name__)

woo = None

def verify_product(product):
    errors = []
    if not product['name']:
        errors.append("product_missing_name")
    if 'Commission' in product['name']:
        return False
    if not product['manage_stock']:
        errors.append("stock_is_not_managed")
    if not product['sold_individually']:
        errors.append("not_sold_individually")
    if not product['weight']:
        errors.append("missing_weight")
    if not product['dimensions']:
        errors.append("missing_dimensions")
    else:
        if not product['dimensions']['length']:
            errors.append("missing_dimensions")
        elif not product['dimensions']['width']:
            errors.append("missing_dimensions")
        elif not product['dimensions']['height']:
            errors.append("missing_dimensions")
    if not errors:
        return False
    return {'id':product['id'], 'errors':errors}


def check_products(response_channel):
    global woo
    logging.info("Checking products")

    products = woo.call_api("products")
    message =  "\n{} products found.\n".format(str(len(products)))
    message += "------------------------\n"
    errors = []
    for product in products:
        error = verify_product(product)
        if error:
            errors.append(error)

    if len(errors) <= 0:
        message += "No products had errors in them."
    else:
        message += "{} product(s) had errors in them.\n".format(str(len(errors)))
        for error in errors:
            message += "{}: {}\n".format(error['id'], ", ".join(error['errors']))

    logging.info("Checking products completed")
    post_message(message, response_channel)

def post_message(message, response_channel):
    logging.debug("Sending message:{}".format(message))
    webhook_url = "https://slack.com/api/chat.postMessage"
    post_data = json.dumps({"channel":response_channel, "text":message}).encode('utf-8')
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(_SLACK_BOT_USER_OATH)}
    req = urllib.request.Request(webhook_url, post_data, headers)
    resp = urllib.request.urlopen(req)
    logging.info(resp.read())
    logging.debug("Message sent")

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
    app.run(host='0.0.0.0')
    woo = WoocommerceInstance(url=_WOO_SITE_URL,username=_WOO_USERNAME,password=_WOO_PASSWORD)
