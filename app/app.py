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

def get_product(response_channel, product_id):
    global woo, slack
    product = woo.get_product(product_id)
    if not product:
        logging.error("Could not retrieve product_id:{}".format(product_id))
        slack.post_message(response_channel, "Could not retrieve product_id:{}".format(product_id))
        return

    message = message_builder.woocommerce_product(product)    
    slack.post_message(response_channel, message)

@app.route("/get", methods=['POST'])
def get_request():
    try:
        if request.form['token'] != _SLACK_VERIFICATION_TOKEN:
            logging.warning("Invalid token given with request: {}".format(request.form['token']))
            return "invalid token"
        text = request.form['text']
        split = text.split(" ")
        if len(split) < 2:
            logging.error("formatting error")
            return "Formatting error!")

        get_type = split[0]
        try:
            type_id = int(split[1])
        except ValueError:
            logging.error("Invalid product id given")
            return "Error checking product: Invalid product id given"

        if get_type == "product"        
            threading.Thread(target=get_product, args=(request.form['channel_id'],product_id)).start()
            return "Retrieving product!"
        else:
            return "Sorry, I don't know how to get {} for you".format(get_type)

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
    app.run(host='0.0.0.0')
    woo = WoocommerceInstance(url=_WOO_SITE_URL,username=_WOO_USERNAME,password=_WOO_PASSWORD)
    slack = SlackInstance(bearer=_SLACK_BOT_USER_OATH)
