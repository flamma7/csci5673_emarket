import json
import socket
import time
from emarket.erequests import FrontRequestEnum
from emarket.emarket import Item

class ClientBuyer:

    def __init__(self, username=None, password=None, host="127.0.0.1", port=11312, delay=0.01): # None for new client
        self.host = host
        self.port = port
        self.username = username
        if username is None:
            print("New user, call create_user()")
        else:
            if self.login(username, password):
                print("Logged in")
            else:
                print("Failed to login")
        print("connected")
        self.delay = delay

    def send_recv_payload(self, payload):
        time.sleep(self.delay)
        json_payload = json.dumps(payload, indent=4)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.sendall(json_payload.encode())
            data = s.recv(2048)
            data_resp = json.loads(data)
            print(data_resp)
            if data_resp["status"] == False:
                print("Error Encountered")
            return data_resp

    def create_user(self, name, username, password):
        if len(username) > 12 or len(password) > 12:
            raise ValueError("Max length username or password 12 characters")
        print(f"Creating user {username}")
        req_id = FrontRequestEnum.index("create_user")
        payload = {"req_id":req_id, "name":name,"username" : username,
            "password": password}
        data_resp = self.send_recv_payload(payload)
        if data_resp["status"] == False:
            return False
        return data_resp["buyer_id"]

    def login(self, username, password):
        print("Logging in")
        if len(username) > 12 or len(password) > 12:
            raise ValueError("Max length username or password 12 characters")
        req_id = FrontRequestEnum.index("login")
        payload = {"req_id":req_id, "username" : username,
            "password": password}
        data_resp = self.send_recv_payload(payload)
        if data_resp["status"]:
            self.username = username
        return data_resp["status"]
    
    def logout(self):
        print("Logging out")
        req_id = FrontRequestEnum.index("logout")
        payload = {"req_id":req_id, "username" : self.username}
        data_resp = self.send_recv_payload(payload)
        return data_resp["status"]

    def search_items_for_sale(self, category=None, keywords=None):
        print("Searching Items for Sale")
        if not isinstance(keywords, list):
            keywords = [keywords]
        if len(keywords) > 5:
            print("Too many keywords")
            return False

        req_id = FrontRequestEnum.index("search_items_for_sale")
        payload = {"req_id":req_id, 
            "username" : self.username
        }
        if category is not None:
            payload["category"] = category
        if keywords is not None:
            payload["keywords"] = keywords

        data_resp = self.send_recv_payload(payload)
        if not data_resp["status"]:
            return False, []
        return data_resp["status"], data_resp["items"]

    def add_item_shopping_cart(self, item_id, quantity):
        print("Adding item to shopping cart")
        req_id = FrontRequestEnum.index("add_item_shopping_cart")
        payload = {"req_id":req_id, 
            "username" : self.username,
            "item_id" : item_id,
            "quantity" : quantity
        }
        data_resp = self.send_recv_payload(payload)
        return data_resp["status"]

    def remove_item_shopping_cart(self, item_id, quantity):
        print("Removing item from shopping cart")
        req_id = FrontRequestEnum.index("remove_item_shopping_cart")
        payload = {"req_id":req_id, 
            "username" : self.username,
            "item_id" : item_id,
            "quantity" : quantity
        }
        data_resp = self.send_recv_payload(payload)
        return data_resp["status"]

    def clear_shopping_cart(self):
        print("Clearing shopping cart")
        req_id = FrontRequestEnum.index("clear_shopping_cart")
        payload = {"req_id":req_id, 
            "username" : self.username
        }
        data_resp = self.send_recv_payload(payload)
        return data_resp["status"]

    def display_shopping_cart(self):
        print("Displaying shopping cart")
        req_id = FrontRequestEnum.index("display_shopping_cart")
        payload = {"req_id":req_id, 
            "username" : self.username
        }
        data_resp = self.send_recv_payload(payload)
        return data_resp["status"], data_resp["items"]

    def leave_feedback(self, item_id, thumbsup=True):
        print("Leaving feedback")
        req_id = FrontRequestEnum.index("leave_feedback")
        feedback = "thumbsup" if thumbsup else "thumbsdown"
        payload = {"req_id":req_id, 
            "username" : self.username,
            "feedback" : feedback,
            "item_id" : item_id
        }
        data_resp = self.send_recv_payload(payload)

        if not data_resp["status"]:
            print(data_resp["error"])

        return data_resp["status"]

    def get_seller_rating(self, seller_id):
        print("Getting seller rating")
        req_id = FrontRequestEnum.index("get_rating")
        payload = {"req_id":req_id, 
            "username" : self.username,
            "seller_id" : seller_id
        }
        data_resp = self.send_recv_payload(payload)

        if not data_resp["status"]:
            print(data_resp["error"])
        return data_resp["status"], data_resp["rating"]

    def get_history(self):
        print("Getting History")
        req_id = FrontRequestEnum.index("get_history")
        payload = {"req_id":req_id, 
            "username" : self.username,
        }
        data_resp = self.send_recv_payload(payload)

        if not data_resp["status"]:
            print(data_resp["error"])
        return data_resp["status"], data_resp["history"]

    def make_purchase(self, cc_name, cc_number, cc_expiration):
        print("Making Purchase")

        req_id = FrontRequestEnum.index("make_purchase")
        payload = {"req_id":req_id, 
            "username" : self.username,
            "cc_name" : cc_name,
            "cc_number" : cc_number,
            "cc_expiration" : cc_expiration,
        }
        data_resp = self.send_recv_payload(payload)
        if not data_resp["status"]:
            print(data_resp["error"])
        return data_resp["status"]
