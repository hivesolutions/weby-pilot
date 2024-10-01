#!/usr/bin/python
# -*- coding: utf-8 -*-

from .bpi import BpiAPI

print(BpiAPI().download_account_report(report_indexes=range(0, 2)))
