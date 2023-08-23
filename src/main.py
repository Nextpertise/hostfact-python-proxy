#!/usr/bin/env python3
from fastapi import FastAPI, Depends, HTTPException, Request, Response, Path, Form
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from hostfact_python_client import hostfact_client
from typing import List, Dict, Any, Annotated
import ipaddress
import yaml
import logging

logger = logging.getLogger("uvicorn")


# Pydantic models and settings
class HostfactInstance(BaseModel):
    hostname: str
    api_key: str


class Subnet(BaseModel):
    subnet: str
    description: str


class Client(BaseModel):
    description: str
    api_key: str
    allow_list: List[Subnet]
    permissions: Dict[str, List[str]]


class Settings(BaseSettings):
    clients: List[Client]
    hostfact_instances: List[HostfactInstance]

    def __init__(self):
        with open("config/settings.yaml", "r") as f:
            yaml_data = yaml.safe_load(f)
        super().__init__(**yaml_data)


settings = Settings()
app = FastAPI()


class RequestBody(BaseModel):
    api_key: str
    data: Dict[str, Any]


def get_client_and_log_request(api_key: Annotated[str, Form()],
                               controller: Annotated[str, Form()],
                               action: Annotated[str, Form()],
                               ):
    client_by_api_key = next((client for client in settings.clients if client.api_key == api_key), None)
    if not client_by_api_key:
        logger.info(f"Controller: {controller}, Action: {action}, API key: {api_key}, Status: Invalid API key")
        raise HTTPException(status_code=403, detail="Invalid API key")
    logger.info(f"Controller: {controller}, Action: {action}, Client: {client_by_api_key.description}")
    return client_by_api_key


def get_api_key_by_hostname(hostname: str):
    api_key_by_hostname = next((instance.api_key
                                for instance in settings.hostfact_instances if instance.hostname == hostname), None)
    if not api_key_by_hostname:
        raise HTTPException(status_code=400, detail="Invalid hostname")
    return api_key_by_hostname


def get_instance_hostnames():
    return [instance.hostname for instance in settings.hostfact_instances]


@app.post("/proxy/{hostname}")
async def proxy(
    request: Request,
    response: Response,
    controller: Annotated[str, Form()],
    action: Annotated[str, Form()],
    client: Client = Depends(get_client_and_log_request),
    hostname: str = Path(...)
):
    form_data = await request.form()
    headers = {"X-CLIENT": client.description}
    response.headers.update(headers)

    if hostname not in get_instance_hostnames():
        raise HTTPException(status_code=400, detail="Invalid hostname", headers=headers)

    # Get IP address from X-REAL-IP header
    ip = request.headers.get("X-REAL-IP")
    if not ip:
        # Get ip from tcp socket
        ip = request.client.host

    # Check IP address
    if not any(ipaddress.ip_address(ip) in ipaddress.ip_network(subnet.subnet) for subnet in client.allow_list):
        raise HTTPException(status_code=403, detail="IP not allowed", headers=headers)

    # Check sub-api permissions
    permission = client.permissions.get('all') and '*' in client.permissions.get('all')
    if not permission:
        permission = client.permissions.get(controller, [])
        if not permission and '*' not in permission and action not in permission:
            raise HTTPException(status_code=403,
                                detail=f"{controller} {action} not allowed for this client",
                                headers=headers)

    # Get upstream API key
    api_key = get_api_key_by_hostname(hostname)

    # Make the actual API call using the HostFact client
    client = hostfact_client.HostFact(url=f"https://{hostname}/Pro/apiv2/api.php", api_key=api_key)
    method = getattr(getattr(client, controller), action)
    request_data = dict(form_data)
    request_data.pop("api_key")
    response_body = method(**request_data)

    return response_body
