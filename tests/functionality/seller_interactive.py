#!/usr/bin/env python
# Test functionality of sellers side
import sys
from emarket.client_seller import ClientSeller
from emarket.emarket import Item
import time
from os import environ as env
from dotenv import load_dotenv, find_dotenv

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)
else:
    raise FileNotFoundError("Could not locate .env file")

DELAY = 0.0

#load the env vars
FRONT_SELLER_A_IP = env.get("FRONT_SELLER_A_IP")
FRONT_SELLER_B_IP = env.get("FRONT_SELLER_B_IP")

cs = ClientSeller([FRONT_SELLER_A_IP, FRONT_SELLER_B_IP])

###########################
options = {
    "create" : ["Create a user", ["name", "username", "password"]],
    "login" : ["Login a user",["username","password"]],
    "logout" : ["Logout a user",[]],
    "put" : ["Put an item for sale",["name","category","","keywords","","price","","quantity"]],
    "change" : ["Change sale price", ["item_id", "new_price"]],
    "remove" : ["Remove item from sale",["item_id","quantity"]],
    "display" : ["Display active seller items", []],
    "rating" : ["Get rating",[]],
    "help" : ["Print help screen",[]]
}

print("Enter name")
name = input()
print("Enter username")
username = input()
print("Enter password")
password = input()
cs.create_user(name, username, password)

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
                elif key == "":
                    args.append(None)
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
                else:
                    print(f"--> {key}")
                    args.append(input())
        except Exception as exc:
            continue
        
        if cmd == "create":
            cs.create_user(*args)
        elif cmd == "login":
            status = cs.login(*args)
            print(f"status: {status}")
        elif cmd == "logout":
            cs.logout()
        elif cmd == "put":
            quantity = int(args[-1])
            args.pop(-1)
            i = Item(*args)
            status, item_id = cs.put_item_for_sale(i, quantity)
            print(f"status: {status}")
            print(f"item_id: {item_id}")
        elif cmd == "change":
            status = cs.change_sale_price_item(int(args[0]),int(args[1]))
            print(f"status: {status}")
        elif cmd == "remove":
            status = cs.remove_item_from_sale(int(args[0]),int(args[1]))
            print(f"status: {status}")
        elif cmd == "display":
            status, items = cs.display_active_seller_items()
            print(f"status: {status}")
            for i in items:
                print(i)
        elif cmd == "rating":
            status, thumbsup, thumbsdown = cs.get_rating()
            print(f"status: {status}")
            print(f"thumbs up: {thumbsup}, thumbs down: {thumbsdown}")