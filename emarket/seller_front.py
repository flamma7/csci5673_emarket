import json
import socket
from emarket.requests import RequestEnum
class SellerFront:

    def __init__(self, host="127.0.0.1", front_port=11311, back_port=11314):
        self.logged_in = []
        self.host = host
        self.front_port = front_port
        self.back_port = back_port

    def run(self):
        print("Seller Front Running")
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((self.host, self.front_port))
                s.listen()            
                conn, addr = s.accept()
                with conn:
                    print('Connected by', addr)
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

    def handle_payload(self, payload):
        req_id = payload["req_id"]
        
        # Check if we're creating a new user
        if req_id == RequestEnum.index("create_user"):
            return self.create_user(payload)
        elif req_id == RequestEnum.index("login"):
            return self.login(payload)
        elif req_id == RequestEnum.index("logout"):
            return self.logout(payload)
        else: # Check that the user is logged in
            if not self.logged_in(payload["seller_id"]):
                return False
            
            if req_id == RequestEnum.index("put_item_for_sale"):
                pass
            elif req_id == RequestEnum.index("change_sale_price_item"):
                pass
            elif req_id == RequestEnum.index("remove_item_from_sale"):
                pass
            elif req_id == RequestEnum.index("display_active_seller_items"):
                pass
            else:
                print(f"Unrecognized Request: {req_id}")
                return False

    def create_user(self, payload):
        print(f"Creating new user {payload['username']}")

        # Create new entry in product database
        seller_id = 1
        return {"status":True, "seller_id":seller_id}

    def login(self, payload):
        print("logging in")

        if self.check_logged_in(payload["username"]):
            print("Already logged in!")
            return True
        else:
            # Check if password is correct with db -> return False

            self.logged_in.append(payload["username"])
            return True
    
    def logout(self, payload):
        print("logging out")
        if not self.check_logged_in(payload["username"]):
            print("Not logged in!")
        else:
            i = self.logged_in.index(payload["username"])
            self.logged_in.pop(i)
        return True
    
    def put_item_for_sale(self, payload):
        print("Putting item for sale")
        pass

    def change_sale_price_item(self, payload):
        print("Changing Sale Price of Item")
        pass

    def remove_item_from_sale(self, payload):
        print("Removing item")
        pass
    
    def display_active_seller_items(self, payload):
        print("Displaying Active Items")
        pass

    def check_logged_in(self, user):
        return user in self.logged_in

if __name__ == "__main__":
    sf = SellerFront()
    sf.run()