#!/usr/bin/python
# -*- coding: utf-8 -*-

from .bpi import BpiAPI

print(BpiAPI().download_account_report(report_indexes=range(0, 2)))

# BpiAPI().download_report(section="Extrato Investimento", report_indexes=range(0, 8))

# BpiAPI().download_invoice()

# print(BpiAPI().get_balance())

# BpiAPI().download_card_report(report_indexes=range(0, 8))
