sudo apt install python3-pip
sudo pip3 install virtualenv
virtualenv venv
source venv/bin/activate
pip install grpcio grpcio_tools flask requests
python setup.py install
cd emarket
python -m grpc_tools.protoc -I../protos --python_out=. --grpc_python_out=. ../protos/product.proto
python -m grpc_tools.protoc -I../protos --python_out=. --grpc_python_out=. ../protos/customer.proto
cd ..
