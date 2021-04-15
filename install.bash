sudo apt install python3-pip
python3 -m pip install grpcio grpcio_tools flask requests spyne lxml suds-py3 pysyncobj
python setup.py install
cd emarket
python -m grpc_tools.protoc -I../protos --python_out=. --grpc_python_out=. ../protos/product.proto
python -m grpc_tools.protoc -I../protos --python_out=. --grpc_python_out=. ../protos/customer.proto
cd ..
