import datetime
import ebaysdk
import gql
import json
import requests
import sys


def get_token(creds):
    """ Log in and extract shiphero api token
        Args:
            creds: dict of credentials
    """
    
    header = {"Content-Type": "application/json"}
    url = creds["login_url"]
    submit_creds = ('{"username":"%s","password":"%s"}'
        % (creds["username"], creds["password"]))
        
    req = requests.post(url, headers = header, data = submit_creds)
    
    if hasattr(req, "json") and "access_token" in req.json():
        token = req.json()["access_token"]
    else:
        token = ""

    return token


def send_query(query, token, creds):
    """ Sends account request query to shiphero api
        Args:
            query: all ebay orders both shipped and unshipped
            token: token needed for api requests
            creds: dict of credentials
        Returns:
            boolean of request success
    """
    
    conn = RequestsHTTPTransport(url = creds["api_url"], use_json = True,)
    conn.headers = {
        "User-Agent" : creds["user_agent"],
        "Authorization": "Bearer {}".format(token),
        "content-type": "application/json",
    }
    
    client = Client(transport = conn, fetch_schema_from_transport = True,)
    query = gql(query)
    
    return client.execute(query)


def get_order_info(orders):
    """Get order items ready for fulfillment request
    Args:
        orders: list completed ebay orders
    Returns:
        shippable_orders: orders info formatted and ready for request
    """
    
    ready_orders = []
     
    for order in orders:

        try:
            items_ordered = order['TransactionArray']['Transaction'][0]['Item']['ItemID']
            order_id = order['OrderID']
            address = order['ShippingAddress']
        except KeyError:
            continue
        
        needed_address = ('Name','Street1','Street2','CityName',
                          'StateOrProvince','PostalCode')
        
        if not all([x in address for x in needed_address]):
            continue
        
        packing_slip = []
        do_not_send = False

        for item in items_ordered:
            
            if 'QuantityPurchased' not in item:
                continue
            quantity = item['QuantityPurchased']
            
            sku = ''
            if 'SKU' in item['Item']:
                sku = item['Item']['SKU']
            item_id = item['Item']['ItemID']
            item_specs = ebay.get_item_info(creds, item_id)
            barcode = 'Unknown'
            if('ItemSpecifics' in item_specs 
            and 'NameValueList' in item_specs['ItemSpecifics']):

                for attribute in item_specs['ItemSpecifics']['NameValueList']:
                    
                    if 'Name' not in attribute: continue
                    if(attribute['Name'] == 'UPC' and 'Value' in attribute
                    and attribute['Value'] != 'Does not apply'):
                        barcode = attribute['Value']
                        break
                    
            if barcode == 'Unknown' and not sku:
                do_not_send = True
                break
            
            packing_slip.append([sku,barcode,quantity])
                
        if do_not_send: continue
        ready_orders.append([order_id, address, packing_slip])

    return ready_orders

