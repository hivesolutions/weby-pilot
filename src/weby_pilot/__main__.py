#!/usr/bin/python
# -*- coding: utf-8 -*-

from .bpi import BpiAPI

app = BpiAPI()

print(app.download_invoice(invoice_indexes=range(0, 2)))
print(app.download_account_report(report_indexes=range(0, 2)))
