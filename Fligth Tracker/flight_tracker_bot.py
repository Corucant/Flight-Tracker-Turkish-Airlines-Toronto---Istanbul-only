from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# === CONFIGURATION ===
EMAIL_ADDRESS = #"your email address" error is normal 
EMAIL_PASSWORD = #"your third party app password in google account" error is normal
TL_ALERT_THRESHOLD = 47000

# === ChromeDriver Setup ===
#service = Service(r"C:\path\to\chromedriver.exe")  # Update with your path
options = Options()
options.add_argument("--window-size=1920,1080")
# options.add_argument("--headless")  # Uncomment to run without opening browser

driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 30)

def send_email(price):
    subject = f"✈️ Turkish Airlines Alert – {price} TL"
    body = f"""
📅 Date: May 23 – Aug 23
💰 Price: {price} TL
🧳 Baggage: 2 checked + 1 carry-on
📌 Below your threshold: ₺{TL_ALERT_THRESHOLD}

-- Your flight tracker bot ✈️
"""

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_ADDRESS
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

    print("✅ Email sent!")

def check_prices():
    print("🕒 Loading Turkish Airlines homepage...")
    driver.get("https://www.turkishairlines.com/en-int/")
    time.sleep(7)

    # Accept cookies
    try:
        wait.until(EC.element_to_be_clickable((By.ID, "cookiePolicyClose"))).click()
    except:
        pass

    # 🛠 Wait for the booking form before touching inputs
    print("⏳ Waiting for flight search form to load...")
    wait.until(EC.presence_of_element_located((By.XPATH, "//form[contains(@class, 'tk-flightSearch')]")))

    print("✏️ Filling origin (Toronto)...")
    from_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='From']")))
    from_input.clear()
    from_input.send_keys("Toronto")
    time.sleep(2)
    from_input.send_keys(Keys.DOWN)
    from_input.send_keys(Keys.ENTER)

    print("✏️ Filling destination (Istanbul)...")
    to_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='To']")))
    to_input.clear()
    to_input.send_keys("Istanbul")
    time.sleep(2)
    to_input.send_keys(Keys.DOWN)
    to_input.send_keys(Keys.ENTER)

    print("📅 Picking dates...")
    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='departure-date-input']"))).click()
    time.sleep(2)
    driver.find_element(By.CSS_SELECTOR, "button[data-id='2025-05-23']").click()
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, "button[data-id='2025-08-23']").click()
    time.sleep(1)

    print("🔍 Searching flights...")
    search_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Search flights')]")))
    search_button.click()
    time.sleep(20)

    print("💰 Looking for prices...")
    prices = driver.find_elements(By.CLASS_NAME, "price-text")

    if not prices:
        print("❌ No prices found.")
    else:
        for p in prices:
            txt = p.text.replace("TL", "").replace(",", "").strip()
            if txt.isdigit():
                price = int(txt)
                print(f"✅ Found flight: {price} TL")
                if price < TL_ALERT_THRESHOLD:
                    send_email(price)
                    break

    driver.quit()

check_prices()
