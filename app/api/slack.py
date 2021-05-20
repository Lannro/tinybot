import requests
import json
import logging
import re

class SlackInstance:
    def __init__(self, bearer):
        self._bearer=bearer

    def post_message(self, channel, text, blocks = None):
        logging.debug("Sending message to slack:{}".format(text))
        response = requests.post('https://slack.com/api/chat.postMessage', {
            'token': self._bearer,
            'channel': channel,
            'text': text,
            'blocks': json.dumps(blocks) if blocks else None
            }).json()
        logging.debug("Slack response: {}".format(response))

def check_product(product):
    return True

class message_builder:
    def woocommerce_product(product):
        name = product['name']
        sold_text = " - SOLD" if product['stock_quantity'] <= 0 else ""
        sku = product['sku']
        price = str(product['price'])
        attributes = ""
        check_status = ":slightly_smiling_face:" if check_product(product) else ":slightly_frowning_face:"
        permalink = product['permalink']
        product_link = "https://shop.tinycatpottery.ca/wp-admin/post.php?post={}&action=edit".format(product['id'])
        product_url = product['images'][0]['src']
        description = product['description']
        description = re.sub(r"\<[^<>]*\>", "", description)
                
        return_message = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "{name}{sold_text}".format(name=name, sold_text=sold_text),
                    "emoji": true
                    }
                },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*SKU:* {sku}\n*Price:* ${price}\n{attributes}\n*Check Status:* {check_status}\n*Store Link:* {permalink}\n*Product Link:* {product_link}\n".format(sku=sku, price=price, attributes=attributes,check_status=check_status,permalink=permalink,product_link=product_link),
                    },
                "accessory": {
                    "type": "image",
                    "image_url": "{product_url}".format(product_url=product_url),
                    "alt_text": "alt text"
                    }
                },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "{description}".format(description=description),
                    }
                }
            ]
        return return_message
        
        
