# 🧪 E2E Test Pipeline — SauceDemo

Automated end-to-end test suite built with Selenium + Pytest.

## Tests Covered
- ✅ Login with valid credentials
- ✅ Add product to cart
- ✅ Complete full checkout flow
- ✅ Invalid login error handling

## Tools Used
- Python
- Selenium WebDriver
- Pytest
- pytest-html (test reports)
- Slack Webhook (results notification)

## How to Run
pip install selenium pytest pytest-html webdriver-manager requests
py -m pytest test_saucedemo.py -v --html=report.html

## What I Learned
- Selenium browser automation
- WebDriverWait and expected conditions
- Pytest fixtures and assertions
- HTML test report generation
- End-to-end test flow design
- 
