import requests
from item import Item
import datetime

def get_bp_name(bp_code):
    for bp in BP:
        if bp['CardCode'] == bp_code: #another loop? this is not efficient
            return bp['CardName']
    return 'Unknown Business Partner'

def get_item():
    while True:
        item_input = input('What is the item code or name you want to buy ').strip().lower() # Convert input to lowercase
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

print('Time to create a purchase order')

BP_url= 'https://localhost:50000/b1s/v1/BusinessPartners'
BP_headers = {'Cookie': 'B1SESSION=' + session_id}
BP_response = requests.get(BP_url, headers=BP_headers, verify=False)
BP = BP_response.json().get('value')

items_url = 'https://localhost:50000/b1s/v1/Items'
items_headers = {'Cookie': 'B1SESSION=' + session_id}
items_response = requests.get(items_url, headers=items_headers, verify=False)
items = items_response.json().get('value', [])


print('Available items')
items_list = []
item_shopping_list = []
for it in items:
    items_list.append(Item(it['ItemCode'], it['ItemName'],0, it.get('ItemPreferredVendors', [{}])[0].get('BPCode', 'Unknown BPCode')))
    print(it['ItemName'] + ' Can be bought from Business Partner ' + get_bp_name(it.get('ItemPreferredVendors', [{}])[0].get('BPCode', 'Unknown BPCode')))#business partner is too hard to follow
add_item_flag = 'Y'
while add_item_flag == 'Y':
    item_input_code = get_item()
    for i in items_list:
        #get preferred vendor
        if i.get_item_code() == item_input_code:
            item_input_pref_vendor = i.get_pref_vendor()
            print('Preferred vendor for item:', item_input_code, 'is:', item_input_pref_vendor)
            break

    quantity = input('How many ' + item_input_code + ' do you want to buy?')
    price = None
    for item in items:
        if item['ItemCode'] == item_input_code:
            for price_detail in item['ItemPrices']:
                if price_detail['PriceList'] == 1:  # Assuming you want the price from PriceList 1
                    price = price_detail['Price']
                    break
            break

    if price is not None:
        itemTemp = Item(item_input_code, quantity, price, item_input_pref_vendor)
        item_shopping_list.append(itemTemp)
    else:
        print('Price not found for item:', item_input_code, '. Please contact us directly for price details')
    print('Item added to shopping list')
    add_item_flag = input('Do you want to add more items to the shopping list? (Y/N)').strip().upper()
    while add_item_flag not in ['Y', 'N']:
        add_item_flag = input('Invalid input. Please enter Y or N').strip().upper()





tax_code="T1"


#if tax_code is None:todo
#    print('Your Institution doesn\'t have a tax code, defaulting to T1')todo
#    tax_code = 'T1' todo

#create the purchase order
#then create the goods receipt PO
#then create the A/P invoice
#then create the payment



print('Based on the items you selected, each item will be bought from its preferred vendor and put into a separate purchase order')
purchase_order_url = 'https://localhost:50000/b1s/v1/PurchaseOrders'
purchase_order_headers = {'Cookie': 'B1SESSION=' + session_id}
purchase_order_response=[]
for item in item_shopping_list:
    purchase_order_payload = {
        "CardCode": item.get_pref_vendor(),
        "DocDate": datetime.datetime.now().strftime('%Y-%m-%d'),
        "DocumentLines": [
            {
                "ItemCode": item.get_item_code(),
                "Quantity": item.get_quantity(),
                "Price": item.get_price(),
                "TaxCode": tax_code
            }
        ]
    }
    response = requests.post(purchase_order_url, json=purchase_order_payload, headers=purchase_order_headers, verify=False)
    purchase_order_response.append(response)

successful_purchase_orders = []
for response in purchase_order_response:
    if response.status_code == 201:
        successful_purchase_orders.append(response.json())
        print('Purchase order with doc entry', response.json()['DocEntry'], 'created successfully')
    else:
        print('Error creating purchase order:', response.text)


vendor_items_map = {}
for item in item_shopping_list:
    vendor = item.get_pref_vendor()
    if vendor not in vendor_items_map:
        vendor_items_map[vendor] = {}
    if item.get_item_code() not in vendor_items_map[vendor]:
        vendor_items_map[vendor][item.get_item_code()] = 0
    vendor_items_map[vendor][item.get_item_code()] += int(item.get_quantity())




if vendor_items_map:
    auto_create_grpo = input('Do you want to automatically create a goods receipt PO for each successful purchase order? (Y/N)').strip().upper()
    while auto_create_grpo not in ['Y', 'N']:
        auto_create_grpo = input('Invalid input. Please enter Y or N').strip().upper()

    if auto_create_grpo == 'Y':
        print('Time to create a goods receipt PO for each vendor')
        goods_receipt_url = 'https://localhost:50000/b1s/v1/PurchaseDeliveryNotes'
        goods_receipt_headers = {'Cookie': 'B1SESSION=' + session_id}
        goods_receipt_response = []

        for vendor, items in vendor_items_map.items():
            document_lines = [{"ItemCode": item_code, "Quantity": quantity} for item_code, quantity in items.items()]

            goods_receipt_payload = {
                "CardCode": vendor,
                "DocDate": datetime.datetime.now().strftime('%Y-%m-%d'),
                "DocumentLines": document_lines
            }
            response = requests.post(goods_receipt_url, json=goods_receipt_payload, headers=goods_receipt_headers, verify=False)
            goods_receipt_response.append(response)

        successful_goods_receipts = []
        for response in goods_receipt_response:
            if response.status_code == 201:
                successful_goods_receipts.append(response.json())
                print('Goods receipt PO with doc entry', response.json()['DocEntry'], 'created successfully')
            else:
                print('Error creating goods receipt PO:', response.text)


    auto_create_ap_invoice = input('Do you want to automatically create an A/P invoice for each successful goods receipt PO? (Y/N)').strip().upper()
    while auto_create_ap_invoice not in ['Y', 'N']:
        auto_create_ap_invoice = input('Invalid input. Please enter Y or N').strip().upper()

    if auto_create_ap_invoice == 'Y':
        print('Time to create an A/P invoice for each successful goods receipt PO')
        ap_invoice_url = 'https://localhost:50000/b1s/v1/PurchaseInvoices'
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
            ap_invoice_response.append(response)

        successful_ap_invoices = []
        for response in ap_invoice_response:
            if response.status_code == 201:
                successful_ap_invoices.append(response.json())
                print('A/P invoice with doc entry', response.json()['DocEntry'], 'created successfully')
            else:
                print('Error creating A/P invoice:', response.text)

    auto_create_payment = input('Do you want to automatically create a payment for each successful A/P invoice? (Y/N)').strip().upper()
    while auto_create_payment not in ['Y', 'N']:
        auto_create_payment = input('Invalid input. Please enter Y or N').strip().upper()

    if auto_create_payment == 'Y':
        print('Time to create a payment for each successful A/P invoice')
        payment_url = 'https://localhost:50000/b1s/v1/VendorPayments'
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
            payment_response.append(response)

    successful_payments = []
    for response in payment_response:
        if response.status_code == 201:
            successful_payments.append(response.json())
            print('Payment with doc entry', response.json()['DocEntry'], 'created successfully')
        else:
            print('Error creating payment:', response.text)
