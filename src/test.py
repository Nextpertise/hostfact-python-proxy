from hostfact_python_client import hostfact_client

client = hostfact_client.HostFact(url=f"https://hostfact-proxy.nextpertise.nl/proxy/your-hostfact-server.com", api_key="secret")
print(client.domain.list(searchat="DebtorCode", searchfor="DB100"))