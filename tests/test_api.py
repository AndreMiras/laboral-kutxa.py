from unittest import mock

import pytest

from laboralkutxa import api


def patch_request_method(method, ok=True, json_response=None):
    mock_response = mock.Mock()
    mock_response.ok = ok
    mock_response.json.return_value = json_response
    mock_post = mock.Mock(return_value=mock_response)
    return mock.patch(f"requests.{method}", mock_post)


def patch_request_get(ok=True, json_response=None):
    return patch_request_method("get", ok, json_response)


def patch_request_post(ok=True, json_response=None):
    return patch_request_method("post", ok, json_response)


def test_handle_status_code():
    # happy case
    response_mock = mock.Mock()
    response_mock.ok = True
    assert api.handle_status_code(response_mock) is None
    # rainy case
    response_mock.ok = False
    response_mock.status_code = 404
    response_mock.text = "Not Found"
    with pytest.raises(Exception, match="HTTP error! Status: 404. Body: Not Found"):
        api.handle_status_code(response_mock)


def test_login():
    username = "username"
    password = "password"
    expected_response = {"token": "test_token"}
    with patch_request_post(json_response=expected_response):
        result = api.login(username, password)
    assert result == expected_response
    with patch_request_post(ok=False), pytest.raises(Exception, match="HTTP error!"):
        api.login(username, password)


def test_get_my_products():
    token = "token"
    expected_response = {"misProductos": []}
    with patch_request_get(json_response=expected_response):
        result = api.get_my_products(token)
    assert result == expected_response
    with patch_request_get(ok=False), pytest.raises(Exception, match="HTTP error!"):
        api.get_my_products(token)


def test_show_product(capsys):
    api.show_product({"alias": "test_product"})
    captured = capsys.readouterr()
    assert captured.out == "{'productAlias': 'test_product'}\n"


def test_show_products(capsys):
    products_response = {"misProductos": [{"alias": "product1"}, {"alias": "product2"}]}
    api.show_products(products_response)
    captured = capsys.readouterr()
    assert (
        captured.out == "{'productAlias': 'product1'}\n{'productAlias': 'product2'}\n"
    )


def test_main(capsys):
    username = "username"
    password = "password"
    token = "token"
    login_response = {"token": token}
    get_my_products_response = {
        "_Importes": {"_CuentasCorrientes": 1000, "_Financiacion": 2000},
        "misProductos": [{"alias": "product1"}, {"alias": "product2"}],
    }
    with mock.patch.dict(
        "os.environ", {"USERNAME": username, "PASSWORD": password}
    ), mock.patch.object(
        api, "login", return_value=login_response
    ) as mock_login, mock.patch.object(
        api, "get_my_products", return_value=get_my_products_response
    ) as mock_get_my_products:
        api.main()
    assert mock_login.call_args_list == [mock.call(username, password)]
    assert mock_get_my_products.call_args_list == [mock.call(token)]
    captured = capsys.readouterr()
    expected_output = (
        "{'productAlias': 'product1'}\n"
        "{'productAlias': 'product2'}\n"
        "{'currentAccount': 1000, 'financing': 2000}\n"
    )
    assert captured.out == expected_output
