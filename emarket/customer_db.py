import json
import socket
from emarket import Buyer, CustomerData
from concurrent import futures
import grpc
import customer_pb2
import customer_pb2_grpc

class CustomerDB(customer_pb2_grpc.CustomerServicer):

    def init(self, addr_map, me):
        # self.buyers = []
        self.database = CustomerData(addr_map, me)

    def CreateUser(self, request, context):
        print("Creating user")
        buyer_id = len(self.database.buyers)
        name = request.name
        us = request.username
        pw = request.password
        self.database.add_buyer( name, buyer_id, us, pw )
        # b = Buyer(name, buyer_id, us, pw)
        # self.buyers.append(b)
        return customer_pb2.Confirmation(status=True, error="")

    def ChangeLogin(self, request, context):
        user = request.username
        found = False
        error = ""
        for i_buyer in range(len(self.database.buyers)):
            # print(f"{self.database.buyers[i_buyer].name} : {self.database.buyers[i_buyer].password} : {self.database.buyers[i_buyer].logged_in}")
            if self.database.buyers[i_buyer].username == user :
                
                if request.logging_in and self.database.buyers[i_buyer].password == request.password:
                    found = True
                    self.database.change_login(i_buyer, True)
                    # self.database.buyers[i_buyer].logged_in = True
                    print(f"Logging in {user}")
                elif not request.logging_in:
                    found = True
                    self.database.change_login(i_buyer, False)
                    # self.database.buyers[i_buyer].logged_in = False
                    print(f"Logging out {user}")
                else:
                    error = "Wrong Password!"
                    print(error)
        if not found:
            error = "User not found or password incorrect"
        return customer_pb2.Confirmation(status=found, error=error)

    def CheckLogin(self, request, context):
        user = request.username
        for b in self.database.buyers:
            if b.username == user:
                return customer_pb2.CheckLoginResponse(status=True, logged_in=b.logged_in, error="")
        return customer_pb2.CheckLoginResponse(status=False, logged_in=False, error="User not found")
    
    def UpdateCart(self, request, context):
        # Updating based on keywords not supported
        # payload : {req_id, username, match_fields, new_fields}
        print("Updating")
        username = request.username
        sub = not request.add

        buyer_lst = [i for i in range(len(self.database.buyers)) if self.database.buyers[i].username == username]
        if len(buyer_lst) == 0:
            error = "BUYER NOT FOUND!"
            return customer_pb2.Confirmation(status=False, error=error)
        else:
            buyer_ind = buyer_lst[0]
        
        if request.key == "shopping_cart":
            print("Modifying shopping cart")
            # We already have item in cart
            if request.item_id in [x[0] for x in self.database.buyers[buyer_ind].shopping_cart]:
                for i in range(len(self.database.buyers[buyer_ind].shopping_cart)):
                    if self.database.buyers[buyer_ind].shopping_cart[i][0] == request.item_id:
                        mult = -1 if sub else 1
                        self.database.buyers[buyer_ind].shopping_cart[i][1] += request.quantity * mult

                        # Check if no more items
                        if self.database.buyers[buyer_ind].shopping_cart[i][1] <= 0:
                            print("Removing item from shopping cart")
                            self.database.buyers[buyer_ind].shopping_cart.pop(i)
            else: # New item to cart
                if request.quantity <= 0:
                    error = f"Invalid quantity requested: {request.quantity}"
                    return customer_pb2.Confirmation(status=False, error=error)
                print(self.database.buyers[buyer_ind].shopping_cart)
                print([request.item_id, request.quantity])
                self.database.buyers[buyer_ind].shopping_cart.append( [request.item_id, request.quantity] )
                print(self.database.buyers[buyer_ind].shopping_cart)
            return customer_pb2.Confirmation(status=True, error="")
        elif request.key == "shopping_cart_clear":
            print("Clearing shopping cart")
            self.database.buyers[buyer_ind].shopping_cart = []
            return customer_pb2.Confirmation(status=True, error="")
        elif request.key == "feedback":
            print("Leaving Feedback")
            already = request.item_id in self.database.buyers[buyer_ind].items_given_feedback
            purchased = request.item_id in self.database.buyers[buyer_ind].history
            if already:
                error = "Already Provided Feedback for item"
                return customer_pb2.Confirmation(status=False, error=error)
            elif not purchased:
                error = "Buyer hasn't purchased item"
                return customer_pb2.Confirmation(status=False, error=error)
            else:
                self.database.buyers[buyer_ind].items_given_feedback.append(request.item_id)
                return customer_pb2.Confirmation(status=True, error="")
        else:
            # TODO history, 
            raise NotImplementedError(f"request.key = {request.key}")


    def GetShoppingCart(self, request, context):
        username = request.username
        for i in self.database.buyers:
            if i.username == username:
                print(vars(i))
                item_ids = [x[0] for x in i.shopping_cart]
                quantities = [x[1] for x in i.shopping_cart]
                # .shopping_cart.append( [request.item_id, request.quantity] )
                return customer_pb2.GetShoppingCartResponse(status=True,item_ids=item_ids,quantities=quantities, error="")
                
        error = "Account Not Found"
        return customer_pb2.GetShoppingCartResponse(status=False,item_ids=[],quantities=[], error=error)

    def GetHistory(self, request, context):
        for i in self.database.buyers:
            if i.username == request.username:
                item_ids = [x[0] for x in i.history]
                quantities = [x[1] for x in i.history]
                return customer_pb2.GetShoppingCartResponse(status=True,item_ids=item_ids,quantities=quantities, error="")
        error = "Account Not Found"
        return customer_pb2.GetShoppingCartResponse(status=False,item_ids=[],quantities=[], error=error)

    def MakePurchase(self, request, context):
        print("Making Purchase")
        # Locate buyer, update their history and clear the shopping cart
        for i in self.database.buyers:
            if i.username == request.username:
                i.history.extend(i.shopping_cart)
                i.shopping_cart = []
                return customer_pb2.Confirmation(status=True, error="")
        return customer_pb2.Confirmation(status=False, error="Account Not Found")

def serve():

    addr_map = None
    me = 0

    my_port = 50060 + me

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    p = CustomerDB()
    p.init(addr_map, me)
    customer_pb2_grpc.add_CustomerServicer_to_server(p, server)
    server.add_insecure_port(f'[::]:{my_port}')
    print("starting")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()