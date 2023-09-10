import contextlib
import pickle
import tempfile
from io import StringIO
from unittest import mock

import pytest

from laboralkutxa import cli


def patch_sys_argv(argv):
    return mock.patch("sys.argv", argv)


def patch_cli_process_login(return_value=mock.DEFAULT):
    return mock.patch("laboralkutxa.cli.process_login", return_value=return_value)


def patch_cli_process_balance():
    return mock.patch("laboralkutxa.cli.process_balance")


def patch_argparse_print_help():
    return mock.patch("laboralkutxa.cli.argparse.ArgumentParser.print_help")


def test_prompt_login():
    s_username = mock.sentinel
    s_password = mock.sentinel
    with mock.patch(
        "laboralkutxa.cli.input", return_value=s_username
    ) as m_input, mock.patch(
        "laboralkutxa.cli.getpass", return_value=s_password
    ) as m_getpass:
        username, password = cli.prompt_login()
    assert m_input.call_args_list == [mock.call("username: ")]
    assert m_getpass.call_args_list == [mock.call("password: ")]
    assert username == s_username
    assert password == s_password


def test_get_session_cache_path():
    with mock.patch(
        "laboralkutxa.cli.user_cache_dir", return_value="user_cache_dir"
    ) as m_user_cache_dir:
        session_cache_path = cli.get_session_cache_path()
    assert m_user_cache_dir.call_args_list == [mock.call(appname="laboral-kutxa")]
    assert session_cache_path == "user_cache_dir/session.cache"


def test_get_cached_session_info():
    """Cached session data is pickle.load() from file."""
    cached_session_info = {
        "token": "token",
    }
    read_data = pickle.dumps(cached_session_info)
    with mock.patch("builtins.open", mock.mock_open(read_data=read_data)):
        token = cli.get_cached_session_info()
    assert token == cached_session_info["token"]


def test_get_cached_session_info_file_not_found():
    """FileNotFoundError is not handled silently."""
    with mock.patch("builtins.open", side_effect=FileNotFoundError), pytest.raises(
        FileNotFoundError
    ):
        cli.get_cached_session_info()


def test_cache_session_info():
    token = "token"
    with tempfile.NamedTemporaryFile() as cache_file, mock.patch(
        "laboralkutxa.cli.get_session_cache_path", return_value=cache_file.name
    ):
        cli.cache_session_info(token)
        cached_session_info = cli.get_cached_session_info()
    assert cached_session_info == token


def test_login():
    m_username = mock.Mock()
    m_password = mock.Mock()
    account_info = {"token": "token"}
    with mock.patch(
        "laboralkutxa.cli.prompt_login", return_value=(m_username, m_password)
    ) as m_prompt_login, mock.patch(
        "laboralkutxa.api.login", return_value=account_info
    ) as m_login:
        token = cli.login()
    assert m_prompt_login.call_args_list == [mock.call()]
    assert m_login.call_args_list == [mock.call(m_username, m_password)]
    assert token == account_info["token"]


def test_process_login():
    m_username = mock.Mock()
    m_password = mock.Mock()
    account_info = {"token": "token"}
    with tempfile.NamedTemporaryFile() as cache_file, mock.patch(
        "laboralkutxa.cli.prompt_login", return_value=(m_username, m_password)
    ) as m_prompt_login, mock.patch(
        "laboralkutxa.api.login", return_value=account_info
    ) as m_login, mock.patch(
        "laboralkutxa.cli.get_session_cache_path", return_value=cache_file.name
    ) as m_get_session_cache_path:
        token = cli.process_login()
    assert m_prompt_login.call_args_list == [mock.call()]
    assert m_login.call_args_list == [mock.call(m_username, m_password)]
    assert m_get_session_cache_path.call_args_list == [mock.call()]
    assert token == account_info["token"]


def test_get_session_or_login():
    """The `login()` should be used when session token is not available."""
    m_token = "token"
    with mock.patch(
        "laboralkutxa.cli.get_cached_session_info", side_effect=FileNotFoundError
    ), patch_cli_process_login(return_value=m_token) as m_login:
        token = cli.get_session_or_login()
    assert m_login.call_args_list == [mock.call()]
    assert token == m_token


def test_print_balance():
    importes = {
        "_Bolsa": {"cantidad": 0.0, "moneda": "EUR"},
        "_CuentasCorrientes": {"cantidad": 1234.56, "moneda": "EUR"},
        "_Financiacion": {"cantidad": 123456.78, "moneda": "EUR"},
        "_MisAhorros": {"cantidad": 1234.56, "moneda": "EUR"},
    }
    with mock.patch("sys.stdout", new_callable=StringIO) as m_stdout:
        cli.print_balance(importes)
    assert m_stdout.getvalue() == (
        "_CuentasCorrientes: 1234.56 EUR\n"
        "_Financiacion: 123456.78 EUR\n"
        "_MisAhorros: 1234.56 EUR\n"
    )


def test_process_balance():
    m_token = mock.Mock()
    products = {
        "_Importes": {
            "_Bolsa": {"cantidad": 0.0, "moneda": "EUR"},
            "_CuentasCorrientes": {"cantidad": 1234.56, "moneda": "EUR"},
        }
    }
    with mock.patch(
        "laboralkutxa.cli.get_session_or_login", return_value=m_token
    ) as m_get_session_or_login, mock.patch(
        "laboralkutxa.api.get_my_products", return_value=products
    ) as m_get_my_products, mock.patch(
        "sys.stdout", new_callable=StringIO
    ) as m_stdout:
        cli.process_balance()
    m_get_session_or_login.call_args_list == [mock.call()]
    m_get_my_products.call_args_list == [mock.call(m_token)]
    assert m_stdout.getvalue() == "_CuentasCorrientes: 1234.56 EUR\n"


@pytest.mark.parametrize(
    "argv,process_login_called,process_balance_called,print_help_called",
    [
        (["laboralkutxa/cli.py"], False, False, True),
        (["laboralkutxa/cli.py", "--login"], True, False, False),
        (["laboralkutxa/cli.py", "--balance"], False, True, False),
    ],
)
def test_main(argv, process_login_called, process_balance_called, print_help_called):
    """The help should be printed if no arguments are passed."""
    with contextlib.ExitStack() as patches:
        patches.enter_context(patch_sys_argv(argv))
        m_process_login = patches.enter_context(patch_cli_process_login())
        m_process_balance = patches.enter_context(patch_cli_process_balance())
        m_print_help = patches.enter_context(patch_argparse_print_help())
        cli.main()
    assert m_process_login.called is process_login_called
    assert m_process_balance.called is process_balance_called
    assert m_print_help.called is print_help_called
