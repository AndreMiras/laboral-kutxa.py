# laboral-kutxa.py

[![Tests](https://github.com/AndreMiras/laboral-kutxa.py/workflows/Tests/badge.svg)](https://github.com/AndreMiras/laboral-kutxa.py/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/AndreMiras/laboral-kutxa.py/badge.svg?branch=main)](https://coveralls.io/github/AndreMiras/laboral-kutxa.py?branch=main)
[![PyPI release](https://github.com/AndreMiras/laboral-kutxa.py/workflows/PyPI%20release/badge.svg)](https://github.com/AndreMiras/laboral-kutxa.py/actions/workflows/pypi-release.yml)
[![PyPI version](https://badge.fury.io/py/laboral-kutxa.svg)](https://badge.fury.io/py/laboral-kutxa)

Unofficial Laboral Kutxa Python library

## Install

```sh
pip install laboral-kutxa
```

## Usage

Reading through the `misProductos` list:

```python
import os
from laboralkutxa.api import login, get_my_products

username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")
login_response = login(username, password)
token = login_response["token"]
products = get_my_products(token)
print(
    [
        {"alias": product["alias"], "grupo": product["grupo"]}
        for product in products["misProductos"]
    ]
)
```

Output:

```python
[
    {'alias': 'CUENTA 0,0', 'grupo': 'cuentasCorrientes'},
    {'alias': 'VISA ELECTRÓN', 'grupo': 'tarjetas'},
    {'alias': 'PRESTAMO', 'grupo': 'prestamos'}
]
```

Accessing the aggregated amounts per account types:

```python
products = get_my_products(token)
current_account = products["_Importes"]["_CuentasCorrientes"]
financing = products["_Importes"]["_Financiacion"]
print({"currentAccount": current_account, "financing": financing})
```

Output:

```python
{
    'currentAccount': {'cantidad': 4440.13, 'moneda': 'EUR'},
    'financing': {'cantidad': 174356.48, 'moneda': 'EUR'}
}
```
