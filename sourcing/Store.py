
import grequests
import pickle

class Store:

    FN = ""
    PID_LIMIT = 35
    REQ_LIMIT = 50
    STORE_LIMIT = 10
    TIMEOUT = 80
    PROXIES = dict()
    
    def __init__(self, min_price, max_price):
        self.min_price = min_price
        self.max_price = max_price
        self.headers = ''
        self.url = ''
        self.product_ids = dict()
        self.stores = dict()
        self.param_batches = list()
        self._get_proxies(self)
        self._get_headers(self)
        return

    def _get_proxies(self):
        return

    def _get_headers(self):
        return

    def get_param_generator(self):
        num_ids = len(self.product_ids)
        num_stores = len(self.stores)
        params = []

        for product_range in range(0, num_ids, PID_LIMIT) :
            for store_range in range(0, num_stores, STORE_LIMIT):

                pids = (',').join(self.product_ids[product_range : product_range + PID_LIMIT])
                stores = (',').join(self.stores[store_range : store_range + STORE_LIMIT])
                params.append({'productId': pids, 'storeNumber': stores})

                if len(params >= REQ_LIMIT):
                    yield params
                    params = []    
        return params

    def process_item_json(self, item_json):

        try:
            prod_id = item_json['productId'].strip()
            store_num = item_json['storeNumber']
            price_fields = item_json['price']
            price_selling = price_fields['selling']

            price_retail = 0
            for key in ['retail', 'was', 'map']:
                if key in price_fields and float(price_fields[key]) > price_retail:
                    price_retail = float(price_fields[key])

            avail_quant = 0
            avalable_responses = item_json['availability']

            for resp in avalable_responses:
                if 'storeNumber' not in resp or (resp['availabilityStatus'] != 'Available'): 
                    continue
                store_avail = int(resp['availabileQuantity'])
                if store_avail > avail_quant: avail_quant = store_avail

        except KeyError:
            return []

        return [prod_id, price_selling, price_retail, avail_quant, store_num, self.stores[store_num]]

    def send_requests(self):

        for params in get_param_generator():
            reqs = (grequests.get(url, params=batch, headers = self.headers, timeout = TIMEOUT) 
                    for batch in params)
            responses = grequests.map(reqs)

            if not check_responses(responses):
                continue

            for response in responses:
                json_resp = response.json()
                for item_json in json_resp:
                    item_attr = process_item_json(item_json)
                    if not item_attr: continue
                    write_item(item_attr)
        return

    def set_product_ids(self):
        product_ids = pickle.load(FN)
        return

    def check_responses(self, responses):
        return 

    def parse_json_response(self, response):
        return

    def write_item(self, item_attr):
        return