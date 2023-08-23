# hostfact-python-proxy

How to use:
```
from hostfact_python_client import hostfact_client

client = hostfact_client.HostFact(url=f"https://hostfact-proxy.nextpertise.nl/proxy/your-hostfact-server.com", api_key="secret")
print(client.debtor.list())
```

Exception example, in this case no permission to show debtor:
```
from hostfact_python_client import hostfact_client

client = hostfact_client.HostFact(url=f"https://hostfact-proxy.nextpertise.nl/proxy/your-hostfact-server.com", api_key="secret")
print(client.debtor.show(Identifier=1))

Traceback (most recent call last):
  File "/hostfact-python-proxy/src/./fulltest.py", line 4, in <module>
    print(client.debtor.show(Identifier=1))
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/hostfact_python_client/hostfact_client.py", line 50, in call
    raise Exception(error)
Exception: HostFact error: {"detail":"debtor show not allowed for this client"}
```
