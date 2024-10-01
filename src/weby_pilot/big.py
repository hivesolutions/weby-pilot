#!/usr/bin/python
# -*- coding: utf-8 -*-

from os import environ

from .base import WebyAPI
from .errors import WebyError


class BigAPI(WebyAPI):
    username: str | None = None
    password: str | None = None
    nif: str | None = None

    def build_login(self):
        if self.username is None:
            self.username = environ.get("BIG_USERNAME", None)
        if self.password is None:
            self.password = environ.get("BIG_PASSWORD", None)
        if self.nif is None:
            self.nif = environ.get("BIG_NIF", None)

        if self.username is None:
            raise WebyError("BIG_USERNAME must be set")
        if self.password is None:
            raise WebyError("BIG_PASSWORD must be set")
        if self.nif is None:
            raise WebyError("BIG_NIF must be set")
