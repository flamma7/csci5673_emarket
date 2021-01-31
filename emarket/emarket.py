class Item:
    def __init__(self, name, category, item_id, keywords, condition_new, sale_price, seller_id):
        self.name = name
        self.category = category
        self.item_id = item_id
        if not isinstance(keywords, list):
            self.keywords = [keywords]
        else:
            assert len(keywords) < 6
            self.keywords = keywords
        assert isinstance(condition_new, bool)
        self.condition_new = condition_new
        self.sale_price = sale_price
        self.seller_id = seller_id

class Seller:
    def __init__(self, name, seller_id, username, password, feedback_thumbsup=0, feedback_thumbsdown=0, num_items_sold=0):
        self.name = name
        self.seller_id = seller_id
        self.username = username
        self.password = password # production would encrypt
        self.feedback = {"thumbsup" : feedback_thumbsup, "thumbsdown" : feedback_thumbsdown}
        self.num_items_sold = num_items_sold
        self.items_for_sale = []
        self.logged_in = False

class Buyer:
    def __init__(self, name, buyer_id, username, password, num_items_purchased=0):
        self.name = name
        self.buyer_id = buyer_id
        self.username = username
        self.password = password # production would encrypt
        self.num_items_purchased = num_items_purchased
        self.shopping_cart = []
        self.history = []
        self.logged_in = False