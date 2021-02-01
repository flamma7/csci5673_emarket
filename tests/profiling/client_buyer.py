# Test functionality of sellers side

from emarket.client_buyer import ClientBuyer
import time

cb = ClientBuyer(None, delay=0.0001)

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
cb.search_items_for_sale(0, ["meme","elon"])
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
