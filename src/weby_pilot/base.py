#!/usr/bin/python
# -*- coding: utf-8 -*-

from io import BytesIO
from shutil import rmtree
from typing import IO, Any, Generator, List, Literal
from uuid import uuid4
from time import sleep
from contextlib import contextmanager
from os import makedirs, listdir, rename, remove, environ
from os.path import exists, abspath, isabs
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait, Select

from .errors import WebyError

MAX_WAIT_TIME = 30.0

ImageFormat = Literal["png", "jpeg", "gif", "bmp", "tiff", "svg"]


class WebyOptions:
    headless: bool = False
    stable: bool = True
    window_width: int | None = 1920
    window_height: int | None = 1080

    def __init__(
        self,
        headless: bool = False,
        stable: bool = True,
        window_width: int | None = 1920,
        window_height: int | None = 1080,
    ):
        self.headless = headless
        self.stable = stable
        self.window_width = window_width
        self.window_height = window_height


class WebyAPI:
    _driver: Chrome | None = None
    _wait: WebDriverWait[Chrome] | None = None
    _remove_downloads: bool = False
    _downloads_dir: str = abspath("downloads")
    _temp_dir: str = abspath("temp")
    _last_path: str | None = None

    @classmethod
    def build_options(cls):
        return WebyOptions(headless=bool(environ.get("HEADLESS", False)))

    def start(self, options: WebyOptions = WebyOptions()):
        if not exists(self._downloads_dir):
            makedirs(self._downloads_dir)

        if not exists(self._temp_dir):
            makedirs(self._temp_dir)

        chrome_options = ChromeOptions()
        chrome_options.arguments.append("--enable-unsafe-swiftshader")
        if options.headless:
            chrome_options.arguments.append("--headless=new")
            if options.window_width is not None and options.window_height is not None:
                chrome_options.arguments.append(
                    f"--window-size={options.window_width},{options.window_height}"
                )
        else:
            chrome_options.arguments.append("--start-maximized")
        if options.stable:
            chrome_options.arguments.append("--no-sandbox")
            chrome_options.arguments.append("--disable-dev-shm-usage")
            chrome_options.arguments.append("--disable-gpu")
            chrome_options.arguments.append("--disable-setuid-sandbox")
            chrome_options.arguments.append("--remote-debugging-port=9222")
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
        if options.stable:
            self._driver.delete_all_cookies()

        self._wait = WebDriverWait(self._driver, MAX_WAIT_TIME)

    def stop(self):
        if self.driver is not None:
            self.driver.quit()
        if self._remove_downloads and exists(self._downloads_dir):
            rmtree(self._downloads_dir)

    def redirect(self, url: str):
        self.driver.get(url)

    def switch_to_iframe(self, by: str, value: str):
        element = self.get_element(by, value)
        self.driver.switch_to.frame(element)

    def switch_to_default(self):
        self.driver.switch_to.default_content()

    def get_element(self, by: str, value: str) -> WebElement:
        return self.wait.until(
            expected_conditions.presence_of_element_located((by, value))
        )

    def get_elements(self, by: str, value: str) -> List[WebElement]:
        return self.wait.until(
            expected_conditions.presence_of_all_elements_located((by, value))
        )

    def select_item(
        self,
        element: WebElement,
        text: str,
        force: bool = False,
        timeout: float | None = None,
    ) -> Select:
        select = Select(element)
        selected_text = select.first_selected_option.text
        if not force and selected_text == text:
            return select
        select.select_by_visible_text(text)
        if timeout is not None:
            sleep(timeout)
        return select

    def select_item_index(
        self,
        element: WebElement,
        index: int,
        force: bool = False,
        timeout: float | None = None,
    ) -> Select:
        select = Select(element)
        selected_index = select.options.index(select.first_selected_option)
        if not force and selected_index == index:
            return select
        select.select_by_index(index)
        if timeout is not None:
            sleep(timeout)
        return select

    def wait_download(
        self,
        file_path: str | None = None,
        suffix: str = ".crdownload",
        timeout: float = MAX_WAIT_TIME,
        step_time: float = 1.0,
        move_file: bool = True,
        overwrite: bool = True,
    ) -> str | None:
        seconds = 0.0
        dst: str | None = None

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

            # get the valid names of the files in the temp download folder
            # in case there's none continues the loop (note that hidden files
            # are not considered as valid files)
            valid_names = [
                name for name in listdir(self._temp_dir) if not name.startswith(".")
            ]
            if not valid_names:
                continue

            # obtains the first name as the file name for the source path
            # of the file to be (eventually) "moved"
            filename = valid_names[0]
            src = f"{self._temp_dir}/{filename}"

            # if the file should be moved, then move it from
            # the temp download folder to the downloads folder
            if move_file:
                if filename in listdir(self._downloads_dir):
                    if overwrite:
                        remove(f"{self._downloads_dir}/{filename}")
                    else:
                        raise WebyError(
                            f"File {filename} already exists in downloads folder"
                        )

                dst = f"{self._downloads_dir}/{filename}"

                if file_path is not None:
                    dst = (
                        file_path
                        if isabs(file_path)
                        else f"{self._downloads_dir}/{file_path}"
                    )

                src = abspath(src)
                dst = abspath(dst)

                rename(src, dst)
            else:
                dst = src

            # "saves" the destination file path as the path to the
            # last downloaded file, required for later use
            self._last_path = dst

            # if we reach this point, then the download is completed
            # we can return the destination file path
            return dst

        raise WebyError(f"Download not completed after {timeout} seconds")

    def screenshot(self) -> bytes:
        return self.driver.get_screenshot_as_png()

    def screenshot_file(
        self, name: str | None = None, image_format: ImageFormat = "png"
    ) -> str:
        if name is None:
            name = f"{uuid4()}"

        filename = f"{name}.{image_format}"

        if not self.driver.get_screenshot_as_file(filename):
            raise WebyError(f"Failed to save screenshot to {filename}")

        return filename

    @contextmanager
    def driver_ctx(
        self, options: WebyOptions | None = None, stop=True
    ) -> Generator[Chrome, Any, Any]:
        if options is None:
            options = self.build_options()
        self.start(options=options)
        try:
            yield self.driver
        finally:
            if stop:
                self.stop()

    @contextmanager
    def download_ctx(
        self, wait_download=True, file_path: str | None = None
    ) -> Generator[str, Any, Any]:
        self._cleanup_temp()
        try:
            yield self._downloads_dir
        finally:
            if wait_download:
                self.wait_download(file_path=file_path)

    @property
    def driver(self) -> Chrome:
        if self._driver is None:
            raise WebyError("Driver is not started")
        return self._driver

    @property
    def wait(self) -> WebDriverWait[Chrome]:
        if self._wait is None:
            raise WebyError("Wait is not started")
        return self._wait

    def _cleanup_temp(self):
        for filename in listdir(self._temp_dir):
            remove(f"{self._temp_dir}/{filename}")

    def _last_download(self) -> IO:
        return open(self._last_download_path, "rb")

    def _last_download_buffer(self) -> IO:
        file = self._last_download()
        try:
            content = file.read()
        finally:
            file.close()
        buffer = BytesIO(content)
        buffer.write(content)
        buffer.seek(0)
        return buffer

    @property
    def _last_download_path(self) -> str:
        if self._last_path is None:
            raise WebyError("No file downloaded")
        if not exists(self._last_path):
            raise WebyError(f"File {self._last_download} does not exist")
        return self._last_path
