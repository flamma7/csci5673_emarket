import json
import socket
from erequests import BackRequestEnum
from emarket import Seller, Item, ProductData

from concurrent import futures
import grpc
import product_pb2
import product_pb2_grpc

from os import environ as env
from dotenv import load_dotenv, find_dotenv
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)
else:
    raise FileNotFoundError("Could not locate .env file")

class ProductDB(product_pb2_grpc.ProductServicer):
    def init(self, my_ip, other_ips):
        self.database = ProductData(my_ip, other_ips)

    def CreateUser(self, request, context):
        print("Creating User")
        seller_id = len(self.database.sellers)
        self.database.add_seller( request.name, seller_id, request.username, request.password )
        return product_pb2.Confirmation(status=True, error="")

    def ChangeLogin(self, request, context):
        user = request.username
        found = False
        error = ""
        for i in range(len(self.database.sellers)):
            # print(f"{s.name} : {s.password} : {s.logged_in}")
            if self.database.sellers[i].username == user :
                
                if request.logging_in and self.database.sellers[i].password == request.password:
                    self.database.change_login(i, True)
                    found = True
                    print(f"Logging in {user}")
                elif not request.logging_in:
                    self.database.change_login(i, False)
                    found = True
                    print(f"Logging out {user}")
                else:
                    error = "Wrong Password!"
                    print(error)
        if not found:
            error = "User not found or password incorrect"
        return product_pb2.Confirmation(status=found, error=error)

    def CheckLogin(self, request, context):
        user = request.username
        for s in self.database.sellers:
            if s.username == user:
                return product_pb2.CheckLoginResponse(status=True, logged_in=s.logged_in, error="")
        return product_pb2.CheckLoginResponse(status=False, logged_in=False, error="User not found")
    
    def CreateItem(self, request, context):
        print("Putting item for sale")
        if len(self.database.products) > 0:
            item_id = self.database.products[-1].item_id + 1
        else:
            item_id = 1

        seller_id = None
        for i in range(len(self.database.sellers)):
            if self.database.sellers[i].username == request.username:
                seller_id = self.database.sellers[i].seller_id
    
                # self.database.add_product_outer(arg_list)
                self.database.add_product(
                    name=request.item_name,
                    category=request.category,
                    item_id=item_id,
                    keywords=list(request.keywords),
                    condition_new=request.condition_new,
                    sale_price=request.sale_price,
                    seller_id=seller_id,
                    quantity =request.quantity
                )
                return product_pb2.CreateItemResponse(status=True, item_id=item_id, error="")
        return product_pb2.CreateItemResponse(status=False, item_id=item_id, error="Seller Not Found")

    def DeleteItem(self, request, context):
        print("Removing Items")
        matched = False
        for i in range(len(self.database.products)):
            if self.database.products[i].item_id == request.item_id:
                # Delete item
                matched = True
                self.database.remove_item(i, request.quantity)
                break
                
        if matched:
            error = ""
            updated = True
        else:
            error = "No items matched" 
            updated = False
        return product_pb2.Confirmation(status=updated, error=error)

    def ChangePrice(self, request, context):
        print("Changing Price")
        matched = False
        for i in range(len(self.database.products)):
            if self.database.products[i].item_id == request.item_id:
                self.database.change_price(i, request.sale_price)
                matched = True

        if matched:
            error = ""
            updated = True
        else:
            error = "No items matched" 
            updated = False
        return product_pb2.Confirmation(status=updated, error=error)

    def GetAcct(self, request, context):
        found = False
        seller_id = 0
        for i in self.database.sellers:
            if i.username == request.username:
                seller_id = i.seller_id
                found = True
        error = "" if found else "Unable to locate acct"
        return product_pb2.GetAcctResponse(status=found, seller_id = seller_id, error=error)

    def GetItemByID(self, request, context):
        print("Searching Item By ID")
        found = False
        items = []
        for s in self.database.products:
            if s.item_id == request.item_id:
                items.append( product_pb2.ItemMsg(
                name = s.name,
                category = s.category,
                item_id = s.item_id,
                condition_new = s.condition_new,
                sale_price = s.sale_price,
                quantity = s.quantity
                ))
                found = True
                print(f"matching {s.name}")
                break
        # print(items)
        error = "" if found else "Unable to locate item"
        return product_pb2.GetItemResponse(status=found, items = items, error=error)

    # Pass in Keywords or Category and get items
    def SearchItem(self, request, context):
        print("Searching by keywords or category")
        found = False
        items = []
        print(request.category)
        print(request.keywords)
        for s in self.database.products:
            print(vars(s))
            if request.category == s.category:
                    items.append( product_pb2.ItemMsg(
                    name = s.name,
                    category = s.category,
                    item_id = s.item_id,
                    condition_new = s.condition_new,
                    sale_price = s.sale_price,
                    quantity = s.quantity
                    ))
                    found = True
                    print(f"matching {s.name}")
            for keyword in request.keywords:
                if keyword in s.keywords:
                    items.append( product_pb2.ItemMsg(
                    name = s.name,
                    category = s.category,
                    item_id = s.item_id,
                    condition_new = s.condition_new,
                    sale_price = s.sale_price,
                    quantity = s.quantity
                    ))
                    found = True
                    print(f"matching {s.name}")
                    break

        # print(items)
        error = "" if found else "Unable to locate any items"
        return product_pb2.GetItemResponse(status=found, items = items, error=error)

    # Pass in seller id to get item
    def GetItem(self, request, context):
        items = []
        found = False
        for s in self.database.products:
            if s.seller_id == request.seller_id:
                items.append( product_pb2.ItemMsg(
                    name = s.name,
                    category = s.category,
                    item_id = s.item_id,
                    condition_new = s.condition_new,
                    sale_price = s.sale_price,
                    quantity = s.quantity
                ))
                found = True
        error = "" if found else "Unable to locate any items"
        return product_pb2.GetItemResponse(status=found, items = items, error=error)

    def GetRating(self, request, context):
        print("Getting Rating")
        found = False
        thumbsup, thumbsdown = 0, 0
        # Buyer is checking seller rating
        for s in self.database.sellers:
            if s.seller_id == request.seller_id:
                thumbsup = s.feedback["thumbsup"]
                thumbsdown = s.feedback["thumbsdown"]
                found = True
        error = "" if found else "User not found"
        return product_pb2.GetRatingResponse(status = True, thumbsup=thumbsup, thumbsdown=thumbsdown, error=error)

    def process_error(self, error):
        print(error)
        return {"status" : False, "error" : error}

    def LeaveFeedback(self, request, context):
        print("Leaving Feedback")
        # Find seller id
        seller_id = None
        for p in self.database.products:
            if p.item_id == request.item_id:
                seller_id = p.seller_id

        if seller_id is not None:
            # Add feedback to seller
            for i in range(len(self.database.sellers)):
                if self.database.sellers[i].seller_id == seller_id:
                    if request.feedback_type not in list(self.database.sellers[i].feedback.keys()):
                        error = "Improper feedback request format"
                        return product_pb2.Confirmation(status=False, error=error)
                    self.database.leave_feedback(i, request.feedback_type)
                    # self.database.sellers[i].feedback[request.feedback_type] += 1
                    return product_pb2.Confirmation(status=True, error="")
            return product_pb2.Confirmation(status=False, error="Could not locate seller id")
        else:
            return product_pb2.Confirmation(status=False, error="Item not found")

    def MakePurchase(self, request, context):
        print("Making Purchase")

        # Check the credit card information
        total_cost = 0.0
        for i in range(len(request.item_ids)):
            item_id = request.item_ids[i]
            quantity = request.quantities[i]

            item_found = False
            for i_product in range(len(self.database.products)):
                if self.database.products[i_product].item_id == item_id: # Making the purchase
                    item_found = True
                    if self.database.products[i_product].quantity >= quantity:
                        sale_price = self.database.products[i_product].sale_price
                        total_cost += (sale_price * quantity)
                        self.database.remove_item(i_product, quantity)
                        # self.database.products[i_product].quantity -= quantity

                        # Update the sellers info
                        for i_seller in range(len(self.database.sellers)):
                            if self.database.sellers[i_seller].seller_id == self.database.products[i_product].seller_id:
                                self.database.make_sale(i_seller, quantity)
                                # self.database.sellers[i_seller].num_items_sold += quantity
                                break
                        break
                    else:
                        error = f"Insufficent Quantity of item {self.database.products[i_product].item_id}. In-stock: {self.database.products[i_product].quantity}, Req: {quantity}"
                        return product_pb2.Confirmation(status=False, error=error)
            if not item_found:
                error = f"Unable to locate item_id: {item_id}"
                return product_pb2.Confirmation(status=False, error=error)

        return product_pb2.Confirmation(status=True, error="")

def get_ip_info():
    CURRENT_PRODUCT_DB = env.get("CURRENT_PRODUCT_DB")
    other_ips = []
    # str_ = "ABCD"
    str_ = env.get("ALL_PRODUCT_DBS")
    i = 0
    for c in str_:
        curr_ip = env.get(f"PRODUCT_DB_{c}_IP")
        new_port = 4321 + i
        new_grpc = 50051 + i
        new_ip = curr_ip + f":{new_port}"
        
        i += 1
        if CURRENT_PRODUCT_DB == c:
            my_ip = new_ip
            grpc_port = new_grpc
        else:
            other_ips.append(new_ip)

    return grpc_port, my_ip, other_ips

def serve():

    grpc_port, my_ip, other_ips = get_ip_info()
    # print(my_ip)
    # print(other_ips)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    p = ProductDB()
    p.init(my_ip, other_ips)
    product_pb2_grpc.add_ProductServicer_to_server(p, server)
    server.add_insecure_port(f'[::]:{grpc_port}')
    print("starting")
    server.start()
    print("waitin..")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()