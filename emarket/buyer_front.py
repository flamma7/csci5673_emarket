import json
import socket
import time
import grpc
import product_pb2
import product_pb2_grpc
import customer_pb2
import customer_pb2_grpc
import random

from flask import Flask, request
app = Flask(__name__)

from os import environ as env
from dotenv import load_dotenv, find_dotenv
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)
else:
    raise FileNotFoundError("Could not locate .env file")

ALL_PRODUCT_DBS = env.get("ALL_PRODUCT_DBS")
ALL_CUSTOMER_DBS = env.get("ALL_CUSTOMER_DBS")

# FRONT_BUYER_IP = env.get("FRONT_BUYER_IP")
CURRENT_FRONT_BUYER = env.get("CURRENT_FRONT_BUYER")
FRONT_BUYER_IP = env.get(f"FRONT_SELLER_{CURRENT_FRONT_BUYER}_IP")

def get_product_db_ip():
    # Select a random IP to request
    ip_port_list = []
    grpc_port = 50051
    for c in ALL_PRODUCT_DBS:
        full_ip = env.get(f"PRODUCT_DB_{c}_IP") + f":{grpc_port}"
        ip_port_list.append( full_ip )
        grpc_port += 1
    return random.choice( ip_port_list )

def get_customer_db_ip():
    return "127.0.0.1:50061"

    ip_port_list = []
    grpc_port = 50061
    for c in ALL_CUSTOMER_DBS:
        full_ip = env.get(f"CUSTOMER_DB_{c}_IP") + f":{grpc_port}"
        ip_port_list.append( full_ip )
        grpc_port += 1
    ret = random.choice( ip_port_list )
    print(ret)
    return ret

@app.route("/create_user", methods=["POST"])
def create_user():

    data = json.loads(request.data)
    name = data["name"]
    username = data["username"]
    password = data["password"]

    print(f"Creating new user {username}")
    while True:
        try:
            channel = grpc.insecure_channel(get_customer_db_ip())
            stub = customer_pb2_grpc.CustomerStub(channel)
            response = stub.CreateUser(customer_pb2.CreateUserRequest(
                name=name,
                username=username,
                password=password
            ))
            if not response.status:
                print("## ERROR ##")
                print(response.error)
            break
        except grpc._channel._InactiveRpcError as grpc_exc:
            print("Server not available, trying a different one")
    return {"status":response.status}

@app.route("/login", methods=["POST"])
def login():
    print("logging in")

    data = json.loads(request.data)
    username = data["username"]
    password = data["password"]

    while True:
        try:
            channel = grpc.insecure_channel(get_customer_db_ip())
            stub = customer_pb2_grpc.CustomerStub(channel)
            response = stub.ChangeLogin(customer_pb2.ChangeLoginRequest(
                username=username,
                password=password,
                logging_in = True
            ))
            if not response.status:
                print("## ERROR ##")
                print(response.error)
            break
        except grpc._channel._InactiveRpcError as grpc_exc:
            print("Server not available, trying a different one")
    return {"status":response.status}

@app.route("/logout", methods=["POST"])
def logout():
    print("logging out")
    data = json.loads(request.data)
    username = data["username"]

    while True:
        try:
            channel = grpc.insecure_channel(get_customer_db_ip())
            stub = customer_pb2_grpc.CustomerStub(channel)
            response = stub.ChangeLogin(customer_pb2.ChangeLoginRequest(
                username=username,
                password="",# Not needed
                logging_in = False
            ))
            if not response.status:
                print("## ERROR ##")
                print(response.error)
            break
        except grpc._channel._InactiveRpcError as grpc_exc:
            print("Server not available, trying a different one")
    return {"status":response.status}

@app.route("/search_items_for_sale", methods=["POST"])
def search_items_for_sale():
    print("Searching items for sale")
    data = json.loads(request.data)
    username = data["username"]

    resp = check_logged_in(username)
    if not resp["status"] or not resp["logged_in"]:
        print("## ERROR ##")
        print("Not logged in")
        return {"status" : False, "items" : []}

    keywords = []
    category = -1 # Won't match any items
    if "keywords" in list(data.keys()):
        keywords = data["keywords"]
    if "category" in list(data.keys()):
        category = data["category"]

    while True:
        try:
            channel = grpc.insecure_channel(get_product_db_ip())
            stub = product_pb2_grpc.ProductStub(channel)
            response = stub.SearchItem(product_pb2.SearchItemRequest(
                keywords = keywords,
                category = category
            ))
            items = []
            break
        except grpc._channel._InactiveRpcError as grpc_exc:
            print("Server not available, trying a different one")
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
    resp = check_logged_in(username)
    if not resp["status"] or not resp["logged_in"]:
        print("## ERROR ##")
        print("Not logged in")
        return {"status" : False}

    item_id = data["item_id"]
    quantity = data["quantity"]

    # Check sufficient quantity
    while True:
        try:
            channel = grpc.insecure_channel(get_product_db_ip())
            stub = product_pb2_grpc.ProductStub(channel)
            response = stub.GetItemByID(product_pb2.GetItemByIDRequest(
                item_id = item_id
            ))
            break
        except grpc._channel._InactiveRpcError as grpc_exc:
            print("Server not available, trying a different one")
    if not response.status:
        print("## ERROR ##")
        print(response.error)
        return {"status" : response.status}
    if quantity > response.items[0].quantity:
        print("## ERROR ##")
        print(f"Insufficient quantity available: {response.items[0].quantity} requested: {quantity}")
        return {"status" : False}
    
    # Add item to shopping cart
    while True:
        try:
            channel = grpc.insecure_channel(get_customer_db_ip())
            stub = customer_pb2_grpc.CustomerStub(channel)
            response = stub.UpdateCart(customer_pb2.UpdateCartRequest(
                username = username,
                add = True,
                key = "shopping_cart",
                item_id = item_id,
                quantity = quantity
            ))
            break
        except grpc._channel._InactiveRpcError as grpc_exc:
            print("Server not available, trying a different one")
    if not response.status:
        print("## ERROR ##")
        print(response.error)
    return {"status" : response.status}

@app.route("/remove_item_shopping_cart", methods=["POST"])
def remove_item_shopping_cart():
    print("Removing items from shopping cart")
    data = json.loads(request.data)
    username = data["username"]
    resp = check_logged_in(username)
    if not resp["status"] or not resp["logged_in"]:
        print("## ERROR ##")
        print("Not logged in")
        return {"status" : False}

    item_id = data["item_id"]
    quantity = data["quantity"]

    while True:
        try:
            channel = grpc.insecure_channel(get_customer_db_ip())
            stub = customer_pb2_grpc.CustomerStub(channel)
            response = stub.UpdateCart(customer_pb2.UpdateCartRequest(
                username = username,
                add = False,
                key = "shopping_cart",
                item_id = item_id,
                quantity = quantity
            ))
            break
        except grpc._channel._InactiveRpcError as grpc_exc:
            print("Server not available, trying a different one")
    if not response.status:
        print("## ERROR ##")
        print(response.error)
    return {"status" : response.status}

@app.route("/clear_shopping_cart", methods=["POST"])
def clear_shopping_cart():
    print("Clearing shopping cart")
    data = json.loads(request.data)
    username = data["username"]
    resp = check_logged_in(username)
    if not resp["status"] or not resp["logged_in"]:
        print("## ERROR ##")
        print("Not logged in")
        return {"status" : False}

    while True:
        try:
            channel = grpc.insecure_channel(get_customer_db_ip())
            stub = customer_pb2_grpc.CustomerStub(channel)
            response = stub.UpdateCart(customer_pb2.UpdateCartRequest(
                username = username,
                add = True,
                key = "shopping_cart_clear",
                item_id = 0,
                quantity = 0
            ))
            break
        except grpc._channel._InactiveRpcError as grpc_exc:
            print("Server not available, trying a different one")
    if not response.status:
        print("## ERROR ##")
        print(response.error)
    return {"status" : response.status}

@app.route("/display_shopping_cart", methods=["POST"])
def display_shopping_cart():
    print("Displaying shopping cart")
    data = json.loads(request.data)
    username = data["username"]
    resp = check_logged_in(username)
    if not resp["status"] or not resp["logged_in"]:
        print("## ERROR ##")
        print("Not logged in")
        return {"status" : False, "items" : []}
    
    # Get item_ids and quantities
    while True:
        try:
            channel = grpc.insecure_channel(get_customer_db_ip())
            stub = customer_pb2_grpc.CustomerStub(channel)
            response = stub.GetShoppingCart(customer_pb2.CheckLoginRequest(
                username = username
            ))
            break
        except grpc._channel._InactiveRpcError as grpc_exc:
            print("Server not available, trying a different one")
    if not response.status:
        print("## ERROR ##")
        print(response.error)
        return {"status" : False, "items" : []}
    print(response.item_ids)
    print(response.quantities)
    # return {"status" : response.status}

    while True:
        try:
            channel = grpc.insecure_channel(get_product_db_ip())
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
            break
        except grpc._channel._InactiveRpcError as grpc_exc:
            print("Server not available, trying a different one")
    return {"status" : True, "items" : items}

def check_logged_in(username):
    while True:
        try:
            channel = grpc.insecure_channel(get_customer_db_ip())
            stub = customer_pb2_grpc.CustomerStub(channel)
            response = stub.CheckLogin(customer_pb2.CheckLoginRequest(
                username = username
            ))
            break
        except grpc._channel._InactiveRpcError as grpc_exc:
            print("Server not available, trying a different one")
    if not response.status:
        print(response.error)
    return {"status" : response.status, "logged_in" : response.logged_in}

@app.route("/leave_feedback", methods=["POST"])
def leave_feedback():
    print("Leaving Feedback")
    data = json.loads(request.data)
    username = data["username"]
    resp = check_logged_in(username)
    if not resp["status"] or not resp["logged_in"]:
        print("## ERROR ##")
        print("Not logged in")
        return {"status" : False}

    item_id = data["item_id"]
    feedback_type = "thumbsup"

    # Check we've purchased this item before
    while True:
        try:
            channel = grpc.insecure_channel(get_customer_db_ip())
            stub = customer_pb2_grpc.CustomerStub(channel)
            response = stub.UpdateCart(customer_pb2.UpdateCartRequest(
                username = username,
                add = True,
                key = "feedback",
                item_id = item_id,
                quantity = 0
            ))
            break
        except grpc._channel._InactiveRpcError as grpc_exc:
            print("Server not available, trying a different one")
    if not response.status:
        print("## ERROR ##")
        print(response.error)
        return {"status" : response.status}
    
    while True:
        try:
            channel = grpc.insecure_channel(get_product_db_ip())
            stub = product_pb2_grpc.ProductStub(channel)
            response = stub.LeaveFeedback(product_pb2.LeaveFeedbackRequest(
                feedback_type = feedback_type,
                item_id = item_id
            ))
            break
        except grpc._channel._InactiveRpcError as grpc_exc:
            print("Server not available, trying a different one")
    if not response.status:
        print("## ERROR ##")
        print(response.error)
    return {"status" : response.status}

@app.route("/get_seller_rating", methods=["POST"])
def get_seller_rating():
    print("Getting Seller Rating")
    data = json.loads(request.data)
    username = data["username"]
    resp = check_logged_in(username)
    if not resp["status"] or not resp["logged_in"]:
        print("## ERROR ##")
        print("Not logged in")
        return {"status" : False, "thumbsup" : -1, "thumbsdown" : -1}
    seller_id = data["seller_id"]

    while True:
        try:
            channel = grpc.insecure_channel(get_product_db_ip())
            stub = product_pb2_grpc.ProductStub(channel)
            response = stub.GetRating(product_pb2.GetRatingRequest(
                seller_id = seller_id
            ))
            break
        except grpc._channel._InactiveRpcError as grpc_exc:
            print("Server not available, trying a different one")
    if not response.status:
        print(response.error)
    return {"status" : response.status, "thumbsup" : response.thumbsup, "thumbsdown" : response.thumbsdown}

@app.route("/get_history", methods=["POST"])
def get_history():
    print("Getting History")
    data = json.loads(request.data)
    username = data["username"]
    resp = check_logged_in(username)
    if not resp["status"] or not resp["logged_in"]:
        print("## ERROR ##")
        print("Not logged in")
        return {"status" : False, "items" : []}

    while True:
        try:
            channel = grpc.insecure_channel(get_customer_db_ip())
            stub = customer_pb2_grpc.CustomerStub(channel)
            response = stub.GetHistory(customer_pb2.CheckLoginRequest(
                username = username
            ))
            break
        except grpc._channel._InactiveRpcError as grpc_exc:
            print("Server not available, trying a different one")
    if not response.status:
        print("## ERROR ##")
        print(response.error)
        return {"status" : False, "items" : []}    
    ids = response.item_ids
    quants = response.quantities
    items = [[ids[i], quants[i]] for i in range(len(ids))]
    return {"status" : True, "items" : items}

if __name__ == "__main__":
    app.run(debug=True, host=FRONT_BUYER_IP, port=5001)