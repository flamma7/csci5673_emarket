# Test functionality of sellers side

from emarket.client_buyer import ClientBuyer


cb = ClientBuyer(None, delay=0.1)
cbid = cb.create_user("Luke","flamma7", "enterprise")

## TEST LOGIN
assert cb.login("flamma7", "enterprise")
# assert cb.logout()

status, items = cb.search_items_for_sale(0, ["meme","elon"])
assert status
print(items)
assert cb.add_item_shopping_cart(1, 500)
assert cb.remove_item_shopping_cart(1, 200)
status, items = cb.display_shopping_cart()
assert status
print(items)
assert cb.clear_shopping_cart()
status, items = cb.display_shopping_cart()
assert status
print(items)
print("############# All Tests Passed #############")