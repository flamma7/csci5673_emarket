#!/usr/bin/env python
# Test functionality of sellers side

from emarket.client_seller import ClientSeller
from emarket.emarket import Item

import socket
host = socket.gethostbyname(socket.gethostname())

cs = ClientSeller(None, host=host,delay=0.0001)
csid = cs.create_user("Luke","flamma7", "enterprise")

## TEST LOGIN
# assert cs.login("flamma7", "enterprise")
# assert cs.logout()

## TEST ITEM FOR SALE
i1 = Item("ether", 0, 0, ["crypto", "smart", "blockchain"], True, 1300, csid)
i2 = Item("bitcoin", 0, 1, ["crypto", "blockchain", "standard"], True, 33000, csid)
i3 = Item("dogecoin", 0, 2, ["crypto", "meme", "blockchain", "elon"], False, 0.03, csid)
i4 = Item("cardano", 0, 3, ["crypto", "blockchain", "smart", "nextgen"], True, 0.3, csid)
# status, i1_id = cs.put_item_for_sale(i1, 500) # Not Logged in
# assert not status
assert cs.login("flamma7", "enterprise")
status, i1_id = cs.put_item_for_sale(i1, 500)
assert status
status, i2_id = cs.put_item_for_sale(i2, 100)
assert status
status, i3_id = cs.put_item_for_sale(i3, 300000)
assert status
status, i4_id = cs.put_item_for_sale(i4, 300000)
assert status
assert cs.change_sale_price_item(i3_id, 0.07)
assert cs.remove_item_from_sale(i2_id, 100)
status, items = cs.display_active_seller_items()
assert status
assert len(items) == 3
print(items)
assert cs.logout()
print("############# All Tests Passed #############")

# Create 2nd Seller

# Create 3rd Seller