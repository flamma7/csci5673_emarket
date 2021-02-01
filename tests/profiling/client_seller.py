# Test functionality of sellers side

from emarket.client_seller import ClientSeller
from emarket.emarket import Item
import time

cs = ClientSeller(None, delay=0.0001)
print("####################### CREATE USER")
start_time = time.time()
csid = cs.create_user("Luke","flamma7", "enterprise")
print("--- %s seconds ---" % (time.time() - start_time))

## TEST LOGIN
print("####################### LOG IN")
start_time = time.time()
cs.login("flamma7", "enterprise")
print("--- %s seconds ---" % (time.time() - start_time))

## TEST ITEM FOR SALE
print("####################### PUT ITEM FOR SALE")
i1 = Item("ether", 0, 0, ["crypto", "smart", "blockchain"], True, 1300, csid)
i2 = Item("bitcoin", 0, 1, ["crypto", "blockchain", "standard"], True, 33000, csid)
i3 = Item("dogecoin", 0, 2, ["crypto", "meme", "blockchain", "elon"], False, 0.03, csid)
i4 = Item("cardano", 0, 3, ["crypto", "blockchain", "smart", "nextgen"], True, 0.3, csid)
status, i1_id = cs.put_item_for_sale(i1, 500)
status, i2_id = cs.put_item_for_sale(i2, 100)
status, i3_id = cs.put_item_for_sale(i3, 300000)
start_time = time.time()
status, i4_id = cs.put_item_for_sale(i4, 300000)
print("--- %s seconds ---" % (time.time() - start_time))

print("####################### CHANGE SALE PRICE")
start_time = time.time()
cs.change_sale_price_item(i3_id, 0.07)
print("--- %s seconds ---" % (time.time() - start_time))

print("####################### REMOVE ITEM FROM SALE")
start_time = time.time()
cs.remove_item_from_sale(i2_id, 100)
print("--- %s seconds ---" % (time.time() - start_time))

print("####################### DISPLAY ACTIVE ITEMS")
start_time = time.time()
cs.display_active_seller_items()
print("--- %s seconds ---" % (time.time() - start_time))

# Create 2nd Seller

# Create 3rd Seller