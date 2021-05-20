from . import *

class SlackInstance(APIInstance):
    def __init__(self, bearer):
        APIInstance.__init__(self, url="https://slack.com/api", bearer=bearer)

    def call_api(self, url, post_fields=None):
        response = super().call_api(url, post_fields=post_fields)
        return response

    def post_message(self, response_channel, message):
        logging.debug("Sending message to slack:{}".format(message))
        response = self.call_api("chat.postMessage", post_fields={"channel":response_channel, "text":message})
        logging.debug("Slack response: {}".format(response.read()))

class message_builder:
    def woocommerce_product(product):
        return_message =
        { "blocks" : [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "PRODUCTS"
                    },
                "accessory": {
                    "type": "image",
                    "image_url": "https://s3-media2.fl.yelpcdn.com/bphoto/korel-1YjNtFtJlMTaC26A/o.jpg",
                    "alt_text": "alt text for image"
                    }
                }
            ]
         }
        return return_message
        
        
