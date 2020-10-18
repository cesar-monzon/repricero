import ebaysdk.trading
import json


def build_request(creds):
    
    required = ('ebay_config',
                'ebay_appid',
                'ebay_domain',
                'ebay_certid',
                'ebay_devid')

    if not all([x in creds for x in required]): raise

    request = ebaysdk.trading.Connection(config_file=creds['ebay_config'],
                                        appid=creds['ebay_appid'],
                                        domain=creds['ebay_domain'],
                                        certid=creds['ebay_certid'],
                                        devid=creds['ebay_devid'],
                                        timeout=20)

    return request


def send_request(creds, operation, params):
    
    api = build_request(creds)
    response = api.execute(operation, params)
    assert(hasattr(response, 'json'))
    response = response.json()
    
    return json.loads(response)


def filter_untracked(orders):
    """ Filters orders to those with no tracking
        Args:
            orders: shipped and unshipped orders
        Returns:
            order-ids that need tracking
    """
    
    if 'OrderArray' in orders and 'Order' in orders['OrderArray']:
        orders = orders['OrderArray']['Order']
    else:
        orders = []
        
    need_tracking = []
    
    for order in orders:
        
        if 'OrderLineItemID' not in order:
            continue
        try:
            tracking = order['ShippingDetails']['ShipmentTrackingDetails']['ShipmentTrackingNumber']
        except:
            need_tracking.append(order['OrderLineItemID'])

    return need_tracking

