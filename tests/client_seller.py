# Test functionality of sellers side

from emarket.client_seller import ClientSeller
from emarket.emarket import Item


cs = ClientSeller(None)
csid = cs.create_user("flamma7", "enterprise")
assert cs.login("flamma7", "enterprise")
assert cs.logout("flamma7")
















# i1 = Item("ether", 0, 0, ["crypto", "smart", "blockchain"], True, 1300, csid)
# i2 = Item("bitcoin", 0, 1, ["crypto", "blockchain", "standard"], True, 33000, csid)
# i3 = Item("dogecoin", 0, 2, ["crypto", "meme", "blockchain", "elon"], False, 0.03, csid)
# i1_id = cs.put_item_for_sale(i1, 500)
# i2_id = cs.put_item_for_sale(i2, 100)
# i3_id = cs.put_item_for_sale(i3, 300000)
# assert i3_id == 2

# assert cs.change_sale_price_item(i2_id, 0.07)
# assert cs.remove_item_from_sale(i2_id, 150000)
# assert cs.display_active_seller_items() == ["Items"]

# Create 2nd Seller

# Create 3rd Seller