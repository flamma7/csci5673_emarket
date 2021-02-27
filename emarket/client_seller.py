import json
import socket
import time
from emarket.erequests import FrontRequestEnum
from emarket.emarket import Item
import requests

class ClientSeller:

    # def __init__(self, username=None, password=None, host="127.0.0.1", port=11311, delay=0.01): # None for new client
    #     self.host = host
    #     self.port = port
    #     self.username = username
    #     if username is None:
    #         print("New user, call create_user()")
    #     else:
    #         if self.login(username, password):
    #             print("Logged in")
    #         else:
    #             print("Failed to login")
    #     print("connected")
    #     self.delay = delay

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
        payload = {"name":name,"username" : username,
            "password": password}
        r = requests.post('http://localhost:5000/create_user', json=payload)
        r = r.json()
        return r["status"]

    def login(self, username, password):
        print("Logging in")
        if len(username) > 12 or len(password) > 12:
            raise ValueError("Max length username or password 12 characters")
        payload = {
            "username" : username,
            "password": password}
        r = requests.post('http://localhost:5000/login', json=payload)
        r = r.json()
        if r["status"]:
            self.username = username
        return r["status"]
    
    def logout(self):
        print("Logging out")
        payload = {"username" : self.username}
        r = requests.post('http://localhost:5000/logout', json=payload)
        r = r.json()
        return r["status"]

    def put_item_for_sale(self, item, quantity):
        print("Putting items for sale")
        if not isinstance(item, Item):
            print("item must be of type Item!")
            return False
        if item.category < 0 or item.category > 9:
            print("item category out of range")
        item_payload = vars(item)

        payload = {"username" : self.username,
            "item":item_payload, "quantity" : quantity}
        r = requests.post('http://localhost:5000/put_item_for_sale', json=payload)
        r = r.json()
        if not r["status"]:
            return False, 0
        return r["status"], r["item_id"]

    def change_sale_price_item(self, item_id, new_price):
        payload = {"username" : self.username,
            "item_id":item_id, "new_price" : new_price}
        r = requests.post('http://localhost:5000/change_sale_price_item', json=payload)
        r = r.json()
        return r["status"]
    
    def remove_item_from_sale(self, item_id, quantity):
        payload = {"username" : self.username,
            "item_id":item_id, "quantity" : -quantity}
        r = requests.post('http://localhost:5000/remove_item_from_sale', json=payload)
        r = r.json()
        return r["status"]

    def display_active_seller_items(self):
        payload = { "username" : self.username}
        r = requests.post('http://localhost:5000/display_active_seller_items', json=payload)
        r = r.json()
        if not r["status"]:
            return False, 0
        else:
            return r["status"], r["items"]

    def get_rating(self):
        payload = {"username" : self.username}
        r = requests.post('http://localhost:5000/get_rating', json=payload)
        r = r.json()
        if not r["status"]:
            return r["status"], 0, 0
        return r["status"], r["thumbsup"], r["thumbsdown"]
            