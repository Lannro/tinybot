import requests
import json

class SlackInstance:
    def __init__(self, bearer):
        self._bearer=bearer

    def post_message(self, channel, text, blocks = None):
        return requests.post('https://slack.com/api/chat.postMessage', {
            'token': self._bearer,
            'channel': channel,
            'text': text,
            'blocks': json.dumps(blocks) if blocks else None
        }).json()

class message_builder:
    def woocommerce_product(product):
        return_message = { "blocks" : [
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
            ]}
        return return_message
        
        
