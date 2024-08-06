from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS

SAP_URL = "https://localhost:50000/b1s/v1/"
SESSION_ID = None

def sap_login():
    global SESSION_ID
    url = f"{SAP_URL}Login"
    payload = {
        "CompanyDB": "SBODemoGB",
        "Password": "1234",
        "UserName": "manager"
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers, verify=False)
    SESSION_ID = response.json()['SessionId']

def get_headers():
    return {'Content-Type': 'application/json', 'Cookie': f'B1SESSION={SESSION_ID}'}

@app.route('/login', methods=['POST'])
def login():
    sap_login()
    return jsonify({"message": "Logged in", "session_id": SESSION_ID})

@app.route('/items', methods=['GET'])
def get_items():
    url = f"{SAP_URL}Items"
    response = requests.get(url, headers=get_headers(), verify=False)
    return jsonify(response.json().get('value', []))

@app.route('/purchase-order', methods=['POST'])
def create_purchase_order():
    data = request.json
    url = f"{SAP_URL}PurchaseOrders"
    response = requests.post(url, json=data, headers=get_headers(), verify=False)
    return jsonify(response.json()), response.status_code

@app.route('/goods-receipt-po', methods=['POST'])
def create_goods_receipt_po():
    data = request.json
    url = f"{SAP_URL}PurchaseDeliveryNotes"
    response = requests.post(url, json=data, headers=get_headers(), verify=False)
    return jsonify(response.json()), response.status_code

@app.route('/ap-invoice', methods=['POST'])
def create_ap_invoice():
    data = request.json
    url = f"{SAP_URL}PurchaseInvoices"
    response = requests.post(url, json=data, headers=get_headers(), verify=False)
    return jsonify(response.json()), response.status_code

@app.route('/payment', methods=['POST'])
def create_payment():
    data = request.json
    url = f"{SAP_URL}VendorPayments"
    response = requests.post(url, json=data, headers=get_headers(), verify=False)
    return jsonify(response.json()), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
