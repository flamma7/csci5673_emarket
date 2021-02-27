import json
import socket
import time
from erequests import FrontRequestEnum, BackRequestEnum
import grpc
import product_pb2
import product_pb2_grpc

from flask import Flask, request
app = Flask(__name__)

@app.route("/create_user", methods=["GET","POST"])
def create_user():
    data = json.loads(request.data)
    name = data["name"]
    username = data["username"]
    password = data["password"]

    channel = grpc.insecure_channel('localhost:50051')
    stub = product_pb2_grpc.ProductStub(channel)
    response = stub.CreateUser(product_pb2.CreateUserRequest(
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

    channel = grpc.insecure_channel('localhost:50051')
    stub = product_pb2_grpc.ProductStub(channel)
    response = stub.ChangeLogin(product_pb2.ChangeLoginRequest(
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

    channel = grpc.insecure_channel('localhost:50051')
    stub = product_pb2_grpc.ProductStub(channel)
    response = stub.ChangeLogin(product_pb2.ChangeLoginRequest(
        username=username,
        password="",# Not needed
        logging_in = False
    ))
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
        return {"status" : False}

    channel = grpc.insecure_channel('localhost:50051')
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
    channel = grpc.insecure_channel('localhost:50051')
    stub = product_pb2_grpc.ProductStub(channel)
    response = stub.UpdateItem(product_pb2.UpdateItemRequest(
        username=username,
        match_fields = ["item_id"],
        value_fields = [str(item_id)],
        new_fields = ["sale_price"],
        new_values = [str(sale_price)]
    ))
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
    channel = grpc.insecure_channel('localhost:50051')
    stub = product_pb2_grpc.ProductStub(channel)
    response = stub.UpdateItem(product_pb2.UpdateItemRequest(
        username=username,
        match_fields = ["item_id"],
        value_fields = [str(item_id)],
        new_fields = ["quantity"],
        new_values = [str(0)]
    ))
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
        return {"status" : False}

    channel = grpc.insecure_channel('localhost:50051')
    stub = product_pb2_grpc.ProductStub(channel)
    response = stub.GetAcct(product_pb2.GetAcctRequest(
        username=username
    ))
    if not response.status:
        print("## ERROR ##")
        print(response.error)

    channel = grpc.insecure_channel('localhost:50051')
    response = stub.GetItem(product_pb2.GetItemRequest(
        seller_id = response.seller_id
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

# @app.route("/check_logged_in")
def check_logged_in(username):
    channel = grpc.insecure_channel('localhost:50051')
    stub = product_pb2_grpc.ProductStub(channel)
    response = stub.CheckLogin(product_pb2.CheckLoginRequest(
        username=username,
    ))
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
        return {"status" : False}

    channel = grpc.insecure_channel('localhost:50051')
    stub = product_pb2_grpc.ProductStub(channel)
    response = stub.GetAcct(product_pb2.GetAcctRequest(
        username=username
    ))
    if not response.status:
        print("## ERROR ##")
        print(response.error)
        return {"status" : response.status}
    print("Located seller id")

    channel = grpc.insecure_channel('localhost:50051')
    stub = product_pb2_grpc.ProductStub(channel)
    response = stub.GetRating(product_pb2.GetRatingRequest(
        seller_id = response.seller_id
    ))
    if not response.status:
        print(response.error)
    return {"status" : response.status, "thumbsup" : response.thumbsup, "thumbsdown" : response.thumbsdown}

if __name__ == "__main__":
    # sf = SellerFront()
    # sf.run()
    app.run(debug=True, port=5000)