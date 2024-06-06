#!/usr/bin/python
# -*- coding: utf-8 -*-

from os import environ
from typing import Literal
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .base import WebyAPI

BpiSections = Literal[
    "Consultas",
    "Operações",
    "Ficheiros",
    "Internacional",
    "Financiamento",
    "Factoring e Confirming",
    "Cartões",
    "TPA",
    "Investimento",
    "Autorizações",
]

BpiSideSections = Literal[
    "Posição Integrada",
    "Posição Integrada Global",
    "Extrato Conta",
    "Extrato Cartões",
]


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
            instance.select_section("Consultas")
            instance.select_side_menu("Extrato Conta")
            instance.click_extract()

    def login(self, username: str, password: str):
        self.driver.get("https://bpinetempresas.bancobpi.pt/SIGNON/signon.asp")

        close = self.driver.find_element(By.ID, "fechar")
        close.click()

        username_e = self.get_element(By.CSS_SELECTOR, '[label="Nome Acesso"]')
        password_e = self.get_element(By.CSS_SELECTOR, '[label="Código Secreto"]')
        username_e.send_keys(username)
        password_e.send_keys(password)
        password_e.send_keys(Keys.RETURN)

    def select_section(self, section: BpiSections):
        section_e = self.get_element(By.XPATH, f'//a[contains(text(), "{section}")]')
        section_e.click()

    def select_side_menu(self, side_section: BpiSideSections):
        side_section_e = self.get_element(
            By.XPATH, f'//div[contains(text(), "{side_section}")]'
        )
        side_section_e.click()

    def click_extract(self, wait_download: bool = True):
        open_extract = self.get_element(By.XPATH, '//a[contains(text(), "Abrir")]')
        open_extract.click()
        if wait_download:
            self.wait_download()
