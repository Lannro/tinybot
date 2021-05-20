from . import *

class WoocommerceInstance(APIInstance):
    def __init__(self, url, username, password):
        APIInstance.__init__(self, url=url, username=username, password=password)
        if 'wp-json/wc/v2' not in self._base_url:
            self._base_url = self._base_url + "/wp-json/wc/v2"
        self._urlencode=True

    def _validate_response(self, response):
        if not response:
            logging.warning("There was an unexpected error with your request")
            return False
        if type(response) == list and len(response) == 1:
            if 'message' in response[0]:
                logging.warning("There was a problem connecting to woocommerce: {}".format(response[0]['message']))
                return False
        return response        

    def call_api(self, url, is_url_absolute=False, method="GET", post_fields=None, all_pages=True, content_type="application/json"):
        response = super().call_api(url,None,is_url_absolute,method,post_fields,content_type)
        if response and all_pages and "Link" in response.headers:
            collector = []
            more_pages = True
            while more_pages:
                response_body = get_response_body(response)
                if isinstance(response_body, dict):
                    response_body = [response_body]
                collector = collector + response_body
                for link in response.headers.get("Link").split(','):
                    parts = link.split(";")
                    if parts[1].find('next') >= 0:
                        next_page = parts[0]
                        next_page = next_page.replace('<', '')
                        next_page = next_page.replace('>', '')
                        next_page = next_page.strip()
                        response = super().call_api(url=next_page,
                                                    on_behalf_of=None,
                                                    is_url_absolute=True,
                                                    method=method,
                                                    post_fields=post_fields,
                                                    content_type=content_type)
                        break
                else:
                    more_pages = False
            
            return self._validate_response(collector)
        else:
            return get_response_body(response)

    def verify_products(self, products):
        errors = []
        for product in products:
            error = self._verify_product(product)
            if error:
                errors.append(error)
        return errors
            
    def _verify_product(self, product):
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

    def get_products(self):
        response = self.call_api("products")
        return response
    
    def get_customer(self, customer_id):
        return self.__get_single(customer_id, "customers", "customer")

    def get_order(self, order_id):
        return self.__get_single(order_id, "orders", "order")
    
    def get_product(self, product_id):
        return self.__get_single(product_id, "products", "product")

    def __get_single(self, single_id, single_url, single_name):
        logging.debug("Getting {}_id:{}".format(single_name, single_id))
        response = self.call_api("{}/{}".format(single_url, single_id))
        if not response:
            logging.warning("Could not get {}_id:{}".format(single_name, single_id))
            return
        if type(response) != list or len(response) != 1 or 'id' not in response[0]:
            loggin.warning("Unexpected response from {}/{}".format(single_url, single_id))
            return
        logging.debug("{}_id:{} retrieved".format(single_name, single_id))
        return response[0]
