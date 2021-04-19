sudo apt install python3-pip
python3 -m pip install --upgrade pip
python3 -m pip install grpcio grpcio_tools flask requests spyne lxml suds-py3 pysyncobj python-dotenv
# python setup.py install
cd emarket
python3 -m grpc_tools.protoc -I../protos --python_out=. --grpc_python_out=. ../protos/product.proto
python3 -m grpc_tools.protoc -I../protos --python_out=. --grpc_python_out=. ../protos/customer.proto
cd ..
