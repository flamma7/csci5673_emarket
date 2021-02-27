import json
import socket
from emarket import Buyer
from concurrent import futures
import grpc
import customer_pb2
import customer_pb2_grpc

class CustomerDB(customer_pb2_grpc.CustomerServicer):

    def init(self):
        self.buyers = []

    def CreateUser(self, request, context):
        print("Creating user")
        buyer_id = len(self.buyers)
        name = request.name
        us = request.username
        pw = request.password
        b = Buyer(name, buyer_id, us, pw)
        self.buyers.append(b)
        return customer_pb2.Confirmation(status=True, error="")

    def ChangeLogin(self, request, context):
        user = request.username
        found = False
        error = ""
        for s in self.buyers:
            # print(f"{s.name} : {s.password} : {s.logged_in}")
            if s.username == user :
                
                if request.logging_in and s.password == request.password:
                    found = True
                    s.logged_in = True
                    print(f"Logging in {user}")
                elif not request.logging_in:
                    found = True
                    s.logged_in = False
                    print(f"Logging out {user}")
                else:
                    error = "Wrong Password!"
                    print(error)
        if not found:
            error = "User not found or password incorrect"
        return customer_pb2.Confirmation(status=found, error=error)
    
    def UpdateCart(self, request, context):
        # Updating based on keywords not supported
        # payload : {req_id, username, match_fields, new_fields}
        print("Updating")
        username = request.username
        sub = not request.add

        buyer_lst = [i for i in range(len(self.buyers)) if self.buyers[i].username == username]
        if len(buyer_lst) == 0:
            error = "BUYER NOT FOUND!"
            return customer_pb2.Confirmation(status=False, error=error)
        else:
            buyer_ind = buyer_lst[0]
        
        if request.key == "shopping_cart":
            print("Modifying shopping cart")
            # We already have item in cart
            if request.item_id in [x[0] for x in self.buyers[buyer_ind].shopping_cart]:
                for i in range(len(self.buyers[buyer_ind].shopping_cart)):
                    if self.buyers[buyer_ind].shopping_cart[i][0] == request.item_id:
                        mult = -1 if sub else 1
                        self.buyers[buyer_ind].shopping_cart[i][1] += request.quantity * mult

                        # Check if no more items
                        if self.buyers[buyer_ind].shopping_cart[i][1] <= 0:
                            self.buyers[buyer_ind].shopping_cart.pop(i)
            else: # Add item to cart
                if request.quantity <= 0:
                    error = f"Invalid quantity requested: {request.quantity}"
                    return customer_pb2.Confirmation(status=False, error=error)
                self.buyers[buyer_ind].shopping_cart.append( [request.item_id, request.quantity] )
            return customer_pb2.Confirmation(status=True, error="")
        elif request.key == "shopping_cart_clear":
            print("Clearing shopping cart")
            self.buyers[buyer_ind].shopping_cart = []
            return customer_pb2.Confirmation(status=True, error="")
        elif request.key == "feedback":
            already = request.item_id in self.buyers[buyer_ind].items_given_feedback
            purchased = request.item_id in self.buyers[buyer_ind].history
            if already:
                error = "Already Provided Feedback for item"
                return customer_pb2.Confirmation(status=False, error=error)
            elif not purchased:
                error = "Buyer hasn't purchased item"
                return customer_pb2.Confirmation(status=False, error=error)
            else:
                self.buyers[buyer_ind].items_given_feedback.append(request.item_id)
                return customer_pb2.Confirmation(status=True, error="")
        else:
            # TODO history, 
            raise NotImplementedError(f"request.key = {request.key}")


    def GetShoppingCart(self, request, context):
        username = request.username
        for i in self.buyers:
            if i.username == username:
                item_ids = [x[0] for x in i.shopping_cart]
                quantities = [x[1] for x in i.shopping_cart]
                # .shopping_cart.append( [request.item_id, request.quantity] )
                return customer_pb2.GetShoppingCartResponse(status=True,item_ids=item_ids,quantities=quantities, error="")
                
        error = "Account Not Found"
        return customer_pb2.GetShoppingCartResponse(status=False,item_ids=[],quantities=[], error=error)

    def GetHistory(self, request, context):
        for i in self.buyers:
            if i.username == request.username:
                item_ids = [x[0] for x in i.history]
                quantities = [x[1] for x in i.history]
                return customer_pb2.GetShoppingCartResponse(status=True,item_ids=item_ids,quantities=quantities, error="")
        error = "Account Not Found"
        return customer_pb2.GetShoppingCartResponse(status=False,item_ids=[],quantities=[], error=error)

    def process_error(self, error):
        print(error)
        return {"status" : False, "error" : error}

    def make_purchase(self, payload):
        print("Making Purchase")
        # Locate buyer, update their history and clear the shopping cart
        for i in self.buyers:
            if i.username == payload["username"]:
                i.history.extend(i.shopping_cart)
                i.shopping_cart = []
                return True
        return self.process_error("Account Not Found")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    p = CustomerDB()
    p.init()
    customer_pb2_grpc.add_CustomerServicer_to_server(p, server)
    server.add_insecure_port('[::]:50052')
    print("starting")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()