import pytest
import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# =============================================
#   E2E Test Pipeline — SauceDemo
#   Tests: Login → Add to Cart → Checkout
# =============================================

# 🔧 CONFIG
SLACK_WEBHOOK = "YOUR_SLACK_WEBHOOK_URL"  # paste your Slack webhook here
BASE_URL       = "https://www.saucedemo.com"
USERNAME       = "standard_user"
PASSWORD       = "secret_sauce"

results = []  # stores test results for Slack report

# -----------------------------------------------
# SETUP — runs before every test
# -----------------------------------------------
@pytest.fixture
def driver():
    print("\n🚀 Opening browser...")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    yield driver
    driver.quit()
    print("🛑 Browser closed.")

# -----------------------------------------------
# HELPER — send results to Slack
# -----------------------------------------------
def send_to_slack(message):
    if SLACK_WEBHOOK == "YOUR_SLACK_WEBHOOK_URL":
        print("⚠️  Slack webhook not set — skipping Slack notification")
        return
    payload = {"text": message}
    requests.post(SLACK_WEBHOOK, json=payload)

# -----------------------------------------------
# TEST 1 — Login with valid credentials
# -----------------------------------------------
def test_login(driver):
    print("\n🔐 TEST 1: Login")
    driver.get(BASE_URL)

    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, "user-name")))

    driver.find_element(By.ID, "user-name").send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.ID, "login-button").click()

    wait.until(EC.url_contains("inventory"))
    assert "inventory" in driver.current_url

    print("✅ Login successful!")
    results.append("✅ Test 1 — Login: PASSED")

# -----------------------------------------------
# TEST 2 — Add product to cart
# -----------------------------------------------
def test_add_to_cart(driver):
    print("\n🛒 TEST 2: Add to Cart")
    driver.get(BASE_URL)

    wait = WebDriverWait(driver, 10)
    driver.find_element(By.ID, "user-name").send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.ID, "login-button").click()
    wait.until(EC.url_contains("inventory"))

    # Add first product to cart
    driver.find_element(By.CLASS_NAME, "btn_inventory").click()
    time.sleep(1)

    # Check cart badge shows 1
    cart_count = driver.find_element(By.CLASS_NAME, "shopping_cart_badge").text
    assert cart_count == "1"

    print("✅ Product added to cart!")
    results.append("✅ Test 2 — Add to Cart: PASSED")

# -----------------------------------------------
# TEST 3 — Complete checkout flow
# -----------------------------------------------
def test_checkout(driver):
    print("\n💳 TEST 3: Checkout")
    driver.get(BASE_URL)

    wait = WebDriverWait(driver, 10)

    # Login
    driver.find_element(By.ID, "user-name").send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.ID, "login-button").click()
    wait.until(EC.url_contains("inventory"))

    # Add to cart
    driver.find_element(By.CLASS_NAME, "btn_inventory").click()
    time.sleep(1)

    # Go to cart
    driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    wait.until(EC.url_contains("cart"))

    # Checkout
    driver.find_element(By.ID, "checkout").click()
    wait.until(EC.url_contains("checkout-step-one"))

    # Fill checkout form
    driver.find_element(By.ID, "first-name").send_keys("Sarvnn")
    driver.find_element(By.ID, "last-name").send_keys("Bot")
    driver.find_element(By.ID, "postal-code").send_keys("600001")
    driver.find_element(By.ID, "continue").click()
    wait.until(EC.url_contains("checkout-step-two"))

    # Finish order
    driver.find_element(By.ID, "finish").click()
    wait.until(EC.url_contains("checkout-complete"))

    # Verify confirmation
    confirmation = driver.find_element(By.CLASS_NAME, "complete-header").text
    assert "THANK YOU" in confirmation.upper()

    print("✅ Checkout complete!")
    results.append("✅ Test 3 — Checkout: PASSED")

# -----------------------------------------------
# TEST 4 — Login with wrong password (should fail)
# -----------------------------------------------
def test_invalid_login(driver):
    print("\n❌ TEST 4: Invalid Login")
    driver.get(BASE_URL)

    wait = WebDriverWait(driver, 10)
    driver.find_element(By.ID, "user-name").send_keys("wrong_user")
    driver.find_element(By.ID, "password").send_keys("wrong_pass")
    driver.find_element(By.ID, "login-button").click()

    error = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "error-message-container")))
    assert error.is_displayed()

    print("✅ Error message shown correctly!")
    results.append("✅ Test 4 — Invalid Login: PASSED")

# -----------------------------------------------
# FINAL — Send all results to Slack
# -----------------------------------------------
def pytest_sessionfinish(session, exitstatus):
    if not results:
        return
    message = "🤖 *SauceDemo E2E Test Results*\n" + "\n".join(results)
    message += f"\n\n{'✅ All tests passed!' if exitstatus == 0 else '❌ Some tests failed!'}"
    send_to_slack(message)
    print("\n📨 Results sent to Slack!")
