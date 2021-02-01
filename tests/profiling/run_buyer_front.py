from emarket.buyer_front import BuyerFront

# TODO read from argparse what hostname to use

bf = BuyerFront(delay=0.1)
bf.run()