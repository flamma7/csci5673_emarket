import json
import socket
import time
from erequests import FrontRequestEnum, BackRequestEnum
import grpc
import product_pb2
import product_pb2_grpc

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

CURRENT_FRONT_SELLER = env.get("CURRENT_FRONT_SELLER")
FRONT_SELLER_IP = env.get(f"FRONT_SELLER_{CURRENT_FRONT_SELLER}_IP")

def get_product_db_ip():
    # Select a random IP to request
    ip_port_list = []
    grpc_port = 50051
    for c in ALL_PRODUCT_DBS:
        full_ip = env.get(f"PRODUCT_DB_{c}_IP") + f":{grpc_port}"
        ip_port_list.append( full_ip )
        grpc_port += 1

    # print(ip_port_list)
    # print(random.choice( ip_port_list ))
    return random.choice( ip_port_list )

@app.route("/create_user", methods=["GET","POST"])
def create_user():
    data = json.loads(request.data)
    name = data["name"]
    username = data["username"]
    password = data["password"]

    while True:
        try:
            channel = grpc.insecure_channel(get_product_db_ip())
            stub = product_pb2_grpc.ProductStub(channel)
            response = stub.CreateUser(product_pb2.CreateUserRequest(
                name=name,
                username=username,
                password=password
            ))
            break
        except grpc._channel._InactiveRpcError as grpc_exc:
            print("Server not available, trying a different one")
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

    while True:
        try:
            channel = grpc.insecure_channel(get_product_db_ip())
            stub = product_pb2_grpc.ProductStub(channel)
            response = stub.ChangeLogin(product_pb2.ChangeLoginRequest(
                username=username,
                password=password,
                logging_in = True
            ))
            break
        except grpc._channel._InactiveRpcError as grpc_exc:
            print("Server not available, trying a different one")
    if not response.status:
        print("## ERROR ##")
        print(response.error)
    return {"status":response.status}

@app.route("/logout", methods=["POST"])    
def logout():
    print("logging out")
    data = json.loads(request.data)
    username = data["username"]

    while True:
        try:
            channel = grpc.insecure_channel(get_product_db_ip())
            stub = product_pb2_grpc.ProductStub(channel)
            response = stub.ChangeLogin(product_pb2.ChangeLoginRequest(
                username=username,
                password="",# Not needed
                logging_in = False
            ))
            break
        except grpc._channel._InactiveRpcError as grpc_exc:
            print("Server not available, trying a different one")
    if not response.status:
        print("## ERROR ##")
        print(response.error)
    return {"status":response.status}

@app.route("/put_item_for_sale", methods=["POST"])
def put_item_for_sale():
    print("Putting item for sale")
    data = json.loads(request.data)
    username = data["username"]
    resp = check_logged_in(username)
    if not resp["status"] or not resp["logged_in"]:
        print("## ERROR ##")
        print("Not logged in")
        return {"status" : False, "item_id" : -1}

    while True:
        try:
            channel = grpc.insecure_channel(get_product_db_ip())
            stub = product_pb2_grpc.ProductStub(channel)
            response = stub.CreateItem(product_pb2.CreateItemRequest(
                username=username,
                item_name = data["item"]["name"],
                category = data["item"]["category"],
                keywords = data["item"]["keywords"],
                condition_new = data["item"]["condition_new"],
                sale_price = data["item"]["sale_price"],
                quantity = data["quantity"]
            ))
            break
        except grpc._channel._InactiveRpcError as grpc_exc:
            print("Server not available, trying a different one")
    if not response.status:
        print("## ERROR ##")
        print(response.error)
    return {"status" : response.status, "item_id" : response.item_id}

@app.route("/change_sale_price_item", methods=["POST"])
def change_sale_price_item():
    print("Changing Sale Price of Item")
    data = json.loads(request.data)

    username = data["username"]
    resp = check_logged_in(username)
    if not resp["status"] or not resp["logged_in"]:
        print("## ERROR ##")
        print("Not logged in")
        return {"status" : False}

    item_id = data["item_id"]
    sale_price = data["new_price"]
    while True:
        try:
            channel = grpc.insecure_channel(get_product_db_ip())
            stub = product_pb2_grpc.ProductStub(channel)
            response = stub.ChangePrice(product_pb2.ChangePriceRequest(
                username=username,
                item_id = item_id,
                sale_price = sale_price
            ))
            break
        except grpc._channel._InactiveRpcError as grpc_exc:
            print("Server not available, trying a different one")
    if not response.status:
        print("## ERROR ##")
        print(response.error)
    return {"status" : response.status}

@app.route("/remove_item_from_sale", methods=["POST"])
def remove_item_from_sale():
    print("Removing item")
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
            channel = grpc.insecure_channel(get_product_db_ip())
            stub = product_pb2_grpc.ProductStub(channel)
            response = stub.DeleteItem(product_pb2.DeleteItemRequest(
                username=username,
                item_id=item_id,
                quantity=quantity
            ))
            break
        except grpc._channel._InactiveRpcError as grpc_exc:
            print("Server not available, trying a different one")
    if not response.status:
        print("## ERROR ##")
        print(response.error)
    return {"status" : response.status}

@app.route("/display_active_seller_items", methods=["POST"])
def display_active_seller_items():
    print("Displaying Active Items")
    data = json.loads(request.data)

    username = data["username"]
    resp = check_logged_in(username)
    if not resp["status"] or not resp["logged_in"]:
        print("## ERROR ##")
        print("Not logged in")
        return {"status" : False, "items" : []}

    while True:
        try:
            channel = grpc.insecure_channel(get_product_db_ip())
            stub = product_pb2_grpc.ProductStub(channel)
            response = stub.GetAcct(product_pb2.GetAcctRequest(
                username=username
            ))
            break
        except grpc._channel._InactiveRpcError as grpc_exc:
            print("Server not available, trying a different one")
    if not response.status:
        print("## ERROR ##")
        print(response.error)

    while True:
        try:
            channel = grpc.insecure_channel(get_product_db_ip())
            response = stub.GetItem(product_pb2.GetItemRequest(
                seller_id = response.seller_id
            ))
            break
        except grpc._channel._InactiveRpcError as grpc_exc:
            print("Server not available, trying a different one")
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

# @app.route("/check_logged_in")
def check_logged_in(username):
    while True:
        try:
            channel = grpc.insecure_channel(get_product_db_ip())
            stub = product_pb2_grpc.ProductStub(channel)
            response = stub.CheckLogin(product_pb2.CheckLoginRequest(
                username=username,
            ))
            break
        except grpc._channel._InactiveRpcError as grpc_exc:
            print("Server not available, trying a different one")
    if not response.status:
        print(response.error)
    return {"status" : response.status, "logged_in" : response.logged_in}


@app.route("/get_rating", methods=["POST"])
def get_rating():

    print("Getting rating")
    data = json.loads(request.data)

    username = data["username"]
    resp = check_logged_in(username)
    if not resp["status"] or not resp["logged_in"]:
        print("## ERROR ##")
        print("Not logged in")
        return {"status" : False, "thumbsup" : -1, "thumbsdown" : -1}

    while True:
        try:
            channel = grpc.insecure_channel(get_product_db_ip())
            stub = product_pb2_grpc.ProductStub(channel)
            response = stub.GetAcct(product_pb2.GetAcctRequest(
                username=username
            ))
            break
        except grpc._channel._InactiveRpcError as grpc_exc:
            print("Server not available, trying a different one")
    if not response.status:
        print("## ERROR ##")
        print(response.error)
        return {"status" : response.status}
    print("Located seller id")

    while True:
        try:
            channel = grpc.insecure_channel(get_product_db_ip())
            stub = product_pb2_grpc.ProductStub(channel)
            response = stub.GetRating(product_pb2.GetRatingRequest(
                seller_id = response.seller_id
            ))
            break
        except grpc._channel._InactiveRpcError as grpc_exc:
            print("Server not available, trying a different one")
    if not response.status:
        print(response.error)
    return {"status" : response.status, "thumbsup" : response.thumbsup, "thumbsdown" : response.thumbsdown}

if __name__ == "__main__":
    # sf = SellerFront()
    # sf.run()



    app.run(debug=True, host=FRONT_SELLER_IP, port=5000)