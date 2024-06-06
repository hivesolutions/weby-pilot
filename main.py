from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

import os
import time

BPI_USERNAME = os.environ.get("BPI_USERNAME")
BPI_PASSWORD = os.environ.get("BPI_PASSWORD")


chrome_options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": False,
    "safebrowsing.disable_download_protection": True,
}
chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=chrome_options)

try:
    wait = WebDriverWait(driver, 10)

    driver.get("https://bpinetempresas.bancobpi.pt/SIGNON/signon.asp")

    close = driver.find_element(By.ID, "fechar")
    close.click()
    time.sleep(1)

    username = driver.find_element(By.CSS_SELECTOR, '[label="Nome Acesso"]')
    password = driver.find_element(By.CSS_SELECTOR, '[label="Código Secreto"]')
    username.send_keys(BPI_USERNAME)
    password.send_keys(BPI_PASSWORD)
    password.send_keys(Keys.RETURN)

    time.sleep(5)

    checks = wait.until(
        expected_conditions.presence_of_element_located(
            (By.XPATH, '//a[contains(text(), "Consultas")]')
        )
    )
    checks.click()
    time.sleep(2)

    account_extracts = wait.until(
        expected_conditions.presence_of_element_located(
            (By.XPATH, '//div[contains(text(), "Extrato Conta")]')
        )
    )
    account_extracts.click()
    time.sleep(2)

    open_extract = wait.until(
        expected_conditions.presence_of_element_located(
            (By.XPATH, '//a[contains(text(), "Abrir")]')
        )
    )
    open_extract.click()

    time.sleep(30)

    screenshot_path = "screenshot.png"
    driver.get_screenshot_as_file(screenshot_path)
    print(f"Screenshot saved to {screenshot_path}")

finally:
    driver.quit()
