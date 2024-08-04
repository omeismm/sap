
import requests
from item import Item
import datetime

def add_item():
    item_code = input('Enter the item code: ')
    item_name = input('Enter the item name: ')
    item_price = float(input('Enter the item price: '))
    item_quantity = int(input('Enter the item quantity: '))
    item = Item(item_code, item_name, item_quantity, item_price)
    return item

def update_item():
    item_code = input('Enter the item code: ')
    item_name = input('Enter the item name: ')
    item_price = float(input('Enter the item price: '))
    item_quantity = int(input('Enter the item quantity: '))
    item = Item(item_code, item_name, item_quantity, item_price)
    return item

def delete_item():
    item_code = input('Enter the item code: ')
    return item_code

def view_item_details():
    item_code = input('Enter the item code: ')
    return item_code

def create_item_group():
    item_group_code = input('Enter the item group code: ')
    item_group_name = input('Enter the item group name: ')
    return item_group_code, item_group_name

def update_item_group():
    item_group_code = input('Enter the item group code: ')
    item_group_name = input('Enter the item group name: ')
    return item_group_code, item_group_name

def delete_item_group():
    item_group_code = input('Enter the item group code: ')
    return item_group_code

def add_item_to_item_group():
    item_group_code = input('Enter the item group code: ')
    item_code = input('Enter the item code: ')
    return item_group_code, item_code

def remove_item_from_item_group():
    item_group_code = input('Enter the item group code: ')
    item_code = input('Enter the item code: ')
    return item_group_code, item_code

def view_item_group_details():
    item_group_code = input('Enter the item group code: ')
    return item_group_code

def create_warehouse():
    warehouse_code = input('Enter the warehouse code: ')
    warehouse_name = input('Enter the warehouse name: ')
    return warehouse_code, warehouse_name

def update_warehouse():
    warehouse_code = input('Enter the warehouse code: ')
    warehouse_name = input('Enter the warehouse name: ')
    return warehouse_code, warehouse_name

def delete_warehouse():
    warehouse_code = input('Enter the warehouse code: ')
    return warehouse_code

def get_warehouse_details():
    warehouse_code = input('Enter the warehouse code: ')
    return warehouse_code

def create_unit_of_measure():
    uom_code = input('Enter the unit of measure code: ')
    uom_name = input('Enter the unit of measure name: ')
    return uom_code, uom_name

def update_unit_of_measure():
    uom_code = input('Enter the unit of measure code: ')
    uom_name = input('Enter the unit of measure name: ')
    return uom_code, uom_name

def delete_unit_of_measure():
    uom_code = input('Enter the unit of measure code: ')
    return uom_code

def view_unit_of_measure_details():
    uom_code = input('Enter the unit of measure code: ')
    return uom_code



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

while True:
    print('''
========================================
    Welcome to the Item Management System
========================================
    Please select an option:

    [1] Add Item
    [2] Update Item
    [3] Delete Item
    [4] View Item Details

    [5] Create Item Group
    [6] Update Item Group
    [7] Delete Item Group
    [8] Add Item to Item Group
    [9] Remove Item from Item Group
    [10] View Item Group Details

    [11] Create Warehouse
    [12] Update Warehouse
    [13] Delete Warehouse
    [14] View Warehouse Details

    [15] Create Unit of Measure
    [16] Update Unit of Measure
    [17] Delete Unit of Measure
    [18] View Unit of Measure Details

    [0] Exit
========================================
    ''')

    choice = input('Enter your choice (0-18): ').strip()

    if choice == '0':
        print('Exiting the system. Goodbye!')
        break

    # Add logic for handling each choice here
    if choice == '1':
        print('Option 1 selected: Add Item')
        item = add_item()
    elif choice == '2':
        print('Option 2 selected: Update Item')
        item = update_item()
    elif choice == '3':
        print('Option 3 selected: Delete Item')
        item_code = delete_item()
    elif choice == '4':
        print('Option 4 selected: View Item Details')
        item_code = view_item_details()
    elif choice == '5':
        print('Option 5 selected: Create Item Group')
        item_group_code, item_group_name = create_item_group()
    elif choice == '6':
        print('Option 6 selected: Update Item Group')
        item_group_code, item_group_name = update_item_group()
    elif choice == '7':
        print('Option 7 selected: Delete Item Group')
        item_group_code = delete_item_group()
    elif choice == '8':
        print('Option 8 selected: Add Item to Item Group')
        item_group_code, item_code = add_item_to_item_group()
    elif choice == '9':
        print('Option 9 selected: Remove Item from Item Group')
        item_group_code, item_code = remove_item_from_item_group()
    elif choice == '10':
        print('Option 10 selected: View Item Group Details')
        item_group_code = view_item_group_details()
    elif choice == '11':
        print('Option 11 selected: Create Warehouse')
        warehouse_code, warehouse_name = create_warehouse()
    elif choice == '12':
        print('Option 12 selected: Update Warehouse')
        warehouse_code, warehouse_name = update_warehouse()
    elif choice == '13':
        print('Option 13 selected: Delete Warehouse')
        warehouse_code = delete_warehouse()
    elif choice == '14':
        print('Option 14 selected: View Warehouse Details')
        warehouse_code = get_warehouse_details()
    elif choice == '15':
        print('Option 15 selected: Create Unit of Measure')
        uom_code, uom_name = create_unit_of_measure()
    elif choice == '16':
        print('Option 16 selected: Update Unit of Measure')
        uom_code, uom_name = update_unit_of_measure()
    elif choice == '17':
        print('Option 17 selected: Delete Unit of Measure')
        uom_code = delete_unit_of_measure()
    elif choice == '18':
        print('Option 18 selected: View Unit of Measure Details')
        uom_code = view_unit_of_measure_details()
    else:
        print('Invalid choice. Please enter a number between 0 and 18.')
