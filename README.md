# csci5673_emarket

### Functionality

RAFT & the atomic broadcast protocol are fully functional. Below are my latency results.


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

## Replication Cloud Performance (one buyer and one seller intfc down)
### Seller's Interface
All units in seconds
- Create User : 0.3005199432373047
- Log in : 0.3067500591278076
- Logout : 0.40812182426452637
- Item for sale : 0.5068395137786865 # Only significant
- Price Change : 0.5619468688964844
- Remove item : 0.4538993835449219
- Display Active Items : 0.21271800994873047
- Get Rating : 0.26776981353759766
### Buyer's Interface
- Create user : 0.42895078659057617
- Log in : 0.30741000175476074
- Log out: 0.3064401149749756
- Search Items for sale : 0.19083952903747559
- Add items to shopping cart : 0.5404839515686035
- Remove Items from shopping cart : 0.4094107151031494
- Display shopping cart : 0.23997282981872559
- Clear shopping cart : 0.5790493488311768
- Get Seller Rating : 0.1516437530517578
- Leaving Feedback : 0.16728973388671875
- Getting History : 0.16681623458862305
- Make Purchase (SOAP) : 0.5336377620697021

## Replication Cloud Performance (one non-master RAFT server down)
### Seller's Interface
All units in seconds
- Create User : 0.4225766658782959
- Log in : 0.3801612854003906
- Logout : 0.40778112411499023
- Item for sale : 0.5073819160461426
- Price Change : 0.5802431106567383
- Remove item : 0.41078853607177734
- Display Active Items : 0.2649383544921875
- Get Rating : 0.24284052848815918
### Buyer's Interface
- Create user : 0.2954897880554199
- Log in : 0.36654233932495117
- Log out: 0.08941316604614258
- Search Items for sale : 0.23473024368286133
- Add items to shopping cart : 0.29722094535827637
- Remove Items from shopping cart : 0.8272976875305176
- Display shopping cart : 0.16821002960205078
- Clear shopping cart : 0.08876419067382812
- Get Seller Rating : 0.18932318687438965
- Leaving Feedback : 0.17329692840576172
- Getting History : 0.15850424766540527
- Make Purchase (SOAP) : 0.1819620132446289

## Replication Cloud Performance (master RAFT server down)
### Seller's Interface
All units in seconds
- Create User : 0.4225881099700928
- Log in : 0.4504218101501465
- Logout : 0.40595531463623047
- Item for sale : 0.5092527866363525
- Price Change : 0.6073486804962158
- Remove item : 0.4317967891693115
- Display Active Items : 0.2144489288330078
- Get Rating : 0.2984282970428467
### Buyer's Interface
- Create user : 0.3277778625488281
- Log in : 0.40932703018188477
- Log out: 0.40986180305480957
- Search Items for sale : 0.24393200874328613
- Add items to shopping cart : 0.46654582023620605
- Remove Items from shopping cart : 0.37590599060058594
- Display shopping cart : 0.387221097946167
- Clear shopping cart : 0.2041318416595459
- Get Seller Rating : 0.2043929100036621
- Leaving Feedback : 0.26787590980529785
- Getting History : 0.2055034637451172
- Make Purchase (SOAP) : 0.6381411552429199

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
