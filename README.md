# csci5673_emarket

### Functionality

The RAFT database replication is fully functional. The atomic broadcast protocol is functional for the create_user() and login() functionality, but is not yet functional in other areas. Occasionally during my testing I had to insert delays to give RAFT time to sync.


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
