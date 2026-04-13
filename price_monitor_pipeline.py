import time
import sqlite3
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import requests
from TOKENandID import TOKEN,ID

def laptop_check():

    
    conn = sqlite3.connect("price_history.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS price_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product TEXT,
        price INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    
    options = uc.ChromeOptions()

    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    )

    options.add_argument("--headless")

    driver = uc.Chrome(
        options=options,
        version_main=146,
        use_subprocess=True
    )

    try:

        url = "https://www.amazon.in/ASUS-Zenbook-Smartchoice-Graphics-UM3406KA-PP240WS/dp/B0F9YG6D4C/"

        driver.get(url)

        time.sleep(5)

        BOT_TOKEN = TOKEN 
        CHAT_ID = ID

        message = "Price dropped"

        alert_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"

        soup = BeautifulSoup(
            driver.page_source,
            "html.parser"
        )

        price_tag = soup.find(
            "span",
            class_="a-price-whole"
        )

        if price_tag:

            raw_price = price_tag.text.strip()

            clean_price = raw_price.replace(",", "").replace(".", "")

            current_price = int(clean_price)

            print(f"Current price: {current_price}")

            
            cursor.execute("""
            SELECT price FROM price_history
            ORDER BY id DESC LIMIT 1
            """)

            last_entry = cursor.fetchone()

            if last_entry:

                old_price = last_entry[0]

                if current_price < old_price:

                    print("Price dropped! Sending alert...")

                    requests.get(alert_url)

                else:

                    print("No price drop")

            else:

                print("First entry saved")

            # INSERT NEW PRICE INTO DATABASE
            cursor.execute("""
            INSERT INTO price_history(product, price)
            VALUES(?,?)
            """, ("Zenbook", current_price))

            conn.commit()

        else:

            print("Price not found")

    except Exception as e:

        print("Error:", e)

    finally:

        driver.quit()
        conn.close()


laptop_check()
