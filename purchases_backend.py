from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from item import Item
import datetime

app = Flask(__name__)
CORS(app)

BASE_URL = "https://localhost:50000/b1s/v1"
SAP_LOGIN_PAYLOAD = {
    "CompanyDB": "SBODemoGB",
    "UserName": "manager",
    "Password": "1234"
}
HEADERS = {
    "Content-Type": "application/json"
}

# Login and get session ID
def login_to_sap():

    url = f"{BASE_URL}/Login"
    response = requests.post(url, json=SAP_LOGIN_PAYLOAD, headers=HEADERS, verify=False)
    response.raise_for_status()  # Raise an exception for HTTP errors
    session_id = response.json().get('SessionId')
    return session_id

@app.route('/business_partners', methods=['GET'])
def get_business_partners():
    global BP
    session_id = login_to_sap()
    BP_url = f"{BASE_URL}/BusinessPartners"
    BP_headers = {'Cookie': 'B1SESSION=' + session_id}
    BP_response = requests.get(BP_url, headers=BP_headers, verify=False)
    BP = BP_response.json().get('value')
    return jsonify(BP)


@app.route('/items', methods=['GET'])
def get_items():
    session_id = login_to_sap()
    items_url = f"{BASE_URL}/Items"
    items_headers = {'Cookie': 'B1SESSION=' + session_id}
    items_response = requests.get(items_url, headers=items_headers, verify=False)
    items_data = items_response.json().get('value', [])

    items = [
        Item(
            it['ItemCode'],
            it['ItemName'],
            0,  # Default quantity to 0
            it.get('ItemPrices', [{}])[0].get('Price', 0),  # Default price to 0
            it.get('ItemPreferredVendors', [{}])[0].get('BPCode', 'Unknown BPCode')
        )
        for it in items_data
    ]

    items_json = [
        {
            "ItemCode": item.get_item_code(),
            "ItemName": item.get_item_name(),
            "Quantity": item.get_quantity(),
            "Price": item.get_price(),
            "PrefVendor": item.get_pref_vendor()
        }
        for item in items
    ]

    return jsonify(items_json)

@app.route('/purchase_order', methods=['POST'])
def create_purchase_order():
    session_id = login_to_sap()
    item_shopping_list_data = request.json.get('items')

    # Fetch all items to match
    items_url = f"{BASE_URL}/Items"
    items_headers = {'Cookie': 'B1SESSION=' + session_id}
    items_response = requests.get(items_url, headers=items_headers, verify=False)
    items_data = items_response.json().get('value', [])

    # Map to find item details by name (case-insensitive)
    item_map = {
        it['ItemName'].strip().lower(): {
            'ItemCode': it['ItemCode'],
            'PrefVendor': it.get('ItemPreferredVendors', [{}])[0].get('BPCode', 'Unknown BPCode')
        }
        for it in items_data
    }

    # Create Item instances from the provided data
    item_shopping_list = [
        Item(
            item_map.get(item['item'].strip().lower(), {}).get('ItemCode', 'Unknown ItemCode'),
            item['item'],  # Item name as provided
            item['quantity'],
            item['totalItemPrice'] / item['quantity'] if item['quantity'] > 0 else 0,  # Calculate price per unit
            item_map.get(item['item'].strip().lower(), {}).get('PrefVendor', 'None'),
        )
        for item in item_shopping_list_data
    ]

    # Group items by their preferred vendor
    vendor_groups = {}
    for item in item_shopping_list:
        vendor = item.get_pref_vendor()
        if vendor not in vendor_groups:
            vendor_groups[vendor] = []
        vendor_groups[vendor].append(item)

    purchase_order_url = f"{BASE_URL}/PurchaseOrders"
    purchase_order_headers = {'Cookie': 'B1SESSION=' + session_id}
    purchase_order_response = []

    # Create a purchase order for each vendor
    for vendor, items in vendor_groups.items():
        document_lines = [
            {
                "ItemCode": item.get_item_code(),
                "Quantity": item.get_quantity(),
                "Price": item.get_price(),
                "TaxCode": 'T1'  # Assuming tax code is 'T1'
            }
            for item in items
        ]

        purchase_order_payload = {
            "CardCode": vendor,
            "DocDate": datetime.datetime.now().strftime('%Y-%m-%d'),
            "DocumentLines": document_lines
        }

        response = requests.post(purchase_order_url, json=purchase_order_payload, headers=purchase_order_headers,
                                 verify=False)
        purchase_order_response.append(response.json())

    return jsonify(purchase_order_response)


@app.route('/goods_receipt_po', methods=['POST'])
def create_goods_receipt_po():
    session_id = login_to_sap()
    deliveries = request.json.get('deliveries')  # Expecting a list of delivery data
    print(deliveries)
    goods_receipt_url = f"{BASE_URL}/PurchaseDeliveryNotes"
    goods_receipt_headers = {'Cookie': 'B1SESSION=' + session_id}
    goods_receipt_response = []

    for delivery in deliveries:
        vendor = delivery['CardCode']
        document_lines = [{"ItemCode": item['ItemCode'], "Quantity": item['Quantity']} for item in
                          delivery['DocumentLines']]

        goods_receipt_payload = {
            "CardCode": vendor,
            "DocDate": datetime.datetime.now().strftime('%Y-%m-%d'),
            "DocumentLines": document_lines,
            "BaseEntry": delivery['DocEntry'],
        }
        print(goods_receipt_payload)
        response = requests.post(goods_receipt_url, json=goods_receipt_payload, headers=goods_receipt_headers,
                                 verify=False)
        goods_receipt_response.append(response.json())

    return jsonify(goods_receipt_response)


@app.route('/ap_invoice', methods=['POST'])
def create_ap_invoice():
    session_id = login_to_sap()
    vendor_items_map = request.json.get('vendor_items_map')
    ap_invoice_url = f"{BASE_URL}/PurchaseInvoices"
    ap_invoice_headers = {'Cookie': 'B1SESSION=' + session_id}
    ap_invoice_response = []

    for vendor, items in vendor_items_map.items():
        document_lines = [{"ItemCode": item_code, "Quantity": quantity} for item_code, quantity in items.items()]

        ap_invoice_payload = {
            "CardCode": vendor,
            "DocDate": datetime.datetime.now().strftime('%Y-%m-%d'),
            "DocumentLines": document_lines
        }
        response = requests.post(ap_invoice_url, json=ap_invoice_payload, headers=ap_invoice_headers, verify=False)
        ap_invoice_response.append(response.json())

    return jsonify(ap_invoice_response)

@app.route('/payment', methods=['POST'])
def create_payment():
    session_id = login_to_sap()
    successful_ap_invoices = request.json.get('ap_invoices')
    payment_url = f"{BASE_URL}/VendorPayments"
    payment_headers = {'Cookie': 'B1SESSION=' + session_id}
    payment_response = []

    for ap_invoice in successful_ap_invoices:
        payment_payload = {
            "CardCode": ap_invoice['CardCode'],
            "PaymentInvoices": [
                {
                    "DocEntry": ap_invoice['DocEntry']
                }
            ]
        }
        response = requests.post(payment_url, json=payment_payload, headers=payment_headers, verify=False)
        payment_response.append(response.json())

    return jsonify(payment_response)

if __name__ == '__main__':
    app.run(debug=True)
