import json
import socket
import time
from emarket.requests import FrontRequestEnum, BackRequestEnum
class BuyerFront:

    def __init__(self, host="127.0.0.1", front_port=11312, back_port_customer=11313, back_port_product=11314, delay=0.5):
        self.logged_in = []
        self.host = host
        self.front_port = front_port
        self.back_port_customer = back_port_customer
        self.back_port_product = back_port_product
        self.delay = delay

    def run(self):
        print("Buyer Front Running")
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((self.host, self.front_port))
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
        if req_id == FrontRequestEnum.index("create_user"):
            return self.create_user(payload)
        elif req_id == FrontRequestEnum.index("login"):
            return self.login(payload)
        elif req_id == FrontRequestEnum.index("logout"):
            return self.logout(payload)
        else: # Check that the user is logged in
            if not self.check_logged_in(payload["username"]):
                print("Not logged in!")
                return False
            
            if req_id == FrontRequestEnum.index("search_items_for_sale"):
                return self.search_items_for_sale(payload)
            elif req_id == FrontRequestEnum.index("add_item_shopping_cart"):
                return self.add_item_shopping_cart(payload)
            elif req_id == FrontRequestEnum.index("remove_item_shopping_cart"):
                return self.remove_item_shopping_cart(payload)
            elif req_id == FrontRequestEnum.index("clear_shopping_cart"):
                return self.clear_shopping_cart(payload)
            elif req_id == FrontRequestEnum.index("display_shopping_cart"):
                return self.display_shopping_cart(payload)
            else:
                print(f"Unrecognized Request: {req_id}")
                return False
    
    def send_recv_payload(self, payload, customer_db=True):
        time.sleep(self.delay)
        json_payload = json.dumps(payload, indent=4)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            back_port = self.back_port_customer if customer_db else self.back_port_product
            s.connect((self.host, back_port))
            s.sendall(json_payload.encode())
            data = s.recv(2048)
            data_resp = json.loads(data)
            print(data_resp)
            if data_resp["status"] == False:
                print("Error Encountered")
            return data_resp

    def create_user(self, payload):
        print(f"Creating new user {payload['username']}")
        req_id = BackRequestEnum.index("create_acct")
        payload = {"req_id":req_id, "name":payload["name"],
            "username" : payload["username"],
            "password": payload["password"]}
        return self.send_recv_payload(payload)

    def login(self, payload):
        print("logging in")

        if self.check_logged_in(payload["username"]):
            print("Already logged in!")
            return True
        else:
            # Check correct password
            req_id = BackRequestEnum.index("get_acct")
            new_payload = {"req_id":req_id,
                "username" : payload["username"],
                "fields" : ["password"]
            }
            resp = self.send_recv_payload(new_payload)
            if resp["password"] == payload["password"]:
                self.logged_in.append(payload["username"])
                return True
            else:
                print("Incorrect password")
                return False
    
    def logout(self, payload):
        print("logging out")
        if not self.check_logged_in(payload["username"]):
            print("Not logged in!")
        else:
            i = self.logged_in.index(payload["username"])
            self.logged_in.pop(i)
        return True
    
    def search_items_for_sale(self, payload):
        #payload = {"req_id":req_id, 
        #     "username" : self.username,
        #     "category" : category,
        #     "keywords" : keywords
        # }
        print("Searching items for sale")
        req_id = BackRequestEnum.index("get_item")
        new_payload = {"req_id":req_id, 
            "match_fields" : {}
        }
        if "category" in payload.keys():
            new_payload["match_fields"]["category"] = payload["category"]
        if "keywords" in payload.keys():
            new_payload["match_fields"]["keywords"] = payload["keywords"]

        return self.send_recv_payload(new_payload, customer_db=False)

    def add_item_shopping_cart(self, payload):
        print("Adding items to shopping cart")
        # payload = {"req_id":req_id, 
        #     "username" : self.username,
        #     "item_id" : item_id,
        #     "quantity" : quantity
        # }

        # Check sufficient number of items available
        req_id = BackRequestEnum.index("get_item")
        new_payload = {
            "req_id" : req_id,
            "match_fields" : {"item_id" : payload["item_id"]}
        }
        item_resp = self.send_recv_payload(new_payload, customer_db=False)
        if not item_resp["status"]:
            print("Item not found!")
            return False
        target_item = item_resp["items"][0]
        if target_item["quantity"] < payload["quantity"]:
            print("Insufficient number of items available!")
            return False

        req_id = BackRequestEnum.index("add")
        new_payload = {"req_id" : req_id,
            "username" : payload["username"],
            "key" : "shopping_cart",
            "value" : [payload["item_id"], payload["quantity"]]
        }
        return self.send_recv_payload(new_payload, customer_db=True)

    def remove_item_shopping_cart(self, payload):
        print("Removing items from shopping cart")
        # payload = {"req_id":req_id, 
        #     "username" : self.username,
        #     "item_id" : item_id,
        #     "quantity" : quantity
        # }
        req_id = BackRequestEnum.index("sub")
        new_payload = {"req_id" : req_id,
            "username" : payload["username"],
            "key" : "shopping_cart",
            "value" : [payload["item_id"], payload["quantity"]]
        }
        return self.send_recv_payload(new_payload, customer_db=True)

    def clear_shopping_cart(self, payload):
        print("Clearing shopping cart")
        # payload = {"req_id":req_id, 
        #     "username" : self.username
        # }
        req_id = BackRequestEnum.index("add")
        new_payload = {
            "req_id" : req_id,
            "username" : payload["username"],
            "key" : "shopping_cart_clear"
        }
        return self.send_recv_payload(new_payload, customer_db=True)

    def display_shopping_cart(self, payload):
        print("Displaying shopping cart")
        # payload = {"req_id":req_id, 
        #     "username" : self.username
        # }
        req_id = BackRequestEnum.index("get_acct")
        new_payload = {
            "req_id" : req_id,
            "username" : payload["username"],
            "fields" : ["shopping_cart"]
        }
        data_resp = self.send_recv_payload(new_payload, customer_db=True)
        if not data_resp["status"]:
            return False
        else:
            return_msg = {"status":True, "items":[]}
            for item_id, quant in data_resp["shopping_cart"]:
                req_id = BackRequestEnum.index("get_item")
                new_payload = {
                    "req_id" : req_id,
                    "match_fields" : {"item_id" : item_id}
                }
                item_resp = self.send_recv_payload(new_payload, customer_db=False)
                if item_resp["status"]:
                    return_msg["items"].append(item_resp["items"][0])
                    return_msg["items"][-1]["quantity"] = quant
                else:
                    print("Unable to locate item -- out of sync!")
                    return False
            return return_msg
    def check_logged_in(self, user):
        return user in self.logged_in

if __name__ == "__main__":
    sf = SellerFront()
    sf.run()