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

from os import environ as env
from dotenv import load_dotenv, find_dotenv
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)
else:
    raise FileNotFoundError("Could not locate .env file")

PRODUCT_DB_IP = env.get("PRODUCT_DB_IP")
CUSTOMER_DB_IP = env.get("CUSTOMER_DB_IP")

@app.route("/create_user", methods=["POST"])
def create_user():

    data = json.loads(request.data)
    name = data["name"]
    username = data["username"]
    password = data["password"]

    print(f"Creating new user {username}")
    channel = grpc.insecure_channel(f'{CUSTOMER_DB_IP}:50052')
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

@app.route("/login", methods=["POST"])
def login():
    print("logging in")

    data = json.loads(request.data)
    username = data["username"]
    password = data["password"]

    channel = grpc.insecure_channel(f'{CUSTOMER_DB_IP}:50052')
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

@app.route("/logout", methods=["POST"])
def logout():
    print("logging out")
    data = json.loads(request.data)
    username = data["username"]

    channel = grpc.insecure_channel(f'{CUSTOMER_DB_IP}:50052')
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

@app.route("/search_items_for_sale", methods=["POST"])
def search_items_for_sale():
    print("Searching items for sale")
    data = json.loads(request.data)

    keywords = []
    category = -1 # Won't match any items
    if "keywords" in list(data.keys()):
        keywords = data["keywords"]
    if "category" in list(data.keys()):
        category = data["category"]

    channel = grpc.insecure_channel(f'{PRODUCT_DB_IP}:50051')
    stub = product_pb2_grpc.ProductStub(channel)
    response = stub.SearchItem(product_pb2.SearchItemRequest(
        keywords = keywords,
        category = category
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

@app.route("/add_item_shopping_cart", methods=["POST"])
def add_item_shopping_cart():
    print("Adding items to shopping cart")
    data = json.loads(request.data)
    username = data["username"]
    item_id = data["item_id"]
    quantity = data["quantity"]

    # Check sufficient quantity
    channel = grpc.insecure_channel(f'{PRODUCT_DB_IP}:50051')
    stub = product_pb2_grpc.ProductStub(channel)
    response = stub.GetItemByID(product_pb2.GetItemByIDRequest(
        item_id = item_id
    ))
    if not response.status:
        print("## ERROR ##")
        print(response.error)
        return {"status" : response.status}
    if quantity > response.items[0].quantity:
        print("## ERROR ##")
        print(f"Insufficient quantity available: {response.items[0].quantity} requested: {quantity}")
        return {"status" : False}
    
    # Add item to shopping cart
    channel = grpc.insecure_channel(f'{CUSTOMER_DB_IP}:50052')
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

@app.route("/remove_item_shopping_cart", methods=["POST"])
def remove_item_shopping_cart():
    print("Removing items from shopping cart")
    data = json.loads(request.data)
    username = data["username"]
    item_id = data["item_id"]
    quantity = data["quantity"]

    channel = grpc.insecure_channel(f'{CUSTOMER_DB_IP}:50052')
    stub = customer_pb2_grpc.CustomerStub(channel)
    response = stub.UpdateCart(customer_pb2.UpdateCartRequest(
        username = username,
        add = False,
        key = "shopping_cart",
        item_id = item_id,
        quantity = quantity
    ))
    if not response.status:
        print("## ERROR ##")
        print(response.error)
    return {"status" : response.status}

@app.route("/clear_shopping_cart", methods=["POST"])
def clear_shopping_cart():
    print("Clearing shopping cart")
    data = json.loads(request.data)
    username = data["username"]

    channel = grpc.insecure_channel(f'{CUSTOMER_DB_IP}:50052')
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

@app.route("/display_shopping_cart", methods=["POST"])
def display_shopping_cart():
    print("Displaying shopping cart")
    data = json.loads(request.data)
    username = data["username"]
    
    # Get item_ids and quantities
    channel = grpc.insecure_channel(f'{CUSTOMER_DB_IP}:50052')
    stub = customer_pb2_grpc.CustomerStub(channel)
    response = stub.GetShoppingCart(customer_pb2.CheckLoginRequest(
        username = username
    ))
    if not response.status:
        print("## ERROR ##")
        print(response.error)
        return {"status" : False, "items" : []}
    print(response.item_ids)
    print(response.quantities)
    # return {"status" : response.status}

    channel = grpc.insecure_channel(f'{PRODUCT_DB_IP}:50051')
    stub = product_pb2_grpc.ProductStub(channel)

    items = []

    for i in range(len(response.item_ids)):
        item_id = response.item_ids[i]
        quantity = response.quantities[i]

        response2 = stub.GetItemByID(product_pb2.GetItemByIDRequest(
            item_id = item_id
        ))
        if response2.status:
            items.append( {"name":response2.items[0].name, "quantity" : quantity})
        else:
            print("Unable to locate item")
    return {"status" : True, "items" : items}

def check_logged_in(self, user):
    return user in self.logged_in

@app.route("/leave_feedback", methods=["POST"])
def leave_feedback():
    print("Leaving Feedback")
    data = json.loads(request.data)
    username = data["username"]
    item_id = data["item_id"]
    feedback_type = "thumbsup"

    # Check we've purchased this item before
    channel = grpc.insecure_channel(f'{CUSTOMER_DB_IP}:50052')
    stub = customer_pb2_grpc.CustomerStub(channel)
    response = stub.UpdateCart(customer_pb2.UpdateCartRequest(
        username = username,
        add = True,
        key = "feedback",
        item_id = item_id,
        quantity = 0
    ))
    if not response.status:
        print("## ERROR ##")
        print(response.error)
        return {"status" : response.status}
    
    channel = grpc.insecure_channel(f'{PRODUCT_DB_IP}:50051')
    stub = product_pb2_grpc.ProductStub(channel)
    response = stub.LeaveFeedback(product_pb2.LeaveFeedbackRequest(
        feedback_type = feedback_type,
        item_id = item_id
    ))
    if not response.status:
        print("## ERROR ##")
        print(response.error)
    return {"status" : response.status}

@app.route("/get_seller_rating", methods=["POST"])
def get_seller_rating():
    print("Getting Seller Rating")
    data = json.loads(request.data)
    username = data["username"]
    seller_id = data["seller_id"]

    channel = grpc.insecure_channel(f'{PRODUCT_DB_IP}:50051')
    stub = product_pb2_grpc.ProductStub(channel)
    response = stub.GetRating(product_pb2.GetRatingRequest(
        seller_id = seller_id
    ))
    if not response.status:
        print(response.error)
    return {"status" : response.status, "thumbsup" : response.thumbsup, "thumbsdown" : response.thumbsdown}

@app.route("/get_history", methods=["POST"])
def get_history():
    print("Getting History")
    data = json.loads(request.data)
    username = data["username"]

    channel = grpc.insecure_channel(f'{CUSTOMER_DB_IP}:50052')
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

if __name__ == "__main__":
    app.run(debug=True, port=5001)