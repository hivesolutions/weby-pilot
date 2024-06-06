#!/usr/bin/python
# -*- coding: utf-8 -*-

from typing import Any, Generator, Literal
from uuid import uuid4
from os import makedirs
from contextlib import contextmanager
from os.path import exists, abspath
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait

ImageFormat = Literal["png", "jpeg", "gif", "bmp", "tiff", "svg"]


class WebyAPI:
    _driver: Chrome | None = None

    def start(self):
        download_dir = abspath("downloads")

        if not exists(download_dir):
            makedirs(download_dir)

        chrome_options = ChromeOptions()
        chrome_options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": False,
                "safebrowsing.disable_download_protection": True,
            },
        )
        self._driver = Chrome(options=chrome_options)

        self._wait = WebDriverWait(self._driver, 10)

    def stop(self):
        if self.driver is not None:
            self.driver.quit()

    def screenshot(self) -> bytes:
        return self.driver.get_screenshot_as_png()

    def screenshot_file(
        self, name: str | None = None, format: ImageFormat = "png"
    ) -> str:
        if name is None:
            name = f"{uuid4()}"

        filename = f"{name}.{format}"

        if not self.driver.get_screenshot_as_file(filename):
            raise Exception(f"Failed to save screenshot to {filename}")

        return filename

    @contextmanager
    def driver_ctx(self, stop=True) -> Generator[Chrome, Any, Any]:
        self.start()
        try:
            yield self.driver
        finally:
            if stop:
                self.stop()

    @property
    def driver(self) -> Chrome:
        if self._driver is None:
            raise Exception("Driver is not started")
        return self._driver

    @property
    def wait(self) -> WebDriverWait[Chrome]:
        if self._wait is None:
            raise Exception("Wait is not started")
        return self._wait
