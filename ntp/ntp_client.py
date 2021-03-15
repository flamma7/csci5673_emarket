import socket
import datetime
import time
import csv
import argparse

NTP_START = datetime.datetime(1899, 12, 31,17)


parser = argparse.ArgumentParser()
parser.add_argument("test_type")
args = parser.parse_args()
test_type = args.test_type

"""
Add timeout (& resend)
Start recording local, cloud, 


Select smallest delay and offset

Add support for UDP timeout if pkg failure
"""

def from_npt_time(number):
    secs_dec = 0
    for i in range(1,32):
        if number & (1 << (32-i)):
            secs_dec += 1 / 2**i
    return secs_dec

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

# Create socket for server
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# s.settimeout(2)
# ip = "localhost"
ip = "pool.ntp.org"
# port = 5005
port = 123

with open(f"times_{test_type}.csv", mode="w") as times_file:
    writer = csv.writer(times_file, delimiter=",")
    writer.writerow(["Seq", "Subseq", "T1", "T2", "T3", "T4"])

for i in range(15): # Loop for 1 hour

    j = 0
    while j < 8:
        ## Create NTP packet ##
        data = bytearray((0).to_bytes(48, "big"))
        # Version
        data[0] = (35).to_bytes(1, "big")[0] # Version 4, Mode 3

        # Get the TX timestmap
        tx = datetime.datetime.now() - NTP_START
        txsecs = tx.total_seconds()
        # print(txsecs)
        txsecs_full = int(txsecs)
        txsecs_dec = to_ntp_time(txsecs - txsecs_full)
        # print(txsecs - txsecs_full)
        # print(from_npt_time(txsecs_dec))    
        for k in range(4):
            data[k+40] = txsecs_full.to_bytes(4, "big")[k]
        for k in range(4):
            data[k+44] = txsecs_dec.to_bytes(4, "big")[k]

        s.sendto(bytes(data), (ip, port))

        # Receive response
        try:
            data, address = s.recvfrom(1024)
            rx = datetime.datetime.now() - NTP_START
            print("received response")
        except socket.timeout as exc:
            print("missed a UDP packet...")
            time.sleep(1)
            continue # Try again

        # Origin Timestamp (T1)
        integer = int.from_bytes(bytes(data[24:28]), byteorder="big")
        frac = int.from_bytes(bytes(data[28:32]), byteorder="big")
        frac_secs = from_npt_time(frac)
        t1 = integer + frac_secs

        # Receive Timestamp (T2)
        integer = int.from_bytes(bytes(data[32:36]), byteorder="big")
        frac = int.from_bytes(bytes(data[36:40]), byteorder="big")
        frac_secs = from_npt_time(frac)
        t2 = integer + frac_secs

        # Transmit Timestamp (T3)
        integer = int.from_bytes(bytes(data[40:44]), byteorder="big")
        frac = int.from_bytes(bytes(data[44:48]), byteorder="big")
        frac_secs = from_npt_time(frac)
        t3 = integer + frac_secs

        # T4 
        t4 = rx.total_seconds()
        
        with open(f"times_{test_type}.csv", mode="a") as times_file:
            writer = csv.writer(times_file, delimiter=",")
            writer.writerow([i,j,t1,t2,t3,t4])

        j += 1
        time.sleep(2)
        
    time.sleep(60*4) # Sleep 4 minutes
    print("---")
# print(int.from_bytes(bytes(data[0]), byteorder="big"))

# Choose the smallest delay

s.close()