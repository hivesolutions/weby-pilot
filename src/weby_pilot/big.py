#!/usr/bin/python
# -*- coding: utf-8 -*-

from os.path import environ
from typing import Tuple

from .base import WebyAPI

class BpiAPI(WebyAPI):
    @classmethod
    def build_login(cls) -> Tuple[str, str, str]:
        username = environ.get("BIG_USERNAME", None)
        password = environ.get("BIG_PASSWORD", None)
        nif = environ.get("BIG_NIF", None)
        if username is None:
            raise Exception("BIG_USERNAME must be set")
        if password is None:
            raise Exception("BIG_PASSWORD must be set")
        if nif is None:
            raise Exception("BIG_NIF must be set")

        return username, password, nif
