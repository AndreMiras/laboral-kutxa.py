import json
import os
from typing import Any, Dict

import requests

from laboralkutxa.constants import API_URL


def handle_status_code(response: requests.Response) -> None:
    if response.ok is True:
        return
    raise Exception(
        f"HTTP error! Status: {response.status_code}. Body: {response.text}"
    )


def login(username: str, password: str) -> Dict[str, Any]:
    resource = f"{API_URL}/App/api/Logon"
    body = {
        "primeravez": False,
        "dispositivo": {"sistemaOperativo": "Android", "tipoDispositivo": "Movil"},
        "versionApp": "7.2.6",
        "usuario": username,
        "pwd": password,
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    response = requests.post(resource, headers=headers, data=json.dumps(body))
    handle_status_code(response)
    data = response.json()
    return data


def get_my_products(token: str) -> Dict[str, Any]:
    resource = f"{API_URL}/srv/api/mis-productos"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "cookie": f"lkId={token}",
    }
    response = requests.get(resource, headers=headers)
    handle_status_code(response)
    data = response.json()
    return data


def show_product(product: Dict[str, Any]) -> None:
    print({"productAlias": product["alias"]})


def show_products(products_response: Dict[str, Any]) -> None:
    for product in products_response["misProductos"]:
        show_product(product)


def main() -> None:
    assert (USERNAME := os.environ.get("USERNAME"))
    assert (PASSWORD := os.environ.get("PASSWORD"))
    login_response = login(USERNAME, PASSWORD)
    token = login_response["token"]
    products = get_my_products(token)
    show_products(products)
    current_account = products["_Importes"]["_CuentasCorrientes"]
    financing = products["_Importes"]["_Financiacion"]
    print({"currentAccount": current_account, "financing": financing})


if __name__ == "__main__":
    main()
