import pytest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

CHROMEDRIVER_PATH = r"chromedriver-win64\chromedriver.exe"
APP_URL = "http://127.0.0.1:8050/"


# Wait for server to be ready

def wait_for_server(url, timeout=15):
    for _ in range(timeout):
        try:
            requests.get(url)
            return True
        except:
            time.sleep(1)
    raise Exception(f"Server at {url} not reachable. Is it running?")


# Pytest fixture for browser

@pytest.fixture(scope="module")
def driver():
    wait_for_server(APP_URL)  # wait until server is ready
    
    service = Service(CHROMEDRIVER_PATH)
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-allow-origins=*")
    
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()


# Tests

def test_header_present(driver):
    driver.get(APP_URL)
    wait = WebDriverWait(driver, 10)
    header = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
    assert header.is_displayed()

def test_visualisation_present(driver):
    driver.get(APP_URL)
    wait = WebDriverWait(driver, 10)
    viz = wait.until(EC.presence_of_element_located((By.ID, "visualisation")))  
    assert viz.is_displayed()

def test_region_picker_present(driver):
    driver.get(APP_URL)
    wait = WebDriverWait(driver, 10)
    region_picker = wait.until(EC.presence_of_element_located((By.ID, "region-picker"))) 
    assert region_picker.is_displayed()
