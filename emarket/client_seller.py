import json
import socket
import time
from emarket.requests import RequestEnum

class ClientSeller:

    def __init__(self, seller_id=None, host="127.0.0.1", port=11311): # None for new client
        self.host = host
        self.port = port

        if seller_id is None:
            print("New user: call create_user()")
        self.seller_id = seller_id
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

    def create_user(self, username, password):
        if len(username) > 12 or len(password) > 12:
            raise ValueError("Max length username or password 12 characters")
        print(f"Creating user {username}")
        req_id = RequestEnum.index("create_user")
        payload = {"req_id":req_id, "username" : username,
            "password": password}
        data_resp = self.send_recv_payload(payload)
        if data_resp["status"] == False:
            return False
        return data_resp["seller_id"]

    def login(self, username, password):
        print("Logging in")
        if len(username) > 12 or len(password) > 12:
            raise ValueError("Max length username or password 12 characters")
        req_id = RequestEnum.index("login")
        payload = {"req_id":req_id, "username" : username,
            "password": password}
        data_resp = self.send_recv_payload(payload)
        return data_resp["status"]
    
    def logout(self, username):
        print("Logging out")
        if len(username) > 12:
            raise ValueError("Max length username or password 12 characters")
        req_id = RequestEnum.index("logout")
        payload = {"req_id":req_id, "username" : username}
        data_resp = self.send_recv_payload(payload)
        return data_resp["status"]

    def put_item_for_sale(self, item, quantity):
        # Initiate connection with seller_front
        item_id = 2
        return item_id

    def change_sale_price_item(self, item_id, new_price):
        # Initiate connection with seller_front
        return True
    
    def remove_item_from_sale(self, item_id, quantity):
        # Initiate connection with seller_front
        return True

    def display_active_seller_items(self):
        # Initiate connection with seller_front
        # Use self.seller_id
        return ["Items"]