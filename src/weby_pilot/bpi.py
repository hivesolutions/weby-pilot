#!/usr/bin/python
# -*- coding: utf-8 -*-

from os import environ
from typing import Literal, Sequence, Tuple, cast
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
    "Avisos/Faturas/Notas Crédito e Débito",
    "Avaliação da Adequação de Prod. Investimento",
    "Extrato Conta",
    "Extrato Cartões",
]

ReportSections = Literal["Extrato Conta", "Extrato Investimento"]

SelectDateRange = Literal[
    "Últimos 3 dias",
    "Última Semana",
    "Último Mês",
    "Últimos 3 Meses",
    "Último Ano",
    "Intervalo de Datas",
]


class BpiAPI(WebyAPI):
    @classmethod
    def build_login(cls) -> Tuple[str, str]:
        username = environ.get("BPI_USERNAME", None)
        password = environ.get("BPI_PASSWORD", None)
        if username is None:
            raise Exception("BPI_USERNAME must be set")
        if password is None:
            raise Exception("BPI_PASSWORD must be set")

        return username, password

    @classmethod
    def download_invoice(cls, range: SelectDateRange = "Último Ano"):
        instance = cls()
        with instance.driver_ctx(options=cls.build_options()):
            instance.login(*cls.build_login())
            instance.select_section("Consultas")
            instance.select_side_menu("Avisos/Faturas/Notas Crédito e Débito")
            instance.select_item(instance.get_elements(By.XPATH, "//select")[2], range)

    @classmethod
    def download_report(
        cls,
        section: ReportSections = "Extrato Conta",
        report_indexes: Sequence[int] = (0,),
    ):
        instance = cls()
        with instance.driver_ctx(options=cls.build_options()):
            instance.login(*cls.build_login())
            instance.select_section("Consultas")
            instance.select_side_menu(cast(BpiSideSections, section))
            for report_index in report_indexes:
                instance.click_extract(row_index=report_index)

    @classmethod
    def download_investing_report(cls, report_indexes: Sequence[int] = (0,)):
        return cls.download_report(
            section="Extrato Investimento", report_indexes=report_indexes
        )

    @classmethod
    def download_card_report(cls, card_index=0, report_indexes: Sequence[int] = (0,)):
        instance = cls()
        with instance.driver_ctx(options=cls.build_options()):
            instance.login(*cls.build_login())
            instance.select_section("Consultas")
            instance.select_side_menu("Extrato Cartões")
            for report_index in report_indexes:
                instance.click_card_account(row_index=card_index)
                instance.click_extract(row_index=report_index)

    def login(self, username: str, password: str):
        self.driver.get("https://bpinetempresas.bancobpi.pt/SIGNON/signon.asp")

        close = self.driver.find_element(By.ID, "fechar")
        close.click()

        username_e = self.get_element(By.XPATH, '//*[@label="Nome Acesso"]')
        password_e = self.get_element(By.XPATH, '//*[@label="Código Secreto"]')
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

    def click_extract(self, row_index=0, wait_download: bool = True):
        open_extract = self.get_element(
            By.XPATH,
            f'//table[contains(@class, "TableRecords")]//tr[{row_index + 1}]//a[contains(text(), "Abrir")]',
        )
        with self.download_ctx(wait_download=wait_download):
            open_extract.click()

    def click_card_account(self, row_index=0, wait_download: bool = True):
        card_account = self.get_element(
            By.XPATH, f'//a[contains(@class, "Text_NoWrap")][{row_index + 1}]'
        )
        card_account.click()
