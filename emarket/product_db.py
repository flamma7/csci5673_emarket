import json
import socket
from emarket.requests import BackRequestEnum
from emarket.emarket import Seller, Item

class ProductDB:
    def __init__(self, host="127.0.0.1", port=11314):
        self.host = host
        self.port = port
        self.sellers = []
        self.products = []

    def run(self):
        print("Running Product DB")
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((self.host, self.port))
                s.listen()            
                conn, addr = s.accept()
                with conn:
                    while True:
                        data = conn.recv(2048)
                        if not data:
                            break
                        payload = json.loads(data)
                        print(payload)
                        resp = self.handle_payload( payload )

                        if isinstance(resp, bool):
                            resp = {"status" : resp}
                        elif isinstance(resp, dict):
                            resp_payload = resp
                        else:
                            raise ValueError(f"Unknown return type: {type(resp)}")
                        
                        resp_payload = json.dumps(resp, indent=4)
                        conn.sendall(resp_payload.encode())
                        print("#######")

    def handle_payload(self, payload):
        req_id = payload["req_id"]
        
        # Check if we're creating a new user
        if req_id == BackRequestEnum.index("create_acct"):
            return self.create_acct(payload)
        elif req_id == BackRequestEnum.index("login"):
            return self.change_login(payload, True)
        elif req_id == BackRequestEnum.index("logout"):
            return self.change_login(payload, False)
        elif req_id == BackRequestEnum.index("check_login"):
            return self.check_login(payload)
        elif req_id == BackRequestEnum.index("create_item"):
            return self.create_item(payload)
        elif req_id == BackRequestEnum.index("update"):
            return self.update(payload)
        elif req_id == BackRequestEnum.index("get_acct"):
            return self.get_acct(payload)
        elif req_id == BackRequestEnum.index("get_item"):
            return self.get_item(payload)
        elif req_id == BackRequestEnum.index("get_rating"):
            return self.get_rating(payload)
        elif req_id == BackRequestEnum.index("leave_feedback"):
            return self.leave_feedback(payload)
        elif req_id == BackRequestEnum.index("make_purchase"):
            return self.make_purchase(payload)
        else:
            raise ValueError(f"Unrecognized Request Enum: {req_id}")

    def create_acct(self, payload):
        print("Creating user")
        seller_id = len(self.sellers)
        name = payload["name"]
        us = payload["username"]
        pw = payload["password"]
        s = Seller(name, seller_id, us, pw)
        self.sellers.append(s)
        return {"status":True, "seller_id" : seller_id}

    def change_login(self, payload, login=True):
        user = payload["username"]
        found = False
        # print(vars(self.sellers))
        for s in self.sellers:
            # print(f"{s.name} : {s.password} : {s.logged_in}")
            if s.username == user :
                
                if login and s.password == payload["password"]:
                    found = True
                    s.logged_in = True
                    print(f"Logging in {user}")
                elif not login:
                    found = True
                    s.logged_in = False
                    print(f"Logging out {user}")
                else:
                    print("Wrong Password!")
        return found

    def check_login(self, payload):
        user = payload["username"]
        for s in self.sellers:
            if s.username == user:
                return s.logged_in
        return False
    
    def create_item(self, payload):
        if len(self.products) > 0:
            item_id = self.products[-1].item_id + 1
        else:
            item_id = 1

        seller_id = None
        for i in range(len(self.sellers)):
            if self.sellers[i].username == payload["username"]:
                seller_id = self.sellers[i].seller_id
        
                new_item = Item(
                    name=payload["item"]["name"],
                    category=payload["item"]["category"],
                    item_id=item_id,
                    keywords=payload["item"]["keywords"],
                    condition_new=payload["item"]["condition_new"],
                    sale_price = payload["item"]["sale_price"],
                    seller_id=seller_id,
                    quantity = payload["quantity"]
                )
                self.products.append( new_item )
                self.sellers[i].items_for_sale.append( new_item )
                return {"status":True, "item_id":item_id}
        return False

    
    def update(self, payload):
        # Updating based on keywords not supported
        # payload : {req_id, username, match_fields, new_fields}
        print("Updating")
        updated = False
        to_delete = []
        for i in range(len(self.products)):
            match = 0
            for key in payload["match_fields"]:
                if key == "keywords":
                    raise NotImplementedError("Updating based on keyword match not supported")
                if vars(self.products[i])[key] == payload["match_fields"][key]:
                    match += 1
            if match == len(payload["match_fields"]):
                updated = True
                for key in payload["new_fields"]:
                    if key == "quantity" and payload["new_fields"][key] < 0: # Just update
                        vars(self.products[i])[key] += payload["new_fields"][key]
                    else: # Update new field with value
                        vars(self.products[i])[key] = payload["new_fields"][key]
                if self.products[i].quantity <= 0:
                    to_delete.append( i )
        for td in reversed(to_delete):
            print(f"Deleting {self.products[td].name}")
            sid = self.products[td].seller_id
            ind = self.sellers[sid].items_for_sale.index(self.products[td])
            self.sellers[sid].items_for_sale.pop(ind) # Remove seller object link
            self.products.pop( td )
        return updated
            

    def get_acct(self, payload):
        for i in self.sellers:
            if i.username == payload["username"]:
                new_payload = {"status":True}
                for f in payload["fields"]:
                    new_payload[f] = vars(i)[f]
                return new_payload
        return {"status": False}

    def get_item(self, payload):
        items = []
        for i in range(len(self.products)):
            match = 0

            # Check for field matches
            for key in payload["match_fields"]:
                if key == "keywords":
                    for key2 in payload["match_fields"][key]:
                        if key2 in vars(self.products[i])[key]:
                            match += 1
                            break
                if vars(self.products[i])[key] == payload["match_fields"][key]:
                    match += 1

            # Check if we've matched all of the fields
            if match == len(payload["match_fields"]):
                items.append( self.products[i] )
        if len(items) > 0:
            new_payload = {"status":True, "items" : [vars(x) for x in items]}
            return new_payload
        else:
            return False

    def get_rating(self, payload):
        print("Getting Rating")
        
        # Buyer is checking seller rating
        if "seller_id" in list(payload.keys()):
            for s in self.sellers:
                if s.seller_id == payload["seller_id"]:
                    return {"status": True, "rating": s.feedback }
            return self.process_error("Seller ID not found")
        
        # Seller themself are checking rating
        user = payload["username"]
        for s in self.sellers:
            if s.username == user:
                return {"status": True, "rating": s.feedback }
        return {"status":False, "rating" : {}}

    def process_error(self, error):
        print(error)
        return {"status" : False, "error" : error}

    def leave_feedback(self, payload):
        print("Leaving Feedback")
        # Find seller id
        seller_id = None
        for p in self.products:
            if p.item_id == payload["item_id"]:
                seller_id = p.seller_id

        if seller_id is not None:
            # Add feedback to seller
            for s in self.sellers:
                if s.seller_id == seller_id:
                    if payload["feedback"] not in list(s.feedback.keys()):
                        return self.process_error("Improper feedback request format")
                    s.feedback[payload["feedback"]] += 1
                    return True
            return self.process_error("Could not locate seller id")
        else:
            return self.process_error("Item not found")

    def make_purchase(self, payload):
        print("Making Purchase")

        # Check the credit card information
        total_cost = 0.0
        for item_id, quantity in payload["items"]:
            item_found = False
            for p in self.products:
                if p.item_id == item_id: # Making the purchase
                    item_found = True
                    if p.quantity >= quantity:
                        total_cost += (p.sale_price * quantity)
                        p.quantity -= quantity

                        # Update the sellers info
                        for s in self.sellers:
                            if s.seller_id == p.seller_id:
                                s.num_items_sold += quantity
                                break
                        break
                    else:
                        return self.process_error(f"Insufficent Quantity of item {p.item_id}. In-stock: {p.quantity}, Req: {quantity}")
            if not item_found:
                return self.process_error(f"Unable to locate item_id: {item_id}")

        # TODO check credit card information & bill the total amount?

        return True