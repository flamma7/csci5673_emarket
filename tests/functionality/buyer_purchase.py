from suds.client import Client
d = Client("http://localhost:8000?wsdl")
resp = d.service.make_purchase("flamma7", "Luke", 1238325, "12/22")
print(resp)