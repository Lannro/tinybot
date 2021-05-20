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
                    "emoji": True
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
    
    def woocommerce_order(order):
        order_id = order['id']
        status = order['status']
        items_purchased = []
        for item in order['line_items']:
            items_purchased.append({"type": "mrkdwn",
                                    "text": "*{product_name} ({product_id})*\n*SKU:* {product_sku}\n<https://shop.tinycatpottery.ca/wp-admin/post.php?post={product_id}&action=edit|Product Link>".format(product_name=item['name'],
                                                                                                                                                                                                          product_id=item['product_id'],
                                                                                                                                                                                                          product_sku=item['sku'],)})
        customer_name= "{} {}".format(order['billing']['first_name'], order['billing']['last_name'])
        customer_id  = order['customer_id']
        note = "*note:* _{}_".format(order['customer_note']) if order['customer_note'] else ""

        billing_address = "{}\n".format(customer_name)
        for key in order['billing']:
            if key == 'first_name' or key == 'last_name':
                continue
            if not order['billing'][key]:
                continue
            billing_address += "{}\n".format(str(order['billing'][key]))
            
        shipping_address = "{}\n".format(customer_name)
        for key in order['shipping']:
            if key == 'first_name' or key == 'last_name':
                continue
            if not order['shipping'][key]:
                continue
            shipping_address += "{}\n".format(str(order['shipping'][key]))

        
        return_message = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "{order_id} - {status}".format(order_id=order_id,status=status),
                    "emoji": True
                    }
                },
            {
                "type": "divider"
                },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Items purchased*"
                    }
                },
            {
                "type": "section",
                "fields": items_purchased,
                },
            {
                "type": "divider"
                },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*{customer_name}*\n*Customer_id:* {customer_id}\n{note}".format(customer_name=customer_name, customer_id=customer_id, note=note)
                    }
                },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "*Billing Address*\n{billing_address}".format(billing_address=billing_address)
                        },
                    {
                        "type": "mrkdwn",
                        "text": "*Shipping Address*\n{shipping_address}".format(shipping_address=shipping_address)
                        }
                    ]
                }
            ]
        return return_message
        
        
