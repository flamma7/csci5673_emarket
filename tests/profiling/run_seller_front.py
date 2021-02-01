from emarket.seller_front import SellerFront

# TODO read from argparse what hostname to use

sf = SellerFront(delay=0.1)
sf.run()