#!/usr/bin/python
# -*- coding: utf-8 -*-

from typing import Any, Generator, Literal, Tuple
from uuid import uuid4
from time import sleep
from os import makedirs, listdir, rename
from contextlib import contextmanager
from os.path import exists, abspath
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

MAX_WAIT_TIME = 30.0

ImageFormat = Literal["png", "jpeg", "gif", "bmp", "tiff", "svg"]


class WebyAPI:
    _driver: Chrome | None = None
    _wait: WebDriverWait[Chrome] | None = None
    _downloads_dir: str = abspath("downloads")
    _temp_dir: str = abspath("temp")

    def start(self):

        if not exists(self._downloads_dir):
            makedirs(self._downloads_dir)

        if not exists(self._temp_dir):
            makedirs(self._temp_dir)

        chrome_options = ChromeOptions()
        chrome_options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": self._temp_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": False,
                "safebrowsing.disable_download_protection": True,
            },
        )
        self._driver = Chrome(options=chrome_options)

        self._wait = WebDriverWait(self._driver, MAX_WAIT_TIME)

    def stop(self):
        if self.driver is not None:
            self.driver.quit()

    def get_element(self, by: str, value: str) -> WebElement:
        return self.wait.until(
            expected_conditions.presence_of_element_located((by, value))
        )

    def wait_download(
        self,
        suffix: str = ".crdownload",
        timeout: float = MAX_WAIT_TIME,
        step_time: float = 1.0,
        move_file: bool = True,
    ):
        seconds = 0.0

        while seconds < timeout:
            sleep(step_time)
            seconds += step_time

            # in case the file is not yet in temp download, then
            # the download is yet to be started
            if not listdir(self._temp_dir):
                continue

            # in case there's a file with the suffix, then the download
            # is ongoing (need to wait a little bit more)
            if any([filename.endswith(suffix) for filename in listdir(self._temp_dir)]):
                continue

            # if the file should be moved, then move it from
            # the temp download folder to the downloads folder
            if move_file:
                for filename in listdir(self._temp_dir):
                    src = f"{self._temp_dir}/{filename}"
                    dst = f"{self._downloads_dir}/{filename}"
                    rename(src, dst)

            # if we reach this point, then the download is completed
            return

        raise Exception(f"Download not completed after {timeout} seconds")

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
