# csci5673_emarket

My emarket is packaged in the form of a python package that can be installed into a virtual env on the user's system.

My design splits the server side into 4 processes, following the design from class. The ports used were 1131x for x = {1,2,3,4}. 

### Currently Functional (All off Assignment One and more)
Functionality is tested in tests/client_seller.py and tests/client_buyer.py
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


## Performance

## Assumptions
The assumptions I made in my design were
1. Communication messages between processes of 2048 bytes max. 
2. Usernames and passwords 12 characters max
3. I generally did not check size of numbers and names since python handles memory management

## Setup
```
python setup.py install
```

## Running
In 4 separate terminals start the server processes
```
cd tests/functionality
python run_product_db.py
python run_customer_db.py
python run_buyer_front.py
python run_seller_front.py
```
Then populate the database
```
python client_seller.py
```
Then run the buyer interface
```
python client_buyer.py
```

## Performance
```
cd tests/profiling
bash run_servers.bash
python client_seller.py
python client_buyer.py
```
Kill the background processes with
```
pkill python
```