#!/usr/bin/env python
# coding: utf-8

# # Income Scraper
# **Link:**  `https://www.gotohui.com/life/ldata-3` (city-level)          
# **Coverage:** Annual urban resident per-capita disposable income (城镇居民人均可支配收入) for Shanghai (city-level)
# 
# ---

# In[ ]:


def scrape_shanghai_income_data():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    import time
    import re
    import csv
    from bs4 import BeautifulSoup


    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
    )

    all_data = []
    url = "https://www.gotohui.com/life/ldata-3"

    try:
        driver.get(url)

        print("MANUAL LOGIN REQUIRED")
        input("Press ENTER here to continue scraping...")

        time.sleep(3)

        page_html = driver.page_source
        soup = BeautifulSoup(page_html, 'html.parser')

        all_tables = soup.find_all('table')
        print(f"Found {len(all_tables)} tables on the page")

        if len(all_tables) == 0:
            print("No tables found!")
            return []

        target_table = None
        for table in all_tables:
            table_text = table.get_text()
            if '城镇居民人均可支配收入' in table_text:
                target_table = table
                break

        if target_table is None:
            print("Could not find income table, using first table")
            target_table = all_tables[0]
        rows = target_table.find_all('tr')
        print(f"Found {len(rows)} rows")

        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 2:
                continue

            year_text = cells[0].get_text(strip=True)
            year_match = re.fullmatch(r'(\d{4})', year_text)

            if not year_match:
                continue

            year = int(year_match.group(1))

            if year < 2016 or year > 2025:
                continue

            income_value = None

            income_text = cells[1].get_text(strip=True)

            #in case unable to scrape behind paywall
            if income_text == '查看' or income_text == '':
                if len(cells) > 2:
                    income_text = cells[2].get_text(strip=True)
            if income_text == '查看' or income_text == '':
                if len(cells) > 3:
                    income_text = cells[3].get_text(strip=True)

            income_match = re.search(r'([\d,]+\.?\d*)', income_text)

            if income_match:
                income_value = float(income_match.group(1).replace(',', ''))
                print(f" {year}: {income_value:,.2f} yuan")

                all_data.append({
                    'district': 'Shanghai_Whole_City',
                    'year': year,
                    'urban_disposable_income_per_capita': income_value,
                })
            else:
                print(f"{year}: No data found (showed: '{income_text}')")

        print(f"\nCollected {len(all_data)} years of data")

    except Exception as error:
        print(f"\nERROR: {error}")
        import traceback
        traceback.print_exc()

    finally:
        time.sleep(5)
        driver.quit()

    return all_data
import csv
from pathlib import Path

results = scrape_shanghai_income_data()

if results:
    project_root = Path.cwd().parent
    data_dir = project_root / "data" 
    filename = data_dir / "shanghai_income_final.csv"

    with open(
        'shanghai_income_final.csv',
        'w',
        newline='',
        encoding='utf-8-sig'
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=results[0].keys()
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"\nSaved {len(results)} rows to shanghai_income_final.csv")

    for row in results:
        print(row)

else:
    print("\nNo data was collected.")

print("\nDone!")

