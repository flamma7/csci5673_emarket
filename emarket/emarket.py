class Item:
    def __init__(self, name, category, item_id, keywords, condition_new, sale_price):
        self.name = name
        self.category = category
        self.item_id = item_id
        self.keywords = keywords
        self.condition_new = condition_new
        self.sale_price = sale_price

class Seller:
    def __init__(self, name, seller_id, feedback_thumbsup=0, feedback_thumbsdown=0, num_items_sold=0):
        self.name = name
        self.seller_id = seller_id
        self.feedback = {"thumbsup" : feedback_thumbsup, "thumbsdown" : feedback_thumbsdown}
        self.num_items_sold = num_items_sold

class Buyer:
    def __init__(self, name, buyer_id, num_items_purchased=0):
        self.name = name
        self.buyer_id = buyer_id
        self.num_items_purchased = num_items_purchased