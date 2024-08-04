
import requests
from item import Item
import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)


def get_bp():
    while True:
        BP_input = input('What is your Business Partner Name or CardCode?').strip().lower()  # Convert input to lowercase
        for bp in BP:
            if bp['CardName'].lower() == BP_input or bp['CardCode'].lower() == BP_input:  # Convert both to lowercase for comparison
                if bp['CardType'] != 'cCustomer':
                    print('WARNING: You are registered in our records but not as a customer. The sales order can still continue')
                print('Welcome ' + bp['CardName'])
                card_code = bp['CardCode']
                return card_code
        print('Business Partner not found')
        print('Please try again')

def get_item():
    while True:
        item_input = input('What is the item code or name you want to buy?').strip().lower()  # Convert input to lowercase
        for it in items:
            if it['ItemCode'].lower() == item_input or it['ItemName'].lower() == item_input:  # Convert both to lowercase for comparison
                print('Item found')
                item_code = it['ItemCode']
                return item_code
        print('Item not found')
        print('Please try again')


url = "https://localhost:50000/b1s/v1/Login"
payload = {
    "CompanyDB": "SBODemoGB",
    "Password": "1234",
    "UserName": "manager"
}
headers = {
    "Content-Type": "application/json"
}
response = requests.post(url, json=payload, headers=headers, verify=False)
print(response.text)
session_id = response.json()['SessionId']
print(response.json()['SessionId'])

print('Time to create a sales order')

BP_url= 'https://localhost:50000/b1s/v1/BusinessPartners'
BP_headers = {'Cookie': 'B1SESSION=' + session_id}
BP_response = requests.get(BP_url, headers=BP_headers, verify=False)
BP = BP_response.json().get('value')

card_code = get_bp()
tax_code=BP_response.json().get('TaxCode')

if tax_code is None:
    print('Your Institution doesn\'t have a tax code, defaulting to T1')
    tax_code = 'T1'

items_url = 'https://localhost:50000/b1s/v1/Items'
items_headers = {'Cookie': 'B1SESSION=' + session_id}
items_response = requests.get(items_url, headers=items_headers, verify=False)
items = items_response.json().get('value')

print('Available items')
for item in items:
    print(item['ItemName'])

item_shopping_list=[]

add_item_flag = 'Y'
while add_item_flag == 'Y':
    item_input_code = get_item()
    quantity = input('How many of this item do you want to buy?')
    price = None
    for item in items:
        if item['ItemCode'] == item_input_code:
            for price_detail in item['ItemPrices']:
                if price_detail['PriceList'] == 1:  # Assuming you want the price from PriceList 1
                    price = price_detail['Price']
                    break
            break

    if price is not None:
        itemTemp = Item(item_input_code, quantity, price,"")
        item_shopping_list.append(itemTemp)
    else:
        print('Price not found for item:', item_input_code,'. Please contact us directly for price details')

    add_item_flag = input('Do you want to add another item? Y/N').strip().upper()

due_date = datetime.datetime.now() + datetime.timedelta(days=30)
due_date = due_date.strftime('%Y-%m-%d')

print('Sales Order Summary')
total_price=0
print('Card Code: ' + card_code)
print('Tax Code: ' + tax_code)
print('Due Date: ' + due_date)
print('Items:')
for item in item_shopping_list:
    print('Item Code: ' + item.get_item_code())
    print('Quantity: ' + item.get_quantity())
    total_price += item.get_price() * int(item.get_quantity())
    print('Price: ' + str(item.get_price()))
print('Total Price: ' + str(total_price) + ' GBP')
create_flag = input('Do you want to create this sales order? Y/N').strip().upper()
if create_flag == 'Y':
    print('Creating sales order')
    sales_order_url = 'https://localhost:50000/b1s/v1/Orders'
    sales_order_headers = {'Cookie': 'B1SESSION=' + session_id}
    sales_order_payload = {
        "CardCode": card_code,
        "DocDueDate": due_date,
        "DocumentLines": []
    }
    for item in item_shopping_list:
        sales_order_payload['DocumentLines'].append(
            {
            "ItemCode": item.get_item_code(),
            "Quantity": item.get_quantity(),
            "Price": str(item.get_price())
        })
    print(sales_order_payload)
    sales_order_response = requests.post(sales_order_url, json=sales_order_payload, headers=sales_order_headers, verify=False)
    sales_order_data = sales_order_response.json()
    print(sales_order_response.text)

if sales_order_response.status_code == 201:
    sales_order_doc_num = sales_order_data['DocEntry']
    print('Sales order created successfully with DocEntry:', sales_order_doc_num)
    create_delivery_flag = ''
    while create_delivery_flag not in ['Y', 'N']:
        create_delivery_flag = input('Do you want to automatically create a delivery document for this sales order? Y/N').strip().upper()
        boolCreateDeliv = create_delivery_flag == 'Y'
    if boolCreateDeliv:
        # Create Delivery Document
        delivery_url = 'https://localhost:50000/b1s/v1/DeliveryNotes'
        delivery_payload = {
            "CardCode": card_code,
            "DocDueDate": due_date,
            "DocumentLines": sales_order_payload['DocumentLines'],
            "BaseDocumentType": 17,  # Sales Order
            "BaseEntry": sales_order_doc_num
        }
        print(delivery_payload)
        delivery_response = requests.post(delivery_url, json=delivery_payload, headers=sales_order_headers, verify=False)
        print(delivery_response.text) #value" : "Customer record not found "
    else:
        print('Delivery document not created')
else:
    print('Sales order not created')
##verify all code under this line

if delivery_response.status_code == 201:
    delivery_doc_num = delivery_response.json()['DocEntry']
    print('Delivery document created successfully with DocEntry:', delivery_doc_num)
    create_invoice_flag = ''
    while create_invoice_flag not in ['Y', 'N']:

        create_invoice_flag = input('Do you want to automatically create an A/R Invoice for this delivery document? Y/N').strip().upper()
    boolCreateInvoice = create_invoice_flag == 'Y'

    if boolCreateInvoice:
        # Create A/R Invoice
        invoice_url = 'https://localhost:50000/b1s/v1/Invoices'
        invoice_payload = {
            "CardCode": card_code,
            "DocDueDate": due_date,
            "DocumentLines": sales_order_payload['DocumentLines'],
            "BaseDocumentType": 15,  # Delivery Document
            "BaseEntry": delivery_doc_num
        }
        print(invoice_payload)
        invoice_response = requests.post(invoice_url, json=invoice_payload, headers=sales_order_headers, verify=False)
        print(invoice_response.text)
else:
    print('Delivery document not created')

if invoice_response.status_code == 201:
    invoice_doc_num = invoice_response.json()['DocEntry']
    print('A/R Invoice created successfully with DocEntry:', invoice_doc_num)
    create_payment_flag = ''
    while create_payment_flag not in ['Y', 'N']:
        create_payment_flag = input('Was this invoice paid for? If yes then payment record will be made automatically Y/N').strip().upper()
        boolCreatePay = create_payment_flag == 'Y'
    if boolCreatePay:
        # Create Payment
        payment_url = 'https://localhost:50000/b1s/v1/IncomingPayments'
        payment_payload = {
            "CardCode": card_code,
            "CashSum": total_price,
            "CashAccount": "161000",#cash account
            #"CashFlowAssignments": [
            #    {
            #        "AmountLC": total_price,
            #        "PaymentMeans": "pm_Check",
            #    }
            #],
            "PaymentInvoices": [
                {
                    "DocEntry": invoice_doc_num
                }
            ]
        }
        print(payment_payload)
        payment_response = requests.post(payment_url, json=payment_payload, headers=sales_order_headers, verify=False)
        print(payment_response.text)

else:
    print('A/R Invoice not created')
print('Sales Order Process Completed')
