#!/usr/bin/env python
# Test functionality of sellers side
import sys
from suds.client import Client
from emarket.client_buyer import ClientBuyer
from emarket.emarket import Item
import time
from os import environ as env
from dotenv import load_dotenv, find_dotenv

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)
else:
    raise FileNotFoundError("Could not locate .env file")

#load the env vars
FRONT_BUYER_A_IP = env.get("FRONT_BUYER_A_IP")
FRONT_BUYER_B_IP = env.get("FRONT_BUYER_B_IP")
CREDIT_FRONT_IP = env.get("CREDIT_FRONT_IP")

cb = ClientBuyer([FRONT_BUYER_A_IP, FRONT_BUYER_B_IP])

###########################
options = {
    "create" : ["Create a user", ["name", "username", "password"]],
    "login" : ["Login a user",["username","password"]],
    "logout" : ["Logout a user",[]],
    "search" : ["Search item for sale",["keywords"]],
    "add" : ["Add item to shopping cart", ["item_id", "quantity"]],
    "remove" : ["Remove item from shopping cart",["item_id","quantity"]],
    "display" : ["Display shopping cart", []],
    "leave" : ["Leave Feedback",["item_id", "thumbsup"]],
    "rating" : ["Get seller rating", ["seller_id"]],
    "history" : ["Get buyer history", []],
    "make" : ["Make purchase of shopping cart", []],
    "help" : ["Print help screen",[]]
}

print("Enter name")
name = input()
print("Enter username")
username = input()
print("Enter password")
password = input()
cb.create_user(name, username, password)

while True:

    args = []

    print("\n***********\n")
    print("Enter a command or 'help' to print the commands")
    cmd = input()

    if cmd == "help":
        for key in options:
            print(f"{key} : {options[key][0]}")
    else:
        # Grab args
        try:
            for key in options[cmd][1]:
                if key == "username":
                    args.append(username)
                elif key == "password":
                    args.append(password)
                elif key == "keywords":
                    keywords = []
                    while True:
                        print("new keyword")
                        keywrd = input()
                        if keywrd == "":
                            break
                        else:
                            keywords.append( keywrd )
                    args.append(keywords)
                elif key == "":
                    args.append(None)
                else:
                    print(f"--> {key}")
                    args.append(input())
        except Exception as exc:
            continue
        
        if cmd == "create":
            cb.create_user(*args)
        elif cmd == "login":
            status = cb.login(*args)
            print(f"status: {status}")
        elif cmd == "logout":
            cb.logout()
        elif cmd == "search":
            status, items = cb.search_items_for_sale(keywords=args[0])
            print(f"status: {status}")
            for i in items:
                print(i)
        elif cmd == "add":
            status = cb.add_item_shopping_cart(int(args[0]), int(args[1]))
            print(f"status: {status}")
        elif cmd == "remove":
            status = cb.remove_item_shopping_cart(int(args[0]), int(args[1]))
            print(f"status: {status}")
        elif cmd == "display":
            status, items = cb.display_shopping_cart()
            print(f"status: {status}")
            for i in items:
                print(i)
        elif cmd == "leave":
            status = cb.leave_feedback(int(args[0]), thumbsup=bool(args[1]))
            print(f"status: {status}")
        elif cmd == "rating":
            status, rating = cb.get_seller_rating(int(args[0]))
            print(f"status: {status}")
            print(rating)
        elif cmd == "make":
            d = Client(f"http://{CREDIT_FRONT_IP}:8000?wsdl")
            resp = d.service.make_purchase(username, name, 1238325, "12/22")
            print(resp)
        elif cmd == "history":
            status, history = cb.get_history()
            print(f"status: {status}")
            print(history)