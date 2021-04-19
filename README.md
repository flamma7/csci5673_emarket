# csci5673_emarket

### Functionality

RAFT & the atomic broadcast protocol are fully functional. Below are my speed results.


## Replication Cloud Performance (everything functional)
### Seller's Interface
All units in seconds
- Create User : 0.4844369888305664
- Log in : 0.3110849857330322
- Logout : 0.3561718463897705
- Item for sale : 0.5798244476318359
- Price Change : 0.43914246559143066
- Remove item : 0.5061273574829102
- Display Active Items : 0.23522019386291504
- Get Rating : 0.24208998680114746
### Buyer's Interface
- Create user : 0.30600857734680176
- Log in : 0.3050985336303711
- Log out: 0.29507923126220703
- Search Items for sale : 0.1895749568939209
- Add items to shopping cart : 0.16912293434143066
- Remove Items from shopping cart : 0.37454843521118164
- Display shopping cart : 0.24503493309020996
- Clear shopping cart : 0.3949141502380371
- Get Seller Rating : 0.17244601249694824
- Leaving Feedback : 0.1809232234954834
- Getting History : 0.18568634986877441
- Make Purchase (SOAP) : 0.1602797508239746

## Replication Cloud Performance (one buyer and one seller intfc down)
### Seller's Interface
All units in seconds
- Create User : 0.3005199432373047
- Log in : 0.3067500591278076
- Logout : 0.40812182426452637
- Item for sale : 0.5068395137786865 # Only significant increase
- Price Change : 0.5619468688964844
- Remove item : 0.4538993835449219
- Display Active Items : 0.21271800994873047
- Get Rating : 0.26776981353759766
### Buyer's Interface
- Create user : 0.3049941062927246
- Log in : 0.28176283836364746
- Log out: 0.08504462242126465
- Search Items for sale : 0.17226386070251465
- Add items to shopping cart : 0.45393848419189453
- Remove Items from shopping cart : 0.37454843521118164
- Display shopping cart : 0.24503493309020996
- Clear shopping cart : 0.3949141502380371
- Get Seller Rating : 0.17244601249694824
- Leaving Feedback : 0.1809232234954834
- Getting History : 0.18568634986877441
- Make Purchase (SOAP) : 0.1602797508239746

## REST/gRPC/SOAP Cloud Performance
### Seller's Interface
All units in seconds
- Create User : 0.016
- Log in : 0.0074
- Logout : 0.0075
- Item for sale : 0.0095
- Price Change : 0.0102
- Remove item : 0.0103
- Display Active Items : 0.0105
- Get Rating : 0.011
### Buyer's Interface
- Create user : 0.018
- Log in : 0.0095
- Log out: 0.0098
- Search Items for sale : 0.0176
- Add items to shopping cart : 0.019
- Remove Items from shopping cart : 0.013
- Display shopping cart : 0.017
- Clear shopping cart : 0.018
- Get Seller Rating : 0.012
- Leaving Feedback : 0.0195
- Getting History : 0.0126
- Make Purchase (SOAP) : 0.074

## TCP Performance Locally
### Seller's Interface
All units in seconds
- Create User : 0.0011067
- Log in : 0.000868
- Log in : 0.00087
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

We see that local TCP connection in general is 10x faster than the cloud REST/gRPC/SOAP performance.

## Setup
```
source install.bash
```python -m grpc_tools.protoc -I../protos --python_out=. --grpc_python_out=. ../protos/product.proto
