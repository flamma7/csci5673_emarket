from emarket.customer_db import CustomerDB
import socket
host = socket.gethostbyname(socket.gethostname())
c = CustomerDB(host=host)
c.run()