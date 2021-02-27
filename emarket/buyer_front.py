import json
import socket
import time
import grpc
import product_pb2
import product_pb2_grpc
import customer_pb2
import customer_pb2_grpc

from flask import Flask, request
app = Flask(__name__)

@app.route("/create_user")#, methods=["GET","POST"])
def create_user():

    name = "Luke"
    username = "flamma7"
    password = "nuts"

    print(f"Creating new user {username}")
    channel = grpc.insecure_channel('localhost:50052')
    stub = customer_pb2_grpc.CustomerStub(channel)
    response = stub.CreateUser(customer_pb2.CreateUserRequest(
        name=name,
        username=username,
        password=password
    ))
    if not response.status:
        print("## ERROR ##")
        print(response.error)
    return {"status":response.status}

@app.route("/login")#, methods=["GET","POST"])
def login():
    print("logging in")

    username = "flamma7"
    password = "nuts"

    channel = grpc.insecure_channel('localhost:50052')
    stub = customer_pb2_grpc.CustomerStub(channel)
    response = stub.ChangeLogin(customer_pb2.ChangeLoginRequest(
        username=username,
        password=password,
        logging_in = True
    ))
    if not response.status:
        print("## ERROR ##")
        print(response.error)
    return {"status":response.status}

@app.route("/logout")
def logout():
    print("logging out")
    # data = json.loads(request.data)
    # username = data["username"]
    username = "flamma7"

    channel = grpc.insecure_channel('localhost:50052')
    stub = customer_pb2_grpc.CustomerStub(channel)
    response = stub.ChangeLogin(customer_pb2.ChangeLoginRequest(
        username=username,
        password="",# Not needed
        logging_in = False
    ))
    if not response.status:
        print("## ERROR ##")
        print(response.error)
    return {"status":response.status}

@app.route("/search_items_for_sale")
def search_items_for_sale():
    #payload = {"req_id":req_id, 
    #     "username" : self.username,
    #     "category" : category,
    #     "keywords" : keywords
    # }
    print("Searching items for sale")

    keywords = ["meme","elon"]


    channel = grpc.insecure_channel('localhost:50051')
    stub = product_pb2_grpc.ProductStub(channel)
    response = stub.SearchItem(product_pb2.SearchItemRequest(
        keywords = keywords
    ))
    items = []
    if not response.status:
        print("## ERROR ##")
        print(response.error)
    else:
        for i in response.items:
            item_dict = {
                "name" : i.name,
                "category" : i.category,
                "item_id" : i.item_id,
                "condition_new" : i.condition_new,
                "sale_price" : i.sale_price,
                "quantity" : i.quantity
            }
            items.append( item_dict )
    return {"status" : response.status, "items" : items}

@app.route("/add_item_shopping_cart")
def add_item_shopping_cart():
    print("Adding items to shopping cart")
    # payload = {"req_id":req_id, 
    #     "username" : self.username,
    #     "item_id" : item_id,
    #     "quantity" : quantity
    # }
    username = "flamma7"
    item_id = 3
    quantity = 1000

    # Check sufficient number of items available
    # req_id = BackRequestEnum.index("get_item")
    # new_payload = {
    #     "req_id" : req_id,
    #     "match_fields" : {"item_id" : payload["item_id"]}
    # }
    # item_resp = self.send_recv_payload(new_payload, customer_db=False)
    # if not item_resp["status"]:
    #     print("Item not found!")
    #     return False
    # target_item = item_resp["items"][0]
    # if target_item["quantity"] < payload["quantity"]:
    #     print("Insufficient number of items available!")
    #     return False
    channel = grpc.insecure_channel('localhost:50052')
    stub = customer_pb2_grpc.CustomerStub(channel)
    response = stub.UpdateCart(customer_pb2.UpdateCartRequest(
        username = username,
        add = True,
        key = "shopping_cart",
        item_id = item_id,
        quantity = quantity
    ))
    if not response.status:
        print("## ERROR ##")
        print(response.error)
    return {"status" : response.status}
    # req_id = BackRequestEnum.index("add")
    # new_payload = {"req_id" : req_id,
    #     "username" : payload["username"],
    #     "key" : "shopping_cart",
    #     "value" : [payload["item_id"], payload["quantity"]]
    # }
    # return self.send_recv_payload(new_payload, customer_db=True)

@app.route("/remove_item_shopping_cart")
def remove_item_shopping_cart():
    print("Removing items from shopping cart")
    # payload = {"req_id":req_id, 
    #     "username" : self.username,
    #     "item_id" : item_id,
    #     "quantity" : quantity
    # }
    username = "flamma7"
    item_id = 3
    quantity = -1000

    channel = grpc.insecure_channel('localhost:50052')
    stub = customer_pb2_grpc.CustomerStub(channel)
    response = stub.UpdateCart(customer_pb2.UpdateCartRequest(
        username = username,
        add = True,
        key = "shopping_cart",
        item_id = item_id,
        quantity = quantity
    ))
    if not response.status:
        print("## ERROR ##")
        print(response.error)
    return {"status" : response.status}

    # req_id = BackRequestEnum.index("sub")
    # new_payload = {"req_id" : req_id,
    #     "username" : payload["username"],
    #     "key" : "shopping_cart",
    #     "value" : [payload["item_id"], payload["quantity"]]
    # }
    # return self.send_recv_payload(new_payload, customer_db=True)

@app.route("/clear_shopping_cart")
def clear_shopping_cart():
    print("Clearing shopping cart")
    # payload = {"req_id":req_id, 
    #     "username" : self.username
    # }
    username = "flamma7"

    channel = grpc.insecure_channel('localhost:50052')
    stub = customer_pb2_grpc.CustomerStub(channel)
    response = stub.UpdateCart(customer_pb2.UpdateCartRequest(
        username = username,
        add = True,
        key = "shopping_cart_clear",
        item_id = 0,
        quantity = 0
    ))
    if not response.status:
        print("## ERROR ##")
        print(response.error)
    return {"status" : response.status}
    # req_id = BackRequestEnum.index("add")
    # new_payload = {
    #     "req_id" : req_id,
    #     "username" : payload["username"],
    #     "key" : "shopping_cart_clear"
    # }
    # return self.send_recv_payload(new_payload, customer_db=True)

@app.route("/display_shopping_cart")
def display_shopping_cart():
    print("Displaying shopping cart")
    # payload = {"req_id":req_id, 
    #     "username" : self.username
    # }
    username = "flamma7"
    
    channel = grpc.insecure_channel('localhost:50052')
    stub = customer_pb2_grpc.CustomerStub(channel)
    response = stub.GetShoppingCart(customer_pb2.CheckLoginRequest(
        username = username
    ))
    if not response.status:
        print("## ERROR ##")
        print(response.error)
        return {"status" : False, "items" : []}
    # print(response.item_ids)
    # print(response.quantities)
    # return {"status" : response.status}



    # req_id = BackRequestEnum.index("get_acct")
    # new_payload = {
    #     "req_id" : req_id,
    #     "username" : payload["username"],
    #     "fields" : ["shopping_cart"]
    # }
    # data_resp = self.send_recv_payload(new_payload, customer_db=True)
    # if not data_resp["status"]:
    #     return False

    # TODO ping product DB
    channel = grpc.insecure_channel('localhost:50051')
    stub = product_pb2_grpc.ProductStub(channel)

    items = []
    for i in range(len(response.item_ids)):
        item_id = response.item_ids[i]
        quantity = response.quantities[i]

        response = stub.GetItemByID(product_pb2.GetItemByIDRequest(
            item_id = item_id
        ))
        if response.status:
            items.append( {"name":response.items[0].name, "quantity" : quantity})
        else:
            print("Unable to locate item")
    return {"status" : True, "items" : items}

    # else:
    #     return_msg = {"status":True, "items":[]}
    #     for item_id, quant in data_resp["shopping_cart"]:
    #         req_id = BackRequestEnum.index("get_item")
    #         new_payload = {
    #             "req_id" : req_id,
    #             "match_fields" : {"item_id" : item_id}
    #         }
    #         item_resp = self.send_recv_payload(new_payload, customer_db=False)
    #         if item_resp["status"]:
    #             return_msg["items"].append(item_resp["items"][0])
    #             return_msg["items"][-1]["quantity"] = quant
    #         else:
    #             print("Unable to locate item -- out of sync!")
    #             return False
    #     return return_msg

def check_logged_in(self, user):
    return user in self.logged_in

@app.route("/leave_feedback")
def leave_feedback():
    print("Leaving Feedback")

    username = "flamma7"
    item_id = 3
    feedback_type = "thumbsup"

    channel = grpc.insecure_channel('localhost:50052')
    stub = customer_pb2_grpc.CustomerStub(channel)
    response = stub.UpdateCart(customer_pb2.UpdateCartRequest(
        username = username,
        add = True,
        key = "feedback",
        item_id = item_id,
        quantity = 0
    ))
    # if not response.status:
    #     print("## ERROR ##")
    #     print(response.error)
    #     return {"status" : response.status}

    # Check if we haven't left a review yet
    # req_id = BackRequestEnum.index("add")
    # new_payload = {
    #     "req_id" : req_id,
    #     "username" : payload["username"],
    #     "key" : "feedback",
    #     "item_id" : payload["item_id"]
    # }
    # resp = self.send_recv_payload(new_payload, customer_db=True)
    
    channel = grpc.insecure_channel('localhost:50051')
    stub = product_pb2_grpc.ProductStub(channel)
    response = stub.LeaveFeedback(product_pb2.LeaveFeedbackRequest(
        feedback_type = feedback_type,
        item_id = item_id
    ))
    if not response.status:
        print("## ERROR ##")
        print(response.error)
    return {"status" : response.status}

    # if resp["status"]:
    #     req_id = BackRequestEnum.index("leave_feedback")
    #     new_payload = {
    #         "req_id" : req_id,
    #         "feedback" : payload["feedback"],
    #         "item_id" : payload["item_id"]
    #     }
    #     return self.send_recv_payload(new_payload, customer_db=False)
    # else:
    #     return resp

@app.route("/get_seller_rating")
def get_seller_rating():
    print("Getting Seller Rating")

    seller_id = 1

    channel = grpc.insecure_channel('localhost:50051')
    stub = product_pb2_grpc.ProductStub(channel)
    response = stub.GetRating(product_pb2.GetRatingRequest(
        seller_id = seller_id
    ))
    if not response.status:
        print(response.error)
    return {"status" : response.status, "thumbsup" : response.thumbsup, "thumbsdown" : response.thumbsdown}

    # req_id = BackRequestEnum.index("get_rating")
    # new_payload = {
    #     "req_id" : req_id,
    #     "seller_id" : payload["seller_id"],
    # }
    # return self.send_recv_payload(new_payload, customer_db=False)

@app.route("/get_history")
def get_history():
    print("Getting History")

    username = "flamma7"

    channel = grpc.insecure_channel('localhost:50052')
    stub = customer_pb2_grpc.CustomerStub(channel)
    response = stub.GetHistory(customer_pb2.CheckLoginRequest(
        username = username
    ))
    if not response.status:
        print("## ERROR ##")
        print(response.error)
        return {"status" : False, "items" : []}    
    ids = response.item_ids
    quants = response.quantities
    items = [[ids[i], quants[i]] for i in range(len(ids))]
    return {"status" : True, "items" : items}

    # req_id = BackRequestEnum.index("get_history")
    # new_payload = {
    #     "req_id" : req_id,
    #     "username" : payload["username"]
    # }
    # return self.send_recv_payload(new_payload, customer_db=True)

def make_purchase(self, payload):
    print("Making Purchase")

    # Get buyer's shopping cart
    resp = self.display_shopping_cart({"username" : payload["username"]})
    if not resp["status"]:
        return resp
    items = [[x["item_id"], x["quantity"]] for x in resp["items"]]

    # Make the purchase
    req_id = BackRequestEnum.index("make_purchase")
    new_payload = {
        "req_id" : req_id,
        "cc_name" : payload["cc_name"],
        "cc_number" : payload["cc_number"],
        "cc_expiration" : payload["cc_expiration"],
        "items" : items
    }
    resp = self.send_recv_payload(new_payload, customer_db=False)
    if not resp["status"]:
        return resp

    # Update the clients account about the purchase
    req_id = BackRequestEnum.index("make_purchase")
    new_payload = {
        "req_id" : req_id,
        "username" : payload["username"]
    }
    resp = self.send_recv_payload(new_payload, customer_db=True)
    if not resp["status"]:
        return resp

    return True

if __name__ == "__main__":
    app.run(debug=True, port=5001)