import json
import socket
import time
from emarket.requests import FrontRequestEnum
from emarket.emarket import Item

class ClientSeller:

    def __init__(self, username=None, password=None, host="127.0.0.1", port=11311): # None for new client
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

    def send_recv_payload(self, payload):
        time.sleep(0.5)
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
        return data_resp["seller_id"]

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

    def put_item_for_sale(self, item, quantity):
        print("Putting items for sale")
        if not isinstance(item, Item):
            print("item must be of type Item!")
            return False
        item_payload = vars(item)

        req_id = FrontRequestEnum.index("put_item_for_sale")
        payload = {"req_id":req_id, "username" : self.username,
            "item":item_payload, "quantity" : quantity}
        data_resp = self.send_recv_payload(payload)
        if not data_resp["status"]:
            return False, 0
        return data_resp["status"], data_resp["item_id"]

    def change_sale_price_item(self, item_id, new_price):
        req_id = FrontRequestEnum.index("change_sale_price_item")
        payload = {"req_id":req_id, "username" : self.username,
            "item_id":item_id, "new_price" : new_price}
        data_resp = self.send_recv_payload(payload)
        return data_resp["status"]
    
    def remove_item_from_sale(self, item_id, quantity):
        req_id = FrontRequestEnum.index("remove_item_from_sale")
        payload = {"req_id":req_id, "username" : self.username,
            "item_id":item_id, "quantity" : -quantity}
        data_resp = self.send_recv_payload(payload)
        return data_resp["status"]

    def display_active_seller_items(self):
        req_id = FrontRequestEnum.index("display_active_seller_items")
        payload = {"req_id":req_id, "username" : self.username}
        data_resp = self.send_recv_payload(payload)
        if not data_resp["status"]:
            return False, 0
        else:
            return data_resp["status"], data_resp["items"]