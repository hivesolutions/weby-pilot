#!/usr/bin/python
# -*- coding: utf-8 -*-

from os import environ
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .base import WebyAPI


class BpiAPI(WebyAPI):
    @classmethod
    def download_report(cls):
        username = environ.get("BPI_USERNAME", None)
        password = environ.get("BPI_PASSWORD", None)
        if username is None:
            raise Exception("BPI_USERNAME must be set")
        if password is None:
            raise Exception("BPI_PASSWORD must be set")

        instance = cls()
        with instance.driver_ctx():
            instance.login(username, password)

    def login(self, username: str, password: str):
        self.driver.get("https://bpinetempresas.bancobpi.pt/SIGNON/signon.asp")

        close = self.driver.find_element(By.ID, "fechar")
        close.click()
        sleep(1)

        username_e = self.driver.find_element(By.CSS_SELECTOR, '[label="Nome Acesso"]')
        password_e = self.driver.find_element(
            By.CSS_SELECTOR, '[label="Código Secreto"]'
        )
        username_e.send_keys(username)
        password_e.send_keys(password)
        password_e.send_keys(Keys.RETURN)
