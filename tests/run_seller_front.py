from emarket.seller_front import SellerFront
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("t")
args = parser.parse_args()

sf = SellerFront(delay=float(args.t))
sf.run()