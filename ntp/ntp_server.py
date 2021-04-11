import socket
import datetime

UDP_IP = "127.0.0.1" # TODO Change to 0.0.0.0 on the cloud.
UDP_PORT = 5005

NTP_START = datetime.datetime(1899, 12, 31,17)

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))
ref_time = datetime.datetime.now() - NTP_START

def to_ntp_time(secs_dec):
    num = 0
    dec_list = []
    for i in range(1,32):
        if secs_dec - 1 / 2**i >= 0:
            dec_list.append(1)
            secs_dec -= 1 / 2**i
            num += 1 << (32-i)
        else:
            dec_list.append(0)
    # print(dec_list)
    return num

while True:

    # Parse packet
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    # Get the RX timestmap
    rx = datetime.datetime.now() - NTP_START
    data = bytearray(data)

    print(addr)
    # print("received message: %s" % data)
    # print(len(data))
    # print(type(data))
    
    # Ref time
    secs = ref_time.total_seconds()
    secs_full = int(secs)
    secs_dec = to_ntp_time(secs - secs_full)
    for i in range(4):
        data[i+16] = secs_full.to_bytes(4, "big")[i]
    for i in range(4):
        data[i+20] = secs_dec.to_bytes(4, "big")[i]

    # Orig time
    orig_time = [data[i] for i in range(40,48)]

    # Version & other metadata
    data[0] = (35).to_bytes(1, "big")[0] # Version 4, Mode 3
    data[1] = (4).to_bytes(1, "big")[0] # Stratum
    data[3] = (233).to_bytes(1, "big")[0] # Precision

    # rx = datetime.datetime(1952, 10, 22) - NTP_START
    rxsecs = rx.total_seconds()
    rxsecs_full = int(rxsecs)
    rxsecs_dec = to_ntp_time(rxsecs - rxsecs_full)
    for i in range(4):
        data[i+32] = rxsecs_full.to_bytes(4, "big")[i]
    for i in range(4):
        data[i+36] = rxsecs_dec.to_bytes(4, "big")[i]

    # Modify the orignal time
    for i in range(8):
        data[i+24] = orig_time[i]

    # Get the TX timestmap
    tx = datetime.datetime.now() - NTP_START
    txsecs = tx.total_seconds()
    txsecs_full = int(txsecs)
    txsecs_dec = to_ntp_time(txsecs - txsecs_full)
    for i in range(4):
        data[i+40] = txsecs_full.to_bytes(4, "big")[i]
    for i in range(4):
        data[i+44] = txsecs_dec.to_bytes(4, "big")[i]

    sock.sendto(bytes(data), addr)