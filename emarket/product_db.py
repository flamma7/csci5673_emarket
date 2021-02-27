import json
import socket
from erequests import BackRequestEnum
from emarket import Seller, Item

from concurrent import futures
import grpc
import product_pb2
import product_pb2_grpc


class ProductDB(product_pb2_grpc.ProductServicer):
    def init(self):
        self.sellers = []
        self.products = []    

    def CreateUser(self, request, context):
        print("Creating User")
        seller_id = len(self.sellers)
        s = Seller(request.name, seller_id, request.username, request.password)
        self.sellers.append(s)
        return product_pb2.Confirmation(status=True, error="")

    def ChangeLogin(self, request, context):
        user = request.username
        found = False
        error = ""
        for s in self.sellers:
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
        return product_pb2.Confirmation(status=found, error=error)

    def CheckLogin(self, request, context):
        user = request.username
        for s in self.sellers:
            if s.username == user:
                return product_pb2.CheckLoginResponse(status=True, logged_in=s.logged_in, error="")
        return product_pb2.CheckLoginResponse(status=False, logged_in=False, error="User not found")
    
    def CreateItem(self, request, context):
        print("Putting item for sale")
        if len(self.products) > 0:
            item_id = self.products[-1].item_id + 1
        else:
            item_id = 1

        seller_id = None
        for i in range(len(self.sellers)):
            if self.sellers[i].username == request.username:
                seller_id = self.sellers[i].seller_id
        
                new_item = Item(
                    name=request.item_name,
                    category=request.category,
                    item_id=item_id,
                    keywords=request.keywords,
                    condition_new=request.condition_new,
                    sale_price = request.sale_price,
                    seller_id=seller_id,
                    quantity = request.quantity
                )
                self.products.append( new_item )
                self.sellers[i].items_for_sale.append( new_item )
                return product_pb2.CreateItemResponse(status=True, item_id=item_id, error="")
        return product_pb2.CreateItemResponse(status=False, item_id=item_id, error="Seller Not Found")

    
    def UpdateItem(self, request, context):
        # Updating based on keywords not supported
        # payload : {req_id, username, match_fields, new_fields}
        print("Updating")
        updated = False
        to_delete = []
        for i in range(len(self.products)):
            match = 0
            for j in range(len(request.match_fields)):
                key = request.match_fields[j]
                value = request.value_fields[j]
                
                if key == "item_id":
                    value = int(value)
                if key == "keywords":
                    raise NotImplementedError("Updating based on keyword match not supported")
                if vars(self.products[i])[key] == value:
                    print(f"matched {self.products[i].name}")
                    match += 1
            if match == len(request.match_fields):
                updated = True
                for j in range(len(request.new_fields)):
                    key = request.new_fields[j]
                    value = request.new_values[j]
                    if key in ["quantity", "sale_price"]:
                        value = float(value)
                    if key == "quantity" and value < 0: # Just update
                        vars(self.products[i])[key] += value
                    else: # Update new field with value
                        vars(self.products[i])[key] = value
                if self.products[i].quantity <= 0:
                    to_delete.append( i )
        for td in reversed(to_delete):
            print(f"Deleting {self.products[td].name}")
            sid = self.products[td].seller_id
            ind = self.sellers[sid].items_for_sale.index(self.products[td])
            self.sellers[sid].items_for_sale.pop(ind) # Remove seller object link
            self.products.pop( td )
        error = "" if updated else "No items matched" 
        return product_pb2.Confirmation(status=updated, error=error)
            

    def GetAcct(self, request, context):
        found = False
        seller_id = 0
        for i in self.sellers:
            if i.username == request.username:
                seller_id = i.seller_id
                found = True
        error = "" if found else "Unable to locate acct"
        return product_pb2.GetAcctResponse(status=found, seller_id = seller_id, error=error)

    def GetItemByID(self, request, context):
        print("Searching Item By ID")
        found = False
        items = []
        for s in self.products:
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

    def SearchItem(self, request, context):
        print("SEARCHING!")
        found = False
        items = []
        for s in self.products:
            for keyword in request.keywords:
                # print(keyword)
                # print(s.keywords[0])
                # print("---")
                if keyword in s.keywords[0]:
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

    def GetItem(self, request, context):
        items = []
        found = False
        for s in self.products:
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
        for s in self.sellers:
            if s.seller_id == request.seller_id:
                thumbsup = s.feedback["thumbsup"]
                thumbsdown = s.feedback["thumbsdown"]
                found = True
        error = "" if found else "User not found"
        return product_pb2.GetRatingResponse(status = True, thumbsup=thumbsup, thumbsdown=thumbsdown, error=error)

    def process_error(self, error):
        print(error)
        return {"status" : False, "error" : error}

    def leave_feedback(self, payload):
        print("Leaving Feedback")
        # Find seller id
        seller_id = None
        for p in self.products:
            if p.item_id == payload["item_id"]:
                seller_id = p.seller_id

        if seller_id is not None:
            # Add feedback to seller
            for s in self.sellers:
                if s.seller_id == seller_id:
                    if payload["feedback"] not in list(s.feedback.keys()):
                        return self.process_error("Improper feedback request format")
                    s.feedback[payload["feedback"]] += 1
                    return True
            return self.process_error("Could not locate seller id")
        else:
            return self.process_error("Item not found")

    def make_purchase(self, payload):
        print("Making Purchase")

        # Check the credit card information
        total_cost = 0.0
        for item_id, quantity in payload["items"]:
            item_found = False
            for p in self.products:
                if p.item_id == item_id: # Making the purchase
                    item_found = True
                    if p.quantity >= quantity:
                        total_cost += (p.sale_price * quantity)
                        p.quantity -= quantity

                        # Update the sellers info
                        for s in self.sellers:
                            if s.seller_id == p.seller_id:
                                s.num_items_sold += quantity
                                break
                        break
                    else:
                        return self.process_error(f"Insufficent Quantity of item {p.item_id}. In-stock: {p.quantity}, Req: {quantity}")
            if not item_found:
                return self.process_error(f"Unable to locate item_id: {item_id}")

        # TODO check credit card information & bill the total amount?

        return True

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    p = ProductDB()
    p.init()
    product_pb2_grpc.add_ProductServicer_to_server(p, server)
    server.add_insecure_port('[::]:50051')
    print("starting")
    server.start()
    print("waitin..")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()