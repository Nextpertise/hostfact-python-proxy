import vcr
import pytest
from fastapi.testclient import TestClient
from hostfact_python_client import hostfact_client
from main import app

ignore_hosts = ['testserver']


class CustomTestClient(TestClient):
    def request(self, *args, **kwargs):
        # Set the X-REAL-IP header for every request
        headers = kwargs.get("headers", {}) or {}
        headers["X-REAL-IP"] = "1.2.3.4"
        kwargs["headers"] = headers
        return super().request(*args, **kwargs)


class HTTPXTransport:
    def __init__(self, status_code: int, client: str = None):
        self.status_code = status_code
        self.client = client

    def request(self, url: str, data: str, headers: dict = None, timeout: int = 30):
        # Use CustomTestClient().post to send the request
        response = client.post(url, data=data, headers=headers, timeout=timeout)

        assert response.status_code == self.status_code
        if self.client:
            assert response.headers["X-CLIENT"] == self.client

        # Return the response
        return response


# Set up the mocked client
client = CustomTestClient(app)


@vcr.use_cassette('tests/vcr_cassettes/test_list_debtors_invalid_api_key.yaml', ignore_hosts=ignore_hosts)
def test_list_debtors_invalid_api_key():
    with pytest.raises(Exception) as exc_info:
        hf_client = hostfact_client.HostFact(url=f"https://testserver/proxy/your-hostfact-server.com", api_key="invalid_api_key", transport=HTTPXTransport(403))
        response = hf_client.debtor.list()
    assert str(exc_info.value) == 'HostFact error: {"detail":"Invalid API key"}'


@vcr.use_cassette('tests/vcr_cassettes/test_list_debtors_invalid_hostname.yaml', ignore_hosts=ignore_hosts)
def test_list_debtors_invalid_hostname():
    with pytest.raises(Exception) as exc_info:
        hf_client = hostfact_client.HostFact(url=f"https://testserver/proxy/invalid-hostfact-server.com", api_key="1234567890", transport=HTTPXTransport(400, 'Client 1'))
        response = hf_client.debtor.list()
    assert str(exc_info.value) == 'HostFact error: {"detail":"Invalid hostname"}'


@vcr.use_cassette('tests/vcr_cassettes/test_list_debtors.yaml', ignore_hosts=ignore_hosts)
def test_list_debtors_client1():
    hf_client = hostfact_client.HostFact(url=f"https://testserver/proxy/your-hostfact-server.com", api_key="1234567890", transport=HTTPXTransport(200, 'Client 1'))
    response = hf_client.debtor.list()
    assert response == {'controller': 'debtor', 'action': 'list', 'status': 'success', 'date': '2023-08-22T08:44:16+02:00', 'totalresults': 206, 'currentresults': 206, 'offset': 0, 'debtors': [{'Identifier': '1', 'DebtorCode': 'DB100', 'CompanyName': 'DB100', 'Sex': 'm', 'Initials': 'D.', 'SurName': 'Code', 'EmailAddress': 'DB100@nextpertise.nl', 'Modified': '2023-01-01\n        20:29:39'}]}


@vcr.use_cassette('tests/vcr_cassettes/test_list_debtors.yaml', ignore_hosts=ignore_hosts)
def test_show_debtor_client1():
    with pytest.raises(Exception) as exc_info:
        hf_client = hostfact_client.HostFact(url=f"https://testserver/proxy/your-hostfact-server.com", api_key="1234567890", transport=HTTPXTransport(403, 'Client 1'))
        response = hf_client.debtor.show(Identifier=1)
    assert str(exc_info.value) == 'HostFact error: {"detail":"debtor show not allowed for this client"}'


@vcr.use_cassette('tests/vcr_cassettes/test_list_debtors.yaml', ignore_hosts=ignore_hosts)
def test_list_debtors_client2():
    hf_client = hostfact_client.HostFact(url=f"https://testserver/proxy/your-hostfact-server.com", api_key="0987654321", transport=HTTPXTransport(200, 'Client 2'))
    response = hf_client.debtor.list()
    assert response == {'controller': 'debtor', 'action': 'list', 'status': 'success', 'date': '2023-08-22T08:44:16+02:00', 'totalresults': 206, 'currentresults': 206, 'offset': 0, 'debtors': [{'Identifier': '1', 'DebtorCode': 'DB100', 'CompanyName': 'DB100', 'Sex': 'm', 'Initials': 'D.', 'SurName': 'Code', 'EmailAddress': 'DB100@nextpertise.nl', 'Modified': '2023-01-01\n        20:29:39'}]}


@vcr.use_cassette('tests/vcr_cassettes/test_list_debtors.yaml', ignore_hosts=ignore_hosts)
def test_list_debtors_client3():
    hf_client = hostfact_client.HostFact(url=f"https://testserver/proxy/your-hostfact-server.com", api_key="5432109876", transport=HTTPXTransport(200, 'Client 3'))
    response = hf_client.debtor.list()
    assert response == {'controller': 'debtor', 'action': 'list', 'status': 'success', 'date': '2023-08-22T08:44:16+02:00', 'totalresults': 206, 'currentresults': 206, 'offset': 0, 'debtors': [{'Identifier': '1', 'DebtorCode': 'DB100', 'CompanyName': 'DB100', 'Sex': 'm', 'Initials': 'D.', 'SurName': 'Code', 'EmailAddress': 'DB100@nextpertise.nl', 'Modified': '2023-01-01\n        20:29:39'}]}


@vcr.use_cassette('tests/vcr_cassettes/test_show_domain_error.yaml', ignore_hosts=ignore_hosts)
def test_show_domains_client3():
    with pytest.raises(Exception) as exc_info:
        hf_client = hostfact_client.HostFact(url=f"https://testserver/proxy/your-hostfact-server.com", api_key="5432109876", transport=HTTPXTransport(500, 'Client 3'))
        response = hf_client.domain.show(searchat="DebtorCode", searchfor="DB100")
    assert str(exc_info.value) == 'HostFact error: {"detail":"HostFact error: [\'Ongeldig kenmerk voor domeinnaam\']"}'


@vcr.use_cassette('tests/vcr_cassettes/test_list_debtors.yaml', ignore_hosts=ignore_hosts)
def test_list_debtors_client4():
    with pytest.raises(Exception) as exc_info:
        hf_client = hostfact_client.HostFact(url=f"https://testserver/proxy/your-hostfact-server.com", api_key="1231231231", transport=HTTPXTransport(403, 'Client 4'))
        response = hf_client.debtor.list()
    assert str(exc_info.value) == 'HostFact error: {"detail":"debtor list not allowed for this client"}'
