# NTP CSCI-5673

All components are functional. My results are in the pdf. Raw data is in times_lan.csv, times_cloud.csv and times_public.csv.

Reminder for myself:
- On Gcloud remember to set up a firewall that allows all UDP traffic
- Change server.py listen to 0.0.0.0

To start the server.
```
python ntp_server.py
```
The client
```
python ntp_client.py
```