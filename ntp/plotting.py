import argparse
import datetime
import time
import csv
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid')

NTP_START = datetime.datetime(1899, 12, 31,17)


# Plots by 12:45p
# Read in 1st CSV
# Read in 2nd CSV
# 3rd

# generate 3x2 subplots (first row is delay, 2nd offset)
fig, axs = plt.subplots(2, 3)

delays = []
offsets = []
xs = []
with open('times_lan.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    skip = False
    for row in csv_reader:
        if not skip:
            skip = True
            continue

        t1 = float(row[2])
        t2 = float(row[3])
        t3 = float(row[4])
        t4 = float(row[5])

        d = (t4 - t1) - (t3 - t2)
        o = 0.5* ( (t2 - t1) + (t3 - t4) )        

        offsets.append(o)
        delays.append(d)
        xs.append(int(row[0]))
mindelays = []
minoffsets = []
for i in range(15):
    start_i = i*8
    end_i = (i+1)*8
    min_i = np.argmin(delays[start_i:end_i]) + start_i
    mindelays.append(delays[min_i])
    minoffsets.append(offsets[min_i])
minxs = [x for x in range(15)]

# Delay
axs[0,0].plot(xs, delays, 'o')
axs[0,0].plot(minxs, mindelays, 'o', color="red", label="Minimum")
axs[0,0].legend()
axs[0,0].set_title("LAN Delay")
axs[0,0].set_xlabel("Interval")
axs[0,0].set_ylabel("Delay (s)")

# Offset
axs[1,0].plot(xs, offsets, 'o')
axs[1,0].plot(minxs, minoffsets, 'o', color="red", label="Minimum Delay")
axs[1,0].legend()
axs[1,0].set_title("LAN Offset")
axs[1,0].set_xlabel("Interval")
axs[1,0].set_ylabel("Offset (s)")

########################################################
delays = []
offsets = []
xs = []
with open('times_cloud.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    skip = False
    for row in csv_reader:
        if not skip:
            skip = True
            continue

        t1 = float(row[2])
        t2 = float(row[3])
        t3 = float(row[4])
        t4 = float(row[5])

        d = (t4 - t1) - (t3 - t2)
        o = 0.5* ( (t2 - t1) + (t3 - t4) )        

        offsets.append(o)
        delays.append(d)
        xs.append(int(row[0]))
mindelays = []
minoffsets = []
for i in range(15):
    start_i = i*8
    end_i = (i+1)*8
    min_i = np.argmin(delays[start_i:end_i]) + start_i
    mindelays.append(delays[min_i])
    minoffsets.append(offsets[min_i])
minxs = [x for x in range(15)]

# Delay
axs[0,1].plot(xs, delays, 'o')
axs[0,1].plot(minxs, mindelays, 'o', color="red", label="Minimum")
axs[0,1].legend()
axs[0,1].set_title("Cloud Delay")
axs[0,1].set_xlabel("Interval")
axs[0,1].set_ylabel("Delay (s)")

# Offset
axs[1,1].plot(xs, offsets, 'o')
axs[1,1].plot(minxs, minoffsets, 'o', color="red", label="Minimum Delay")
axs[1,1].legend()
axs[1,1].set_title("Cloud Offset")
axs[1,1].set_xlabel("Interval")
axs[1,1].set_ylabel("Offset (s)")

########################################################

delays = []
offsets = []
xs = []
with open('times_public.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    skip = False
    for row in csv_reader:
        if not skip:
            skip = True
            continue

        t1 = float(row[2])
        t2 = float(row[3])
        t3 = float(row[4])
        t4 = float(row[5])

        d = (t4 - t1) - (t3 - t2)
        o = 0.5* ( (t2 - t1) + (t3 - t4) )        

        offsets.append(o)
        delays.append(d)
        xs.append(int(row[0]))
mindelays = []
minoffsets = []
for i in range(15):
    start_i = i*8
    end_i = (i+1)*8
    min_i = np.argmin(delays[start_i:end_i]) + start_i
    mindelays.append(delays[min_i])
    minoffsets.append(offsets[min_i])
minxs = [x for x in range(15)]

# Delay
axs[0,2].plot(xs, delays, 'o')
axs[0,2].plot(minxs, mindelays, 'o', color="red", label="Minimum")
axs[0,2].legend()
axs[0,2].set_title("Public NTP Delay")
axs[0,2].set_xlabel("Interval")
axs[0,2].set_ylabel("Delay (s)")

# Offset
axs[1,2].plot(xs, offsets, 'o')
axs[1,2].plot(minxs, minoffsets, 'o', color="red", label="Minimum Delay")
axs[1,2].legend()
axs[1,2].set_title("Public NTP Offset")
axs[1,2].set_xlabel("Interval")
axs[1,2].set_ylabel("Offset (s)")

plt.title("NTP Delays and Offsets")
plt.show()