class Item:
    def __init__(self, item_code, item_name, quantity, price, pref_vendor):
        self._item_code = item_code
        self._item_name = item_name
        self._quantity = quantity
        self._price = price
        self._pref_vendor = pref_vendor

    def get_item_code(self):
        return self._item_code

    def get_item_name(self):
        return self._item_name

    def get_quantity(self):
        return self._quantity

    def get_price(self):
        return self._price

    def get_pref_vendor(self):
        return self._pref_vendor
