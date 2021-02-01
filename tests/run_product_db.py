from emarket.product_db import ProductDB
import socket
host = socket.gethostbyname(socket.gethostname())
p = ProductDB(host=host)
p.run()