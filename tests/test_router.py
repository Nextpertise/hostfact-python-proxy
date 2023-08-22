import vcr
from fastapi.testclient import TestClient
from main import app

ignore_hosts = ['testserver']


class CustomTestClient(TestClient):
    def request(self, *args, **kwargs):
        # Set the X-REAL-IP header for every request
        headers = kwargs.get("headers", {}) or {}
        headers["X-REAL-IP"] = "1.2.3.4"
        kwargs["headers"] = headers
        return super().request(*args, **kwargs)


client = CustomTestClient(app)


@vcr.use_cassette('tests/vcr_cassettes/test_list_debtors_invalid_api_key.yaml', ignore_hosts=ignore_hosts)
def test_list_debtors_invalid_api_key():
    response = client.post("/proxy/your-hostfact-server.com", data={
        "api_key": "invalid_api_key",
        "controller": "debtor",
        "action": "list"
    })
    assert response.status_code == 403
    assert response.content == b'{"detail":"Invalid API key"}'


@vcr.use_cassette('tests/vcr_cassettes/test_list_debtors_invalid_hostname.yaml', ignore_hosts=ignore_hosts)
def test_list_debtors_invalid_hostname():
    response = client.post("/proxy/invalid-hostfact-server.com", data={
        "api_key": "1234567890",
        "controller": "debtor",
        "action": "list"
    })
    assert response.status_code == 400
    assert response.content == b'{"detail":"Invalid hostname"}'


@vcr.use_cassette('tests/vcr_cassettes/test_list_debtors.yaml', ignore_hosts=ignore_hosts)
def test_list_debtors_client1():
    response = client.post("/proxy/your-hostfact-server.com", data={
        "api_key": "1234567890",
        "controller": "debtor",
        "action": "list"
    })
    assert response.status_code == 200
    assert response.json() == {'controller': 'debtor', 'action': 'list', 'status': 'success', 'date': '2023-08-22T08:44:16+02:00', 'totalresults': 206, 'currentresults': 206, 'offset': 0, 'debtors': [{'Identifier': '1', 'DebtorCode': 'DB100', 'CompanyName': 'DB100', 'Sex': 'm', 'Initials': 'D.', 'SurName': 'Code', 'EmailAddress': 'DB100@nextpertise.nl', 'Modified': '2023-01-01\n        20:29:39'}]}
    assert response.headers['x-client'] == 'Client 1'


@vcr.use_cassette('tests/vcr_cassettes/test_list_debtors.yaml', ignore_hosts=ignore_hosts)
def test_list_debtors_client2():
    response = client.post("/proxy/your-hostfact-server.com", data={
        "api_key": "0987654321",
        "controller": "debtor",
        "action": "list"
    })
    assert response.status_code == 200
    assert response.json() == {'controller': 'debtor', 'action': 'list', 'status': 'success', 'date': '2023-08-22T08:44:16+02:00', 'totalresults': 206, 'currentresults': 206, 'offset': 0, 'debtors': [{'Identifier': '1', 'DebtorCode': 'DB100', 'CompanyName': 'DB100', 'Sex': 'm', 'Initials': 'D.', 'SurName': 'Code', 'EmailAddress': 'DB100@nextpertise.nl', 'Modified': '2023-01-01\n        20:29:39'}]}
    assert response.headers['x-client'] == 'Client 2'


@vcr.use_cassette('tests/vcr_cassettes/test_list_debtors.yaml', ignore_hosts=ignore_hosts)
def test_list_debtors_client3():
    response = client.post("/proxy/your-hostfact-server.com", data={
        "api_key": "5432109876",
        "controller": "debtor",
        "action": "list"
    })
    assert response.status_code == 200
    assert response.json() == {'controller': 'debtor', 'action': 'list', 'status': 'success', 'date': '2023-08-22T08:44:16+02:00', 'totalresults': 206, 'currentresults': 206, 'offset': 0, 'debtors': [{'Identifier': '1', 'DebtorCode': 'DB100', 'CompanyName': 'DB100', 'Sex': 'm', 'Initials': 'D.', 'SurName': 'Code', 'EmailAddress': 'DB100@nextpertise.nl', 'Modified': '2023-01-01\n        20:29:39'}]}
    assert response.headers['x-client'] == 'Client 3'


@vcr.use_cassette('tests/vcr_cassettes/test_list_debtors.yaml', ignore_hosts=ignore_hosts)
def test_list_debtors_client4():
    response = client.post("/proxy/your-hostfact-server.com", data={
        "api_key": "1231231231",
        "controller": "debtor",
        "action": "list"
    })
    assert response.status_code == 403
    assert response.json() == {"detail": "debtor list not allowed for this client"}
    assert response.headers['x-client'] == 'Client 4'
