import ntplib

from time import ctime

c = ntplib.NTPClient()
# response = c.request("localhost", version=4, port="5005")
response = c.request("pool.ntp.org", version=4)
print(ctime(response.tx_time))
print(ctime(response.ref_time))
print(ctime(response.orig_time))
print(ctime(response.recv_time))
print(ctime(response.dest_time))
print(response.precision)
print(response.stratum)
print(response.version)
