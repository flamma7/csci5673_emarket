from emarket.buyer_front import BuyerFront
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("t")
args = parser.parse_args()

# TODO read from argparse what hostname to use

import socket
host = socket.gethostbyname(socket.gethostname())

bf = BuyerFront(host=host,delay=float(args.t))
bf.run()