from emarket.seller_front import SellerFront
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("t")
args = parser.parse_args()

import socket
host = socket.gethostbyname(socket.gethostname())

sf = SellerFront(host = host, delay=float(args.t))
sf.run()