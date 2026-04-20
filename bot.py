from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep
import json
import smtplib
import time
import os


# 📦 Products
products = [
    {
        "name": "Fire TV Stick",
        "url": "https://www.amazon.de/dp/B0CQMWQDH4"
    },
    {
        "name": "Echo Dot",
        "url": "https://www.amazon.de/dp/B09B8X9RGM"
    }
]


# 📧 Email sender
def send_email(old_price, new_price, product_name, url):
    msg = f"Subject: Fiyat Degisti!\n\n{product_name}\nEski: {old_price}\nYeni: {new_price}\nSatin Alma Linki:\n\n {url}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login("yunus.aksu.dev@gmail.com", "")
    server.sendmail(
        "yunus.aksu.dev@gmail.com",
        "dev.yunus.aksu@gmail.com",
        msg
    )
    server.quit()


# 🔎 Price extractor
def get_price(product, driver):
    driver.get(product["url"])
    sleep(5)

    try:
        whole = driver.find_element(By.CLASS_NAME, "a-price-whole").text
        fraction = driver.find_element(By.CLASS_NAME, "a-price-fraction").text

        price_text = f"{whole}.{fraction}"

        # Amazon format fix (1.299 -> 1299)
        price_text = price_text.replace(".", "").replace(",", ".")
        return float(price_text)

    except:
        print(f"{product['name']} price not found!")
        return None


# 🚀 Main bot
def run_bot():

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    # ☁️ cloud-safe path
    file_path = "data.json"

    # 📖 load old data (DICT FIX)
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                old_data = json.load(f)

                # 🔥 FIX: if somehow old file is list → reset
                if isinstance(old_data, list):
                    old_data = {}

        except:
            old_data = {}
    else:
        old_data = {}

    new_data = {}

    for product in products:

        price = get_price(product, driver)

        if price is None:
            continue

        name = product["name"]
        old_price = old_data.get(name)
        url = product["url"]
        

        # 🧠 Compare logic
        if old_price is None:
            print(f"{name} first record")

        else:
            old_price = float(old_price)

            if price < old_price:
                print(f"{name} PRICE DROPPED!")
                send_email(old_price, price, name, url)

            elif price > old_price:
                print(f"{name} PRICE INCREASED")

            else:
                print(f"{name} SAME PRICE")

        new_data[name] = price

        sleep(2)

    # 💾 save new data
    with open(file_path, "w") as f:
        json.dump(new_data, f, indent=4)

    driver.quit()


# 🔁 loop
if __name__ == "__main__":
    while True:
        run_bot()
        time.sleep(300)  # 5 minutes recommended
