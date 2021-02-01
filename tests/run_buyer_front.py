from emarket.buyer_front import BuyerFront
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("t")
args = parser.parse_args()

# TODO read from argparse what hostname to use

bf = BuyerFront(delay=float(args.t))
bf.run()