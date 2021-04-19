from pysyncobj import *
import threading
import socket
import json
import time
import copy
import sys

class ProductData(SyncObj):

    def __init__(self, my_ip, other_ips):
        print(f"my_ip: {my_ip}")
        print(f"other_ips: {other_ips}")
        super(ProductData, self).__init__(my_ip, other_ips)
        self.my_ip = my_ip
        self.other_ips = other_ips
        self.sellers = []
        self.products = []

    @replicated_sync
    def add_seller(self, name, seller_id, username, password, feedback_thumbsup=0, feedback_thumbsdown=0, num_items_sold=0):
        print("Addinig user")
        s = Seller(name, seller_id, username, password, feedback_thumbsup, feedback_thumbsdown, num_items_sold)
        self.sellers.append(s)

        leader = self._getLeader()
        print(f"leader: {leader}")
        if leader == self.my_ip:
            print("I AM THE LEADER")
        elif self.my_ip == "10.128.0.4:4323":
            print("Killing...")
            sys.exit(0)
            

    @replicated_sync
    def change_login(self, seller_index, logging_in=True):
        print("Changing login")
        self.sellers[seller_index].logged_in = logging_in

    @replicated_sync
    def add_product(self, name, category, item_id, keywords, condition_new, sale_price, seller_id, quantity):
        print("Adding product")
        new_item = Item(
            name=name,
            category=category,
            item_id=item_id,
            keywords=keywords,
            condition_new=condition_new,
            sale_price = sale_price,
            seller_id=seller_id,
            quantity = quantity )
        
        self.products.append( new_item )

    @replicated_sync
    def remove_item(self, item_index, quantity):
        print("Removing Item")
        self.products[item_index].quantity -= quantity
        if self.products[item_index].quantity <= 0:
            print("Deleting item")
            self.products.pop( item_index )

    @replicated_sync
    def change_price(self, item_index, sale_price):
        print("Changing Price")
        self.products[item_index].sale_price = sale_price

    @replicated_sync
    def leave_feedback(self, seller_index, feedback_type):
        print("Leaving Feedback")
        self.sellers[seller_index].feedback[ feedback_type ] += 1

    @replicated_sync
    def make_sale(self, seller_index, quantity):
        print("Making Sale")
        self.sellers[seller_index].num_items_sold += quantity

class CustomerData():

    def __init__(self, addr_map, me):
        self.me = me
        self.local_info = {}
        for key in addr_map:
            self.local_info[key] = {
                "ip" : addr_map[key][0],
                "port" : addr_map[key][1],
                "req_list" : []
            }

        print(self.local_info)
        
        self.buyers = []

        my_ip = self.local_info[self.me]["ip"]
        my_port = self.local_info[self.me]["port"]
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((my_ip, my_port))

        listen_UDP = threading.Thread(target=self.rec_udp)
        listen_UDP.start()

    def get_global_seq(self):
        # if self.last_msg is None:
        #     return 0
        # else:
        #     return self.last_msg["global_seq"]
        global_seq = 0
        for key in self.local_info:
            global_seq += len(self.local_info[key]["req_list"])
        return global_seq

    def make_purchase(self, buyer_ind):
        argdict = {
            "action" : "make_purchase",
            "buyer_ind" : buyer_ind
        }
        msg_id = self.send2group(argdict)
        self.wait4msg(msg_id)
    
    def _make_purchase(self, argdict):
        buyer_ind = argdict["buyer_ind"]
        buyer = self.buyers[buyer_ind]
        self.buyers[buyer_ind].history.extend(buyer.shopping_cart)
        self.buyers[buyer_ind].shopping_cart = []

    def leave_feedback(self, buyer_ind, item_id):
        argdict = {
            "action" : "leave_feedback",
            "buyer_ind" : buyer_ind,
            "item_id" : item_id
        }
        msg_id = self.send2group(argdict)
        self.wait4msg(msg_id)

    def _leave_feedback(self, argdict):
        buyer_ind = argdict["buyer_ind"]
        item_id = argdict["item_id"]
        self.buyers[buyer_ind].items_given_feedback.append(request.item_id)

    def clear_shopping_cart(self, buyer_ind):
        argdict = {
            "action" : "clear_shopping_cart",
            "buyer_ind" : buyer_ind
        }
        msg_id = self.send2group(argdict)
        self.wait4msg(msg_id)

    def _clear_shopping_cart(self, argdict):
        buyer_ind = argdict["buyer_ind"]
        self.buyers[buyer_ind].shopping_cart = []

    def add_to_shopping_cart(self, buyer_ind, item_id, quantity):
        argdict = {
            "action" : "add_to_shopping_cart",
            "buyer_ind" : buyer_ind,
            "item_id" : item_id,
            "quantity": quantity
        }
        msg_id = self.send2group(argdict)
        self.wait4msg(msg_id)

    def _add_to_shopping_cart(self, argdict):
        buyer_ind = argdict["buyer_ind"]
        item_id = argdict["item_id"]
        quantity = argdict["quantity"]

        item_found = False
        for i_item in range(len(self.buyers[buyer_ind].shopping_cart)):
            item = self.buyers[buyer_ind].shopping_cart[i_item]
            if item[0] == item_id:
                item_found = True
                item[1] += quantity

                # Check if should delete item
                if item[1] <= 0:
                    print("Deleting Item quantity 0 or less")
                    self.buyers[buyer_ind].shopping_cart.pop( i_item )
                break
        if not item_found: # Create new item
            if quantity <= 0:
                print("ERROR: Quantity less than 0!")
            else:
                self.buyers[buyer_ind].shopping_cart.append( [item_id, quantity] )

    def change_login(self, buyer_index, logging_in):
        argdict = {
            "action" : "change_login",
            "buyer_index" : buyer_index,
            "logging_in" : logging_in
        }
        msg_id = self.send2group(argdict)
        self.wait4msg(msg_id)

    def _change_login(self, argdict):
        buyer_index = argdict["buyer_index"]
        logging_in = argdict["logging_in"]
        self.buyers[buyer_index].logged_in = logging_in

    def add_buyer(self, name, buyer_id, username, password):
        argdict = {
            "action" : "add_buyer",
            "name" : name,
            "buyer_id" : buyer_id,
            "us" : username,
            "pw" : password
        }

        msg_id = self.send2group(argdict)
        self.wait4msg(msg_id)

    def _add_buyer(self, argdict):
        name = argdict["name"]
        buyer_id = argdict["buyer_id"]
        us = argdict["us"]
        pw = argdict["pw"]
        b = Buyer(name, buyer_id, us, pw)
        self.buyers.append( b )

    def send2group(self, argdict):
        print("[DB] sending Req")
        if "global_rx" in list(argdict.keys()):
            del argdict["global_rx"]

        payload = {
            "type" : "req",
            "sid" : self.me,
            "local_seq" : len(self.local_info[self.me]["req_list"]),
            "argdict" : argdict
        }
        # for _ in range(2):
        for key in self.local_info:
            if key == self.me:
                continue
            addr = (self.local_info[key]["ip"], self.local_info[key]["port"])
            self.sock.sendto(bytes(json.dumps(payload, indent = 4), encoding='utf8'), addr)


        next_global_num = self.get_global_seq() + 1
        payload["global_seq"] = next_global_num
        payload["global_rx"] = False
        
        self.local_info[self.me]["req_list"].append( payload )


        # Check if it's my turn & if so call the correct function
        # next_global_num = self.get_global_seq() + 1
        check_me = next_global_num + self.me

        # Check send out the global seq
        if check_me % len(self.local_info) == 0:
            # payload["global_seq"] = next_global_num
            payload["type"] = "seq"
            del payload["global_rx"]
            self.sendout_global(payload)

            self.local_info[self.me]["req_list"][-1]["global_rx"] = True
            
            # Handle
            self.handle_msg(payload)

        return (payload["sid"], payload["local_seq"])

    def sendout_global(self, payload):
        print("[DB] Sending global seq")
        if "global_rx" in list(payload.keys()):
            del payload["global_rx"]

        payload["type"] = "seq"
        for key in self.local_info:
            if key == self.me:
                continue
            addr = (self.local_info[key]["ip"], self.local_info[key]["port"])
            self.sock.sendto(bytes(json.dumps(payload, indent = 4), encoding='utf8'), addr)

        # self.global_info["seq_list"].append(payload)
        # self.global_info["last_delivered"] = payload["global_seq"]


    def wait4msg(self, msg_id):   
        """ Method we call to determine whether to deliver """
        # print("Waiting on")
        # print(msg_id)

        cnt = 0
        while True:
            cnt += 1
            i_found = -1
            # print(self.global_info["seq_list"])

            if self.local_info[self.me]["req_list"][-1]["global_rx"]:
                return True

            # for i_msg in reversed(range(len(self.global_info["seq_list"]))):
                # msg = self.global_info["seq_list"][i_msg]
                # if msg["sid"] == msg_id[0] and msg["local_seq"] == msg_id[1]:

                    # return True
                    # if len(self.global_info["seq_list"]) > i_msg + 1:
                    #     return True
                    # else:
                    #     break # Keep looping until we can deliver the msg

            time.sleep(0.2)

            # Resend message
            if cnt > 2:
                print("Resending payload")
                # self.global_info["last_delivered"] += 1
                payload = self.local_info[self.me]["req_list"][-1]
                del payload["global_rx"]
                msg_id = self.send2group(payload["argdict"])
                cnt = 0

    def handle_msg(self, payload):
        assert payload["type"] == "seq"
        argdict = payload["argdict"]
        if argdict["action"] == "add_buyer":
            print("Adding buyer")
            self._add_buyer(argdict)
        elif argdict["action"] == "change_login":
            print("Changing Login")
            self._change_login(argdict)
        elif argdict["action"] == "add_to_shopping_cart":
            print("Adding to shopping cart")
            self._add_to_shopping_cart(argdict)
        elif argdict["action"] == "clear_shopping_cart":
            print("Clearing Shopping Cart")
            self._clear_shopping_cart(argdict)
        elif argdict["action"] == "leave_feedback":
            print("Leaving Feedback")
            self._leave_feedback(argdict)
        elif argdict["action"] == "make_purchase":
            print("Making msg_idpurchase")
            self._make_purchase(argdict)
        else:
            raise NotImplementedError(f"Unknown action : {argdict['action']}")

    def rec_udp(self):
        print("Truth")
        while True:
            
            data, addr = self.sock.recvfrom(1024)
            print( f"received message: local: {len(self.local_info[self.me]['req_list'])}, global: {self.get_global_seq()}")
            data = json.loads(data)
            print(data)

            # Determine Request OR Sequence OR Transmit
            if data["type"] == "req":
                data["global_rx"] = False
                data["global_seq"] = self.get_global_seq() + 1

                self.local_info[data["sid"]]["req_list"].append( data )

                # Check if it's my turn to transmit
                
                check_me = data["global_seq"] + self.me
                if check_me % len(self.local_info) == 0:
                    new_data = copy.deepcopy(data)
                    new_data["type"] = "seq"
                    self.sendout_global(new_data)
            
                    # Handle
                    self.handle_msg(new_data)


            elif data["type"] == "seq":
                
                # Check we've already received this request
                assert data["global_seq"] == self.local_info[data["sid"]]["req_list"][-1]["global_seq"]
                self.local_info[data["sid"]]["req_list"][-1]["global_rx"] = True

                self.handle_msg(data)


class Item:
    def __init__(self, name, category, item_id, keywords, condition_new, sale_price, seller_id,quantity=0):
        # keywords is a list of length max 5
        # condition_new is bool
        self.name = name
        self.category = category
        self.item_id = item_id
        if not isinstance(keywords, list):
            self.keywords = [keywords]
        else:
            self.keywords = keywords
        self.condition_new = condition_new
        self.sale_price = sale_price
        self.seller_id = seller_id
        self.quantity = quantity

class Seller:
    def __init__(self, name, seller_id, username, password, feedback_thumbsup=0, feedback_thumbsdown=0, num_items_sold=0):
        self.name = name
        self.seller_id = seller_id
        self.username = username
        self.password = password # production would encrypt
        self.feedback = {"thumbsup" : feedback_thumbsup, "thumbsdown" : feedback_thumbsdown}
        self.num_items_sold = num_items_sold
        self.logged_in = False

class Buyer:
    def __init__(self, name, buyer_id, username, password, num_items_purchased=0):
        self.name = name
        self.buyer_id = buyer_id
        self.username = username
        self.password = password # production would encrypt
        self.num_items_purchased = num_items_purchased
        self.shopping_cart = [] # 2 item list [id, quantity]
        self.history = []
        self.items_given_feedback = []
        self.logged_in = False