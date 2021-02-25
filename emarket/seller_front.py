import json
import socket
import time
from emarket.requests import FrontRequestEnum, BackRequestEnum
class SellerFront:

    def __init__(self, host="127.0.0.1", front_port=11311, back_port=11314, delay=0.01):
        self.host = host
        self.front_port = front_port
        self.back_port = back_port
        self.delay = delay
        print(f"Delay time: {self.delay}")

    def run(self):
        print("Seller Front Running")
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
            
            if req_id == FrontRequestEnum.index("put_item_for_sale"):
                return self.put_item_for_sale(payload)
            elif req_id == FrontRequestEnum.index("change_sale_price_item"):
                return self.change_sale_price_item(payload)
            elif req_id == FrontRequestEnum.index("remove_item_from_sale"):
                return self.remove_item_from_sale(payload)
            elif req_id == FrontRequestEnum.index("display_active_seller_items"):
                return self.display_active_seller_items(payload)
            else:
                print(f"Unrecognized Request: {req_id}")
                return False
    
    def send_recv_payload(self, payload):
        time.sleep(self.delay)
        json_payload = json.dumps(payload, indent=4)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.back_port))
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
        req_id = BackRequestEnum.index("login")
        new_payload = {"req_id":req_id,
            "username" : payload["username"],
            "password" : payload["password"]
        }
        resp = self.send_recv_payload(new_payload)
        return resp["status"]
    
    def logout(self, payload):
        print("logging out")
        req_id = BackRequestEnum.index("logout")
        new_payload = {"req_id":req_id,
            "username" : payload["username"]
        }
        resp = self.send_recv_payload(new_payload)
        return resp["status"]
    
    def put_item_for_sale(self, payload):
        print("Putting item for sale")
        req_id = BackRequestEnum.index("create_item")
        new_payload = {"req_id":req_id, 
            "username": payload["username"],
            "item" :payload["item"],
            "quantity" : payload["quantity"]
        }
        return self.send_recv_payload(new_payload)

    def change_sale_price_item(self, payload):
        print("Changing Sale Price of Item")
        #payload = {"req_id":req_id, "username" : self.username,
        #    "item_id":item_id, "new_price" : new_price}
        req_id = BackRequestEnum.index("update")
        new_payload = {"req_id":req_id, 
            "username":payload["username"],
            "match_fields" : {"item_id" : payload["item_id"]},
            "new_fields" : {"sale_price" : payload["new_price"]}
        }
        return self.send_recv_payload(new_payload)

    def remove_item_from_sale(self, payload):
        print("Removing item")
        #payload = {"req_id":req_id, "username" : self.username,
        #    "item_id":item_id, "quantity" : quantity}
        req_id = BackRequestEnum.index("update")
        new_payload = {"req_id":req_id, 
            "username":payload["username"],
            "match_fields" : {"item_id" : payload["item_id"]},
            "new_fields" : {"quantity" : 0}
        }
        return self.send_recv_payload(new_payload)
    
    def display_active_seller_items(self, payload):
        print("Displaying Active Items")

        ## Get Seller ID
        req_id = BackRequestEnum.index("get_acct")
        new_payload = {"req_id" : req_id,
            "username" : payload["username"],
            "fields" : ["seller_id"]}
        resp = self.send_recv_payload(new_payload)
        if not resp["status"]:
            return False
        seller_id = resp["seller_id"]

        # Get Items
        req_id = BackRequestEnum.index("get_item")
        new_payload = {"req_id":req_id, 
            "username":payload["username"],
            "match_fields" : {"seller_id" : seller_id}
        }
        return self.send_recv_payload(new_payload)

    def check_logged_in(self, user):
        req_id = BackRequestEnum.index("check_login")
        new_payload = {"req_id":req_id,
            "username" : user
        }
        resp = self.send_recv_payload(new_payload)
        return resp["status"]

if __name__ == "__main__":
    sf = SellerFront()
    sf.run()