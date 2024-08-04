from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import datetime

app = Flask(__name__)
CORS(app)

SAP_BASE_URL = "https://localhost:50000/b1s/v1"
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
    url = f"{SAP_BASE_URL}/Login"
    response = requests.post(url, json=SAP_LOGIN_PAYLOAD, headers=HEADERS, verify=False)
    response.raise_for_status()  # Raise an exception for HTTP errors
    session_id = response.json().get('SessionId')
    return session_id

# Fetch business partners
@app.route('/business-partners', methods=['GET'])
def get_business_partners():
    try:
        session_id = login_to_sap()
        url = f"{SAP_BASE_URL}/BusinessPartners"
        headers = {'Cookie': f'B1SESSION={session_id}'}
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return jsonify(response.json().get('value')), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# Fetch items
@app.route('/items', methods=['GET'])
def get_items():
    try:
        session_id = login_to_sap()
        url = f"{SAP_BASE_URL}/Items"
        headers = {'Cookie': f'B1SESSION={session_id}'}
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return jsonify(response.json().get('value')), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# Create sales order
@app.route('/create-sales-order', methods=['POST'])
def create_sales_order():
    try:
        data = request.get_json()
        bp_input = data.get('bpInput').strip().lower()
        items_data = data.get('items')

        session_id = login_to_sap()
        headers = {'Cookie': f'B1SESSION={session_id}'}

        # Fetch business partners and validate input
        bp_url = f"{SAP_BASE_URL}/BusinessPartners"
        bp_response = requests.get(bp_url, headers=headers, verify=False)
        bp_response.raise_for_status()
        business_partners = bp_response.json().get('value')

        card_code = None
        for bp in business_partners:
            if bp['CardName'].lower() == bp_input or bp['CardCode'].lower() == bp_input:
                card_code = bp['CardCode']
                break

        if not card_code:
            return jsonify({"message": "Business Partner not found"}), 404

        # Fetch items and validate input
        items_url = f"{SAP_BASE_URL}/Items"
        items_response = requests.get(items_url, headers=headers, verify=False)
        items_response.raise_for_status()
        available_items = items_response.json().get('value')

        item_shopping_list = []
        for item_data in items_data:
            item_input_code = item_data['item'].strip().lower()
            quantity = item_data['quantity']
            price = None
            for item in available_items:
                if item['ItemCode'].lower() == item_input_code or item['ItemName'].lower() == item_input_code:
                    for price_detail in item['ItemPrices']:
                        if price_detail['PriceList'] == 1:
                            price = price_detail['Price']
                            break
                    item_code=item['ItemCode']
                    break

            if price is not None:
                item_shopping_list.append({
                    "ItemCode": item_code,
                    "Quantity": quantity,
                    "Price": str(price)
                })
            else:
                return jsonify({"message": f"Price not found for item: {item_input_code}"}), 400

        due_date = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime('%Y-%m-%d')

        sales_order_url = f"{SAP_BASE_URL}/Orders"
        sales_order_payload = {
            "CardCode": card_code,
            "DocDueDate": due_date,
            "DocumentLines": item_shopping_list
        }
        print(sales_order_payload)
        sales_order_response = requests.post(sales_order_url, json=sales_order_payload, headers=headers, verify=False)
        sales_order_response.raise_for_status()

        return jsonify({"message": "Sales order created successfully", "DocEntry": sales_order_response.json().get('DocEntry'), "CardCode": sales_order_response.json().get('CardCode'), "DocDueDate": sales_order_response.json().get('DocDueDate'), "DocumentLines": item_shopping_list}), 201

    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/create-delivery', methods=['POST'])
def create_delivery():
    try:
        data = request.get_json()
        doc_entry = str(data.get('DocEntry')).strip()  # Convert to string and then strip
        items_data = data.get('DocumentLines')

        session_id = login_to_sap()
        headers = {'Cookie': f'B1SESSION={session_id}'}


        print(f"Input Sales Order: {doc_entry}")


        card_code = data.get('CardCode')
        # Fetch items and validate input
        # items_url = f"{SAP_BASE_URL}/Items"
        # items_response = requests.get(items_url, headers=headers, verify=False)
        # items_response.raise_for_status()
        # available_items = items_response.json().get('value')
        #
        # item_shopping_list = []
        # for item_data in items_data:
        #     item_input_code = item_data['item'].strip().lower()
        #     quantity = item_data['quantity']
        #     price = None
        #     for item in available_items:
        #         if item['ItemCode'].lower() == item_input_code or item['ItemName'].lower() == item_input_code:
        #             for price_detail in item['ItemPrices']:
        #                 if price_detail['PriceList'] == 1:
        #                     price = price_detail['Price']
        #                     break
        #             item_code = item['ItemCode']
        #             break
        #
        #     if price is not None:
        #         item_shopping_list.append({
        #             "ItemCode": item_code,
        #             "Quantity": quantity,
        #             "Price": str(price)
        #         })
        #     else:
        #         return jsonify({"message": f"Price not found for item: {item_input_code}"}), 400

        delivery_url = f"{SAP_BASE_URL}/DeliveryNotes"
        delivery_payload = {
            "CardCode": card_code,
            "DocEntry": doc_entry,
            "DocumentLines": items_data
        }
        print(f"Delivery Payload: {delivery_payload}")
        print(f"Delivery URL: {delivery_url}")
        print(f"Headers: {headers}")
        delivery_response = requests.post(delivery_url, json=delivery_payload, headers=headers, verify=False)
        delivery_response.raise_for_status()

        return jsonify({"message": "Delivery created successfully", "DocEntry": delivery_response.json().get('DocEntry')}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)

