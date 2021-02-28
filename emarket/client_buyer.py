import json

from emarket.erequests import FrontRequestEnum
from emarket.emarket import Item
import requests

class ClientBuyer:

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
        r = requests.post(f'http://{self.front_end_ip}:5001/create_user', json=payload)
        r = r.json()
        self.username = username
        return r["status"]

    def login(self, username, password):
        print("Logging in")
        if len(username) > 12 or len(password) > 12:
            raise ValueError("Max length username or password 12 characters")
        payload = {"username" : username,
            "password": password}
        r = requests.post(f'http://{self.front_end_ip}:5001/login', json=payload)
        r = r.json()
        return r["status"]
    
    def logout(self):
        print("Logging out")
        payload = {"username" : self.username}
        r = requests.post(f'http://{self.front_end_ip}:5001/logout', json=payload)
        r = r.json()
        return r["status"]

    def search_items_for_sale(self, category=None, keywords=None):
        print("Searching Items for Sale")
        if not isinstance(keywords, list):
            keywords = [keywords]
        if len(keywords) > 5:
            print("Too many keywords")
            return False, []

        payload = {
            "username" : self.username
        }
        if category is not None:
            payload["category"] = category
        if keywords is not None:
            payload["keywords"] = keywords
        r = requests.post(f'http://{self.front_end_ip}:5001/search_items_for_sale', json=payload)
        r = r.json()
        return r["status"], r["items"]

    def add_item_shopping_cart(self, item_id, quantity):
        print("Adding item to shopping cart")
        payload = {
            "username" : self.username,
            "item_id" : item_id,
            "quantity" : quantity
        }
        r = requests.post(f'http://{self.front_end_ip}:5001/add_item_shopping_cart', json=payload)
        r = r.json()
        return r["status"]

    def remove_item_shopping_cart(self, item_id, quantity):
        print("Removing item from shopping cart")
        payload = {
            "username" : self.username,
            "item_id" : item_id,
            "quantity" : quantity
        }
        r = requests.post(f'http://{self.front_end_ip}:5001/remove_item_shopping_cart', json=payload)
        r = r.json()
        return r["status"]

    def clear_shopping_cart(self):
        print("Clearing shopping cart")
        payload = {
            "username" : self.username
        }
        r = requests.post(f'http://{self.front_end_ip}:5001/clear_shopping_cart', json=payload)
        r = r.json()
        return r["status"]

    def display_shopping_cart(self):
        print("Displaying shopping cart")
        payload = {
            "username" : self.username
        }
        r = requests.post(f'http://{self.front_end_ip}:5001/display_shopping_cart', json=payload)
        r = r.json()
        return r["status"], r["items"]

    def leave_feedback(self, item_id, thumbsup=True):
        print("Leaving feedback")
        feedback = "thumbsup" if thumbsup else "thumbsdown"
        payload = {
            "username" : self.username,
            "feedback" : feedback,
            "item_id" : item_id
        }
        r = requests.post(f'http://{self.front_end_ip}:5001/leave_feedback', json=payload)
        r = r.json()
        return r["status"]

    def get_seller_rating(self, seller_id):
        print("Getting seller rating")
        payload = {
            "username" : self.username,
            "seller_id" : seller_id
        }
        r = requests.post(f'http://{self.front_end_ip}:5001/get_seller_rating', json=payload)
        r = r.json()
        rating = {"thumbsup" : r["thumbsup"], "thumbsdown": r["thumbsdown"]}
        return r["status"], rating

    def get_history(self):
        print("Getting History")
        payload = {
            "username" : self.username,
        }
        r = requests.post(f'http://{self.front_end_ip}:5001/get_history', json=payload)
        r = r.json()
        return r["status"], r["items"]

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
