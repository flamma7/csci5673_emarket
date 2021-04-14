from spyne import Application, rpc, ServiceBase, Iterable, Integer, Unicode

from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

import grpc
import product_pb2
import product_pb2_grpc
import customer_pb2
import customer_pb2_grpc

from os import environ as env
from dotenv import load_dotenv, find_dotenv
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)
else:
    raise FileNotFoundError("Could not locate .env file")

CUSTOMER_DB_IP = env.get("CUSTOMER_DB_IP")
PRODUCT_DB_IP = env.get("PRODUCT_DB_IP")
CREDIT_FRONT_IP = env.get("CREDIT_FRONT_IP")

"""
This is a simple HelloWorld example to show the basics of writing
a webservice using spyne, starting a server, and creating a service
client.
Here's how to call it using suds:
#>>> from suds.client import Client
#>>> c = Client('http://localhost:8000/?wsdl')
#>>> c.service.say_hello('punk', 5)
(stringArray){
   string[] =
      "Hello, punk",
      "Hello, punk",
      "Hello, punk",
      "Hello, punk",
      "Hello, punk",
 }
#>>>
"""

class MakePurchaseService(ServiceBase):

    @rpc(Unicode, Unicode, Integer, Unicode, _returns=Unicode)
    def make_purchase(self, username, name, cc_number, cc_expiration):
        """Docstrings for service methods appear as documentation in the wsdl.
        #     <b>What fun!</b>
        #     @param username
        #     @param name the purchaser
        #     @param cc_number credit card number
        #     @param cc_expiration expiration date of the card
        #     @return confirmed purchase
        #     """
        print("Making Purchase")
        # print(name)
        # print(cc_number)
        # print(cc_expiration)

        # Look up the shopping cart
        # Get item_ids and quantities
        channel = grpc.insecure_channel(f'{CUSTOMER_DB_IP}:50060')
        stub = customer_pb2_grpc.CustomerStub(channel)
        response = stub.GetShoppingCart(customer_pb2.CheckLoginRequest(
            username = username
        ))
        if not response.status:
            print("## ERROR ##")
            print(response.error)
            return u"failure"
        """
        bool status = 1;
        repeated int32 item_ids = 2;
        repeated int32 quantities = 3;
        string error = 4;
        """

        # Make the purchase
        channel = grpc.insecure_channel(f'{PRODUCT_DB_IP}:50051')
        stub = product_pb2_grpc.ProductStub(channel)
        response = stub.MakePurchase(product_pb2.MakePurchaseRequest(
            item_ids = response.item_ids,
            quantities = response.quantities
        ))
        if not response.status:
            print("## ERROR ##")
            print(response.error)
            return u"failure"

        # Indicate to customer DB that we've made the purchase
        channel = grpc.insecure_channel(f'{CUSTOMER_DB_IP}:50060')
        stub = customer_pb2_grpc.CustomerStub(channel)
        response = stub.MakePurchase(customer_pb2.CheckLoginRequest(
            username = username
        ))
        if not response.status:
            print("## ERROR ##")
            print(response.error)

        return u"success"

application = Application([MakePurchaseService], 'purchasing.service',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())

wsgi_application = WsgiApplication(application)


if __name__ == '__main__':
    import logging

    from wsgiref.simple_server import make_server

    # logging.basicConfig(level=logging.DEBUG)
    # logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)

    logging.info(f"listening to http://{CREDIT_FRONT_IP}:8000")
    logging.info(f"wsdl is at: http://{CREDIT_FRONT_IP}:8000/?wsdl")

    server = make_server(CREDIT_FRONT_IP, 8000, wsgi_application)
    server.serve_forever()