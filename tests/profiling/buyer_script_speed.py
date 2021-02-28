# Test functionality of sellers side

from emarket.client_buyer import ClientBuyer
import time

from os import environ as env
from dotenv import load_dotenv, find_dotenv

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)
else:
    raise FileNotFoundError("Could not locate .env file")

#load the env vars
FRONT_BUYER_IP = env.get("FRONT_BUYER_IP")
cb = ClientBuyer(FRONT_BUYER_IP)

print("####################### CREATE USER")
start_time = time.time()
cbid = cb.create_user("Luke","flamma7", "enterprise")
print("--- %s seconds ---" % (time.time() - start_time))

print("####################### LOG IN")
start_time = time.time()
cb.login("flamma7", "enterprise")
print("--- %s seconds ---" % (time.time() - start_time))

print("####################### LOGOUT")
start_time = time.time()
cb.logout()
print("--- %s seconds ---" % (time.time() - start_time))

# Log back in
cb.login("flamma7", "enterprise")

print("####################### SEARCH ITEMS")
start_time = time.time()
cb.search_items_for_sale(keywords=["meme","elon"])
print("--- %s seconds ---" % (time.time() - start_time))

# print(items)
print("####################### ADD ITEMS SHOPPING CART")
start_time = time.time()
cb.add_item_shopping_cart(1, 500)
print("--- %s seconds ---" % (time.time() - start_time))

print("####################### REMOVE ITEMS SHOPPING CART")
start_time = time.time()
cb.remove_item_shopping_cart(1, 200)
print("--- %s seconds ---" % (time.time() - start_time))

print("####################### DISPLAY SHOPPING CART")
start_time = time.time()
cb.display_shopping_cart()
print("--- %s seconds ---" % (time.time() - start_time))

print("####################### CLEAR SHOPPING CART")
start_time = time.time()
cb.clear_shopping_cart()
print("--- %s seconds ---" % (time.time() - start_time))

print("####################### GET SELLER RATING")
start_time = time.time()
cb.get_seller_rating(seller_id = 0)
print("--- %s seconds ---" % (time.time() - start_time))

cb.add_item_shopping_cart(1, 500)
input("Make a purchase...")

print("####################### LEAVE FEEDBACK")
start_time = time.time()
cb.leave_feedback(item_id = 1, thumbsup = True)
print("--- %s seconds ---" % (time.time() - start_time))

print("####################### GET HISTORY")
start_time = time.time()
cb.get_history()
print("--- %s seconds ---" % (time.time() - start_time))
