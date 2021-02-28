from suds.client import Client
import time
from os import environ as env
from dotenv import load_dotenv, find_dotenv
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)
else:
    raise FileNotFoundError("Could not locate .env file")

CREDIT_FRONT_IP = env.get("CREDIT_FRONT_IP")

print("####################### MAKING PURCHASE USING SOAP")
start_time = time.time()
d = Client(f"http://{CREDIT_FRONT_IP}:8000?wsdl")
resp = d.service.make_purchase("flamma7", "Luke", 1238325, "12/22")
print("--- %s seconds ---" % (time.time() - start_time))
