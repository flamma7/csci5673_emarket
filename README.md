# csci5673_emarket

My emarket is packaged in the form of a python package that can be installed into a virtual env on the user's system.

My design splits the server side into 4 processes, following the design from class. The ports used were 1131x for x = {1,2,3,4}. 

## Assumptions
The assumptions I made in my design were
1. Communication messages between processes of 2048 bytes max. 
2. The user does not input extremely long character sequences for keywords
3. Usernames and passwords are limited to 12 characters (arbitray, not a python issue)
4. Port numbers are known beforehand and hardcoded

### Currently Functional (All off Assignment One and more)
Functionality is tested in tests/functionality/client_seller.py and tests/functionality/client_buyer.py scripts. These were recorded using the steps in Running/Performance. All of the below operations are operational.
#### Seller's Interface
- Create Account
- Login
- Logout
- Put item for sale
- Change sale price of item
- Remove item from sale
- Display items currently on sale by seller
#### Buyer's Interface
- Create Account
- Login
- Logout
- Search items for sale
- Add item to shopping cart
- Remove item from shopping cart
- Clear shopping cart
- Display shopping cart


## Performance on Same Machine
### Seller's Interface
All units in seconds
- Create User : 0.0011067
- Log in : 0.000868
- Item for sale : 0.00087
- Price Change : 0.00104
- Remove item : 0.000827
- Display Active Items : 0.001415
### Buyer's Interface
- Create user : 0.001157
- Log in : 0.0008790
- Log out: 0.000360
- Search Items for sale : 0.001063
- Add items to shopping cart : 0.0012974
- Remove Items from shopping cart : 0.000891
- Display shopping cart : 0.0014691
- Clear shopping cart : 0.000847

We see the latency for all calls is below 0.002s. The calls involving larger payloads such as displaying the shopping cart and displaying active items that have to send more data are among the highest in latency. **I inserted a delay in the implementation of 0.0001s before socket calls to give the python socket library time to close one connection and start listening for another connection. Although this adds latency, it is almost an order of magnitude smaller than the latencies we see above, so it does not make a substantial difference.** This could be improved in future versions.

## Setup
```
python setup.py install
```

## Running
### Functionality
In 4 separate terminals start the server processes
```
cd tests
python run_product_db.py
python run_customer_db.py
python run_buyer_front.py
python run_seller_front.py
```
or equivalently
```
bash run_servers.bash
pkill python
```
Run the pkill command at end of testing to kill the background processes from this script.

Then populate the database and test the seller interface
```
cd functionality/
python client_seller.py
```
Then run the buyer interface
```
python client_buyer.py
```

### Performance
```
cd tests
bash run_servers.bash
cd profiling
python client_seller.py
python client_buyer.py
```
Kill the background processes with
```
pkill python
```