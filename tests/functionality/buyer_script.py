#!/usr/bin/env python
# Test functionality of sellers side

from emarket.client_buyer import ClientBuyer

cb = ClientBuyer()
cbid = cb.create_user("Luke","flamma7", "enterprise")

# TEST LOGIN
assert cb.login("flamma7", "enterprise")
assert cb.logout()

status, items = cb.search_items_for_sale(keywords=["meme","elon"])
assert status
assert len(items) == 1

assert cb.add_item_shopping_cart(1, 500)
assert cb.remove_item_shopping_cart(1, 200)
status, items = cb.display_shopping_cart()
assert status
assert len(items) == 1

assert not cb.leave_feedback(item_id = 1, thumbsup = True)
status, rating = cb.get_seller_rating(seller_id = 0)
assert status
assert "thumbsup" in list(rating.keys())
assert "thumbsdown" in list(rating.keys())

status, history = cb.get_history()
assert status
assert not history

# # Make purchase, Check shopping cart, check history
# assert cb.add_item_shopping_cart(3, 9000)
# status, items = cb.display_shopping_cart()
# assert status
# assert items
# status = cb.make_purchase("Luke", 9182408124,"02/23/2021")
# status, items = cb.display_shopping_cart()
# assert status
# assert not items
# status, history = cb.get_history()
# assert status
# assert history

assert cb.clear_shopping_cart()

print("############# All Tests Passed #############")