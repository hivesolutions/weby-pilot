#!/usr/bin/python
# -*- coding: utf-8 -*-

from enum import Enum


class FileType(Enum):
    PDF = "application/pdf"
    CSV = "text/csv"
    TXT = "text/plain"

    @property
    def extension(self) -> str:
        return self.name.lower()
