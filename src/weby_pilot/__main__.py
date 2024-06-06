#!/usr/bin/python
# -*- coding: utf-8 -*-

from .bpi import BpiAPI

BpiAPI.download_report(report_indexes=range(0, 8))
