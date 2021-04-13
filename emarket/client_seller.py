import json
import socket
import time
from emarket.erequests import FrontRequestEnum
from emarket.emarket import Item
import requests

class ClientSeller:

    def __init__(self, front_end_ip):
        self.username = None
        self.front_end_ip = front_end_ip

    def check_username(self):
        if self.username is None:
            print("Must Login First!")
            return False
        else:
            return True

    def create_user(self, name, username, password):
        if len(username) > 12 or len(password) > 12:
            raise ValueError("Max length username or password 12 characters")
        print(f"Creating user {username}")
        payload = {"name":name,"username" : username,
            "password": password}
        r = requests.post(f'http://{self.front_end_ip}:5000/create_user', json=payload)
        r = r.json()
        return r["status"]

    def login(self, username, password):
        print("Logging in")
        if len(username) > 12 or len(password) > 12:
            raise ValueError("Max length username or password 12 characters")
        payload = {
            "username" : username,
            "password": password}
        r = requests.post(f'http://{self.front_end_ip}:5000/login', json=payload)
        r = r.json()
        if r["status"]:
            self.username = username
        return r["status"]
    
    def logout(self):
        print("Logging out")
        if not self.check_username():
            return False
        payload = {"username" : self.username}
        r = requests.post(f'http://{self.front_end_ip}:5000/logout', json=payload)
        r = r.json()
        return r["status"]

    def put_item_for_sale(self, item, quantity):
        print("Putting items for sale")
        if not self.check_username():
            return False
        
        if not isinstance(item, Item):
            print("item must be of type Item!")
            return False
        if item.category < 0 or item.category > 9:
            print("item category out of range")
        item_payload = vars(item)

        payload = {"username" : self.username,
            "item":item_payload, "quantity" : quantity}
        r = requests.post(f'http://{self.front_end_ip}:5000/put_item_for_sale', json=payload)
        r = r.json()
        if not r["status"]:
            return False, 0
        return r["status"], r["item_id"]

    def change_sale_price_item(self, item_id, new_price):
        if not self.check_username():
            return False
        
        payload = {"username" : self.username,
            "item_id":item_id, "new_price" : new_price}
        r = requests.post(f'http://{self.front_end_ip}:5000/change_sale_price_item', json=payload)
        r = r.json()
        return r["status"]
    
    def remove_item_from_sale(self, item_id, quantity):
        if not self.check_username():
            return False

        payload = {"username" : self.username,
            "item_id":item_id, "quantity" : quantity}
        r = requests.post(f'http://{self.front_end_ip}:5000/remove_item_from_sale', json=payload)
        r = r.json()
        return r["status"]

    def display_active_seller_items(self):
        if not self.check_username():
            return False

        payload = { "username" : self.username}
        r = requests.post(f'http://{self.front_end_ip}:5000/display_active_seller_items', json=payload)
        r = r.json()
        if not r["status"]:
            return False, 0
        else:
            return r["status"], r["items"]

    def get_rating(self):
        if not self.check_username():
            return False
            
        payload = {"username" : self.username}
        r = requests.post(f'http://{self.front_end_ip}:5000/get_rating', json=payload)
        r = r.json()
        if not r["status"]:
            return r["status"], 0, 0
        return r["status"], r["thumbsup"], r["thumbsdown"]
            