"""
Contains methods 

"""

class Server:

    def __init__(self):
        # Initialize socket

        self.item_list = []
        self.seller_db = []
        self.buyer_db = []

    def run(self):

        # Log every buyer and every seller in 

        # Loops on socket & receives client requests & parses data & updates

        
        pass

    """############# Seller Functions #############"""
    def create_seller(self, username, password):
        pass

    def create_buyer(self, username, password):
        pass
    
    def get_seller_rating(self, seller_id):
        pass

    def put_item_for_sale(self, item, quantity):
        pass

    def change_sale_price_item(self, item_id, new_price):
        pass

    def remove_item_from_sale(self, item_id, quantity):
        pass

    def display_active_seller_items(self, seller_id):
        pass

    """############# Buyer & Seller Functions #############"""

    def login(self, buyer_id=None, seller_id=None):
        pass
    
    def logout(self, buyer_id=None, seller_id=None):
        pass

    """############# Buyer Functions #############"""

    
