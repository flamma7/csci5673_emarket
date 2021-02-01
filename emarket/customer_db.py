import json
import socket
from emarket.requests import BackRequestEnum
from emarket.emarket import Buyer

class CustomerDB:
    def __init__(self, host="127.0.0.1", port=11313):
        self.host = host
        self.port = port
        self.buyers = []

    def run(self):
        print("Running Customer DB")
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
        elif req_id == BackRequestEnum.index("add"):
            return self.update(payload, sub=False)
        elif req_id == BackRequestEnum.index("sub"):
            return self.update(payload, sub=True)
        elif req_id == BackRequestEnum.index("get_acct"):
            return self.get_acct(payload)
        else:
            raise ValueError(f"Unrecognized Request Enum: {req_id}")

    def create_acct(self, payload):
        print("Creating user")
        buyer_id = len(self.buyers)
        name = payload["name"]
        us = payload["username"]
        pw = payload["password"]
        b = Buyer(name, buyer_id, us, pw)
        self.buyers.append(b)
        return {"status":True, "buyer_id" : buyer_id}
    
    def update(self, payload, sub=False):
        # Updating based on keywords not supported
        # payload : {req_id, username, match_fields, new_fields}
        print("Updating")

        buyer_lst = [i for i in range(len(self.buyers)) if self.buyers[i].username == payload["username"]]
        if len(buyer_lst) == 0:
            return False
        else:
            buyer_ind = buyer_lst[0]
        
        if payload["key"] == "shopping_cart":

            # We already have item in cart
            if payload["value"][0] in [x[0] for x in self.buyers[buyer_ind].shopping_cart]:
                for i in range(len(self.buyers[buyer_ind].shopping_cart)):
                    if self.buyers[buyer_ind].shopping_cart[i][0] == payload["value"][0]:
                        mult = -1 if sub else 1
                        self.buyers[buyer_ind].shopping_cart[i][1] += payload["value"][1] * mult

                        # Check if no more items
                        if self.buyers[buyer_ind].shopping_cart[i][1] <= 0:
                            self.buyers[buyer_ind].shopping_cart.pop(i)
            else: # Add item to cart
                if payload["value"][1] <= 0:
                    return False
                self.buyers[buyer_ind].shopping_cart.append( payload["value"] )
            return True
        elif payload["key"] == "shopping_cart_clear":
            self.buyers[buyer_ind].shopping_cart = []
            return True
        else:
            # TODO history, 
            raise NotImplementedError(f"payload[key] = {payload['key']}")

    def get_acct(self, payload):
        for i in self.buyers:
            if i.username == payload["username"]:
                new_payload = {"status":True}
                for f in payload["fields"]:
                    new_payload[f] = vars(i)[f]
                return new_payload
        return {"status": False}
