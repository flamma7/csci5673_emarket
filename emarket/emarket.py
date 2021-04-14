from pysyncobj import *

class ProductData(SyncObj):

    def __init__(self, my_ip, other_ips):
        super(ProductData, self).__init__(my_ip, other_ips)
        self.sellers = []
        self.products = []

    @replicated_sync
    def add_seller(self, name, seller_id, username, password, feedback_thumbsup=0, feedback_thumbsdown=0, num_items_sold=0):
        print("Addinig user")
        s = Seller(name, seller_id, username, password, feedback_thumbsup, feedback_thumbsdown, num_items_sold)
        self.sellers.append(s)

    @replicated_sync
    def change_login(self, seller_index, logging_in=True):
        print("Changing login")
        self.sellers[seller_index].logged_in = logging_in

    @replicated_sync
    def add_product(self, name, category, item_id, keywords, condition_new, sale_price, seller_id, quantity):
        print("Adding product")
        new_item = Item(
            name=name,
            category=category,
            item_id=item_id,
            keywords=keywords,
            condition_new=condition_new,
            sale_price = sale_price,
            seller_id=seller_id,
            quantity = quantity )
        
        self.products.append( new_item )

    @replicated_sync
    def remove_item(self, item_index, quantity):
        print("Removing Item")
        self.products[item_index].quantity -= quantity
        if self.products[item_index].quantity <= 0:
            print("Deleting item")
            self.products.pop( item_index )

    @replicated_sync
    def change_price(self, item_index, sale_price):
        print("Changing Price")
        self.products[item_index].sale_price = sale_price

    @replicated_sync
    def leave_feedback(self, seller_index, feedback_type):
        print("Leaving Feedback")
        self.sellers[seller_index].feedback[ feedback_type ] += 1

    @replicated_sync
    def make_sale(self, seller_index, quantity):
        print("Making Sale")
        self.sellers[seller_index].num_items_sold += quantity

class Item:
    def __init__(self, name, category, item_id, keywords, condition_new, sale_price, seller_id,quantity=0):
        # keywords is a list of length max 5
        # condition_new is bool
        self.name = name
        self.category = category
        self.item_id = item_id
        if not isinstance(keywords, list):
            self.keywords = [keywords]
        else:
            self.keywords = keywords
        self.condition_new = condition_new
        self.sale_price = sale_price
        self.seller_id = seller_id
        self.quantity = quantity

class Seller:
    def __init__(self, name, seller_id, username, password, feedback_thumbsup=0, feedback_thumbsdown=0, num_items_sold=0):
        self.name = name
        self.seller_id = seller_id
        self.username = username
        self.password = password # production would encrypt
        self.feedback = {"thumbsup" : feedback_thumbsup, "thumbsdown" : feedback_thumbsdown}
        self.num_items_sold = num_items_sold
        self.logged_in = False

class Buyer:
    def __init__(self, name, buyer_id, username, password, num_items_purchased=0):
        self.name = name
        self.buyer_id = buyer_id
        self.username = username
        self.password = password # production would encrypt
        self.num_items_purchased = num_items_purchased
        self.shopping_cart = [] # 2 item list [id, quantity]
        self.history = []
        self.items_given_feedback = []
        self.logged_in = False