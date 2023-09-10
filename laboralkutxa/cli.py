#!/usr/bin/env python3
import argparse
import os
import pickle
from getpass import getpass
from typing import Tuple

from appdirs import user_cache_dir

from laboralkutxa import api
from laboralkutxa.constants import APPLICATION_NAME, SESSION_CACHE_FILENAME


def prompt_login() -> Tuple[str, str]:
    """Prompts user for credentials and the returns them as a tuple."""
    username = input("username: ")
    password = getpass("password: ")
    return (username, password)


def get_session_cache_path() -> str:
    return os.path.join(
        user_cache_dir(appname=APPLICATION_NAME), SESSION_CACHE_FILENAME
    )


def get_cached_session_info() -> str:
    """Returns session token from cache."""
    session_cache_path = get_session_cache_path()
    with open(session_cache_path, "rb") as f:
        cached_session_info = pickle.load(f)
    token = cached_session_info["token"]
    return token


def cache_session_info(token: str) -> None:
    """Caches the session token to disk."""
    session_cache_path = get_session_cache_path()
    cached_session_info = {
        "token": token,
    }
    os.makedirs(os.path.dirname(session_cache_path), exist_ok=True)
    with open(session_cache_path, "wb") as f:
        pickle.dump(cached_session_info, f)


def login() -> str:
    """Logins and returns session token."""
    username, password = prompt_login()
    login_response = api.login(username, password)
    token = login_response["token"]
    return token


def process_login() -> str:
    """Logins and caches the token."""
    token = login()
    cache_session_info(token)
    return token


def get_session_or_login() -> str:
    """Retrieves session token from cache or prompts login then stores the token."""
    try:
        token = get_cached_session_info()
    except FileNotFoundError:
        token = process_login()
    return token


def print_balance(importes):
    """Prints per "importe" balance if not zero."""
    for account_type, amount_info in importes.items():
        amount = amount_info["cantidad"]
        currency = amount_info["moneda"]
        if amount != 0:
            print(f"{account_type}: {amount} {currency}")


def process_balance():
    token = get_session_or_login()
    products = api.get_my_products(token)
    print_balance(products["_Importes"])


def main():
    parser = argparse.ArgumentParser(description="Laboral Kutxa Command Line Interface")
    parser.add_argument(
        "--login",
        action="store_true",
        help="Logins and store session.",
    )
    parser.add_argument(
        "--balance",
        action="store_true",
        help="Returns non zero account balances",
    )
    args = parser.parse_args()
    if args.login:
        process_login()
    elif args.balance:
        process_balance()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()  # pragma: no cover
