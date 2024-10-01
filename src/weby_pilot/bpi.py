#!/usr/bin/python
# -*- coding: utf-8 -*-

from enum import Enum
from os import environ
from os.path import basename
from datetime import datetime
from typing import IO, Literal, Sequence, Tuple, cast
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .base import WebyAPI
from .common import FileType

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
    "Saldos",
    "Lista Saldos",
    "Movimentos",
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

DocumentType = Literal[
    "Todos",
    "Avisos",
    "Factura-Recibo",
    "Facturas",
    "Notas de Crédito",
    "Notas de Débito",
]


class BpiAPI(WebyAPI):

    username: str | None = None

    password: str | None = None

    def __init__(self, username: str | None = None, password: str | None = None):
        super().__init__()

        self.username = username
        self.password = password
        self.build_login()

    def build_login(self):
        if self.username is None:
            self.username = environ.get("BPI_USERNAME", None)
        if self.password is None:
            self.password = environ.get("BPI_PASSWORD", None)

        if self.username is None:
            raise Exception("BPI_USERNAME must be set")
        if self.password is None:
            raise Exception("BPI_PASSWORD must be set")

    def get_balance(self) -> str:
        with self.driver_ctx():
            self.login()
            self.select_section("Consultas")
            self.select_side_menu("Movimentos")
            return self.text_balance()

    def download_invoice(
        self,
        date_range: SelectDateRange = "Último Ano",
        document_type: DocumentType = "Facturas",
        invoice_indexes: Sequence[int] = (0,),
    ) -> Sequence["BpiDocument"]:
        docs: list[BpiDocument] = []
        with self.driver_ctx():
            self.login()
            self.select_section("Consultas")
            self.select_side_menu("Avisos/Faturas/Notas Crédito e Débito")
            self.select_filters(date_range=date_range, document_type=document_type)
            for invoice_index in invoice_indexes:
                self.click_extract(row_index=invoice_index)
                docs.append(
                    BpiDocument(
                        BpiDocumentType.from_section(document_type),
                        basename(self._last_download_path),
                        self._last_download_buffer(),
                        file_type=FileType.PDF,
                        account=self.username,
                        date=datetime.strptime(
                            self._last_download_path[-14:-4], "%Y-%m-%d"
                        ),
                    )
                )
        return docs

    def download_report(
        self,
        section: ReportSections = "Extrato Conta",
        report_indexes: Sequence[int] = (0,),
    ) -> Sequence["BpiDocument"]:
        docs: list[BpiDocument] = []
        with self.driver_ctx():
            self.login()
            self.select_section("Consultas")
            self.select_side_menu(cast(BpiSideSections, section))
            for report_index in report_indexes:
                self.click_extract(row_index=report_index)
                docs.append(
                    BpiDocument(
                        BpiDocumentType.from_section(section),
                        basename(self._last_download_path),
                        self._last_download_buffer(),
                        file_type=FileType.PDF,
                        account=self.username,
                        date=datetime.strptime(
                            self._last_download_path[-14:-4], "%Y-%m-%d"
                        ),
                    )
                )
        return docs

    def download_account_report(
        self, report_indexes: Sequence[int] = (0,)
    ) -> Sequence["BpiDocument"]:
        return self.download_report(
            section="Extrato Conta", report_indexes=report_indexes
        )

    def download_investing_report(
        self, report_indexes: Sequence[int] = (0,)
    ) -> Sequence["BpiDocument"]:
        return self.download_report(
            section="Extrato Investimento", report_indexes=report_indexes
        )

    def download_card_report(self, card_index=0, report_indexes: Sequence[int] = (0,)):
        with self.driver_ctx():
            self.login()
            self.select_section("Consultas")
            self.select_side_menu("Extrato Cartões")
            for report_index in report_indexes:
                self.click_card_account(row_index=card_index)
                self.click_extract(row_index=report_index)

    def login(self, username: str | None = None, password: str | None = None):
        self.driver.get("https://bpinetempresas.bancobpi.pt/SIGNON/signon.asp")

        close = self.driver.find_element(By.ID, "fechar")
        close.click()

        username_e = self.get_element(By.XPATH, "//*[@label='Nome Acesso']")
        password_e = self.get_element(By.XPATH, "//*[@label='Código Secreto']")
        username_e.send_keys(username or self.username or "")
        password_e.send_keys(password or self.password or "")
        password_e.send_keys(Keys.RETURN)

    def text_balance(self) -> str:
        balance = self.get_element(
            By.XPATH, "//div[text()='Saldo Disponível:']/following-sibling::div/span"
        )
        return balance.text

    def select_section(self, section: BpiSections):
        section_e = self.get_element(By.XPATH, f"//a[contains(text(), '{section}')]")
        section_e.click()

    def select_side_menu(self, side_section: BpiSideSections):
        side_section_e = self.get_element(
            By.XPATH, f"//div[contains(text(), '{side_section}')]"
        )
        side_section_e.click()

    def select_filters(self, date_range: SelectDateRange, document_type: DocumentType):
        self.select_item(self.get_elements(By.XPATH, "//select")[2], date_range)
        self.select_item(self.get_elements(By.XPATH, "//select")[3], document_type)

        filter = self.get_element(By.XPATH, "//*[@value='Filtrar']")
        filter.click()

    def click_extract(self, row_index=0, wait_download: bool = True):
        open_extract = self.get_element(
            By.XPATH,
            f"//table[contains(@class, 'TableRecords')]//tr[{row_index + 1}]//a[contains(text(), 'Abrir')]",
        )
        with self.download_ctx(wait_download=wait_download):
            open_extract.click()

    def click_card_account(self, row_index=0, wait_download: bool = True):
        card_account = self.get_element(
            By.XPATH, f"//a[contains(@class, 'Text_NoWrap')][{row_index + 1}]"
        )
        card_account.click()


class BpiDocumentType(Enum):
    ACCOUNT_EXTRACT = 1
    CARD_EXTRACT = 2
    INVESTMENT_EXTRACT = 3
    INVOICE = 4
    UNKNOWN = 100

    @classmethod
    def from_section(cls, section: str) -> "BpiDocumentType":
        if section == "Extrato Conta":
            return BpiDocumentType.ACCOUNT_EXTRACT
        if section == "Extrato Cartões":
            return BpiDocumentType.CARD_EXTRACT
        if section == "Extrato Investimento":
            return BpiDocumentType.INVESTMENT_EXTRACT
        if section == "Avisos/Faturas/Notas Crédito e Débito":
            return BpiDocumentType.INVOICE
        if section == "Faturas":
            return BpiDocumentType.INVOICE
        return BpiDocumentType.UNKNOWN

    def __repr__(self):
        return self.name.lower().replace("_", " ").title()


class BpiDocument:

    type: BpiDocumentType
    name: str
    buffer: IO[bytes]
    file_type: FileType
    account: str | None
    date: datetime | None

    def __init__(
        self,
        type: BpiDocumentType,
        name: str,
        buffer: IO[bytes],
        file_type: FileType,
        account: str | None = None,
        date: datetime | None = None,
    ):
        self.type = type
        self.name = name
        self.buffer = buffer
        self.file_type = file_type
        self.account = account
        self.date = date

    def __repr__(self):
        return f"BpiDocument(type={self.type}, name={self.name}, account={self.account} date={self.date})"

    @property
    def year(self) -> int:
        if self.date is None:
            raise Exception("Date is not set")
        return self.date.year

    @property
    def month_filename(self) -> str:
        if self.date is None:
            raise Exception("Date is not set")
        return f"{self.date.strftime('%m')}.{self.file_type.extension}"
