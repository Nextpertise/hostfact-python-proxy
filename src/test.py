from urllib.error import HTTPError

from hostfact_python_client import hostfact_client


def test_list_debtors():
    api_key = "1234567890"
    api_url = "http://127.0.0.1:8000/proxy/cptest1.nextpertise.nl"

    try:
        client = hostfact_client.HostFact(url=api_url, api_key=api_key)
        debtors = client.debtor.list(Status=0)
        print(debtors)
    except HTTPError as e:
        print(e)


if __name__ == "__main__":
    test_list_debtors()
